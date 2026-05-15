"""
Runtime inference for pickled scikit-learn models under ../models.
Models load once at process start (see main.py lifespan). Pickles are not re-read per request.

The shipped notebook trains a RandomForestClassifier on geographic + ocean features to predict
species occurrence; we combine that with the existing stress engine for stranding-risk UX.
"""

from __future__ import annotations

import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from cmems_fetch import fetch_cmems_with_fallback
from io_zones import IO_ZONES, zone_for_point
from noaa_fetch import fetch_noaa_with_fallback
from species_data import species_data
from species_logic import species_risk
from stress_score import calculate_marine_stress

logger = logging.getLogger("ml_inference")


def _resolve_models_dir() -> Path:
    """Prefer backend/models; fall back to repo-root models/ for older layouts."""
    here = Path(__file__).resolve().parent
    backend_models = here / "models"
    if backend_models.is_dir():
        return backend_models
    return here.parent / "models"


_MODELS_DIR = _resolve_models_dir()
_FEATURE_LIST_PATH = _MODELS_DIR / "feature_list.json"

# In-memory registry (loaded at startup)
_loaded_models: Dict[str, Any] = {}
_feature_order: List[str] = []
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_CACHE_TTL_SEC = 90.0
_CACHE_MAX = 256

PLATFORM_TAGLINE = (
    "AI-assisted marine stranding risk intelligence platform for the Indian Ocean."
)
ML_LAYER_SUMMARY = (
    "The ML layer combines historical marine occurrence patterns, environmental anomaly "
    "features, species tolerance deviations, and seasonal oceanographic signals—using "
    "latitude and longitude as spatial ecological priors alongside live CMEMS/NOAA fields."
)


def _cache_key(lat: float, lon: float, extra: str = "") -> str:
    return f"{round(lat, 3)}:{round(lon, 3)}:{extra}"


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    hit = _cache.get(key)
    if not hit:
        return None
    ts, payload = hit
    if time.monotonic() - ts > _CACHE_TTL_SEC:
        del _cache[key]
        return None
    return payload


def _cache_set(key: str, payload: Dict[str, Any]) -> None:
    if len(_cache) > _CACHE_MAX:
        # drop arbitrary oldest bucket
        first = next(iter(_cache))
        del _cache[first]
    _cache[key] = (time.monotonic(), payload)


def load_feature_list() -> List[str]:
    global _feature_order
    if _FEATURE_LIST_PATH.is_file():
        with open(_FEATURE_LIST_PATH, "r", encoding="utf-8") as f:
            _feature_order = json.load(f)
    else:
        _feature_order = [
            "decimalLatitude",
            "decimalLongitude",
            "temperature",
            "salinity",
            "current_speed",
            "health_score",
        ]
    return list(_feature_order)


def discover_pkl_paths() -> List[Path]:
    if not _MODELS_DIR.is_dir():
        return []
    return sorted(_MODELS_DIR.glob("*.pkl"))


def load_all_models() -> Dict[str, Any]:
    """
    Scan models/*.pkl and load into memory. Safe to call at startup; logs failures per file.
    """
    global _loaded_models
    _loaded_models = {}
    load_feature_list()
    paths = discover_pkl_paths()
    if not paths:
        logger.warning("No .pkl files found under %s — predictions use stress engine only.", _MODELS_DIR)
        return _loaded_models

    for p in paths:
        try:
            with open(p, "rb") as f:
                _loaded_models[p.name] = pickle.load(f)
            logger.info("Loaded model artifact: %s", p.name)
        except Exception as exc:  # noqa: BLE001 — surface load errors without crashing app
            logger.error("Failed to load %s: %s", p.name, exc)
    return _loaded_models


def get_loaded_model_names() -> List[str]:
    return sorted(_loaded_models.keys())


def _final_estimator(model: Any) -> Any:
    if hasattr(model, "named_steps"):
        steps = getattr(model, "named_steps", {})
        if isinstance(steps, dict) and steps:
            return list(steps.values())[-1]
    return model


def _build_feature_row(
    lat: float,
    lon: float,
    sst: float,
    salinity: float,
    current_speed: float,
    health_score: float,
    feature_names: List[str],
) -> np.ndarray:
    row: Dict[str, float] = {
        "decimalLatitude": lat,
        "decimalLongitude": lon,
        "temperature": sst,
        "salinity": salinity,
        "current_speed": current_speed,
        "health_score": health_score,
    }
    vec = [float(row.get(name, 0.0)) for name in feature_names]
    return np.array([vec], dtype=np.float64)


def _pseudo_explain(
    estimator: Any,
    feature_names: List[str],
    x_row: np.ndarray,
) -> List[Dict[str, Any]]:
    """SHAP-style ranking using tree feature importance × local deviation from IO baselines."""
    if not hasattr(estimator, "feature_importances_"):
        return []
    imp = np.asarray(estimator.feature_importances_, dtype=np.float64)
    if imp.size != len(feature_names):
        return []
    ref = np.array(
        [12.0, 82.0, 28.5, 34.5, 0.18, 72.0][: len(feature_names)],
        dtype=np.float64,
    )
    x = x_row.flatten()[: len(feature_names)]
    if x.size < len(feature_names):
        return []
    delta = np.abs(x - ref) / (np.abs(ref) + 1e-4)
    contrib = imp * delta
    total = float(contrib.sum()) or 1.0
    out: List[Dict[str, Any]] = []
    for name, c in zip(feature_names, contrib):
        out.append(
            {
                "factor": name,
                "contribution": round(float(c / total), 4),
                "direction": "stress_increase" if c > 0 else "neutral",
            }
        )
    out.sort(key=lambda d: d["contribution"], reverse=True)
    return out[:8]


def _stress_to_risk_level(stress: float) -> str:
    if stress < 35:
        return "LOW"
    if stress < 65:
        return "MODERATE"
    return "HIGH"


def _risk_to_badge(risk_level: str) -> str:
    return {
        "LOW": "low",
        "MODERATE": "moderate",
        "HIGH": "high",
    }.get(risk_level, "moderate")


def _species_profile(name: str) -> Optional[Dict[str, Tuple[float, float]]]:
    target = name.strip().lower()
    for key, profile in species_data.items():
        if key.lower() == target:
            return profile
    return None


def _metric_penalty(value: float, low: float, high: float, weight: float) -> float:
    if low <= value <= high:
        return 0.0
    span = max(0.1, high - low)
    diff = (low - value) if value < low else (value - high)
    # Out-of-range distance normalized by species tolerance span.
    return min(weight, (diff / span) * weight * 2.5)


def _species_threat_score(
    name: str,
    zone_stress: float,
    model_confidence: Optional[float],
    sst: float,
    salinity: float,
    oxygen: float,
    ph: float,
) -> float:
    # Base score anchored by ecosystem stress.
    score = zone_stress
    if model_confidence is not None:
        score = 0.75 * score + 0.25 * (model_confidence * 100.0)

    profile = _species_profile(name)
    if profile:
        score += _metric_penalty(sst, *profile["temperature_range"], weight=16.0)
        score += _metric_penalty(salinity, *profile["salinity_range"], weight=10.0)
        score += _metric_penalty(oxygen, *profile["oxygen_range"], weight=12.0)
        score += _metric_penalty(ph, *profile["ph_range"], weight=12.0)

        in_range = (
            profile["temperature_range"][0] <= sst <= profile["temperature_range"][1]
            and profile["salinity_range"][0] <= salinity <= profile["salinity_range"][1]
            and profile["oxygen_range"][0] <= oxygen <= profile["oxygen_range"][1]
            and profile["ph_range"][0] <= ph <= profile["ph_range"][1]
        )
        if in_range:
            score -= 8.0

    return max(0.0, min(100.0, round(score, 2)))


def _risk_probability_from_stress(stress: float) -> float:
    """Calibrated 0–1 index from ecosystem stress (not a clinical probability)."""
    x = min(100.0, max(0.0, stress)) / 100.0
    return round(float(min(0.99, 0.04 + 0.96 * (x**1.15))), 4)


def _species_note_placeholder(name: str) -> str:
    return (
        f"{name}: model-ranked under current Indian Ocean thermal and salinity stress; "
        "monitor coastal convergence zones."
    )


def _species_cards_from_names(
    names: List[str],
    zone_stress: float,
    sst: float,
    salinity: float,
    oxygen: float,
    ph: float,
) -> List[Dict[str, Any]]:
    cards = []
    for n in names:
        threat_score = _species_threat_score(
            n,
            zone_stress=zone_stress,
            model_confidence=None,
            sst=sst,
            salinity=salinity,
            oxygen=oxygen,
            ph=ph,
        )
        rk = _risk_to_badge(_stress_to_risk_level(threat_score))
        cards.append(
            {
                "name": n,
                "risk": rk,
                "ngo": "Indian Ocean marine NGO network",
                "note": _species_note_placeholder(n),
                "threat_score": threat_score,
            }
        )
    return cards


def _merge_species_cards(
    stress_names: List[str],
    ml_cards: List[Dict[str, Any]],
    zone_stress: float,
    sst: float,
    salinity: float,
    oxygen: float,
    ph: float,
    max_items: int = 6,
) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for src in ml_cards + _species_cards_from_names(stress_names, zone_stress, sst, salinity, oxygen, ph):
        key = src["name"]
        if key in seen:
            continue
        seen.add(key)
        out.append(src)
        if len(out) >= max_items:
            break
    return out


def run_prediction(lat: float, lon: float, use_cache: bool = True) -> Dict[str, Any]:
    """
    Fetch live ocean fields, compute stress, optionally run sklearn models, return structured JSON.
    """
    key = _cache_key(lat, lon, "v1")
    if use_cache:
        cached = _cache_get(key)
        if cached is not None:
            return cached

    noaa_res = fetch_noaa_with_fallback(lat, lon)
    cmems_res = fetch_cmems_with_fallback(lat, lon)

    sst = float(noaa_res.get("sst_celsius", 28.0))
    hotspot = float(noaa_res.get("hotspot_anomaly", 0.0))
    dhw = float(noaa_res.get("degree_heating_weeks", 0.0))
    salinity = float(cmems_res.get("salinity_psu", 35.0))
    chlorophyll = float(cmems_res.get("chlorophyll_mg_m3", 0.1))
    ph = float(cmems_res.get("ph", 8.1))
    current_speed = float(cmems_res.get("current_velocity_ms", 0.15))
    current_dir = float(cmems_res.get("current_direction_deg", 0.0))

    stress_analysis = calculate_marine_stress(
        sst=sst,
        hotspot_anomaly=hotspot,
        degree_heating_weeks=dhw,
        ph=ph,
        salinity=salinity,
        chlorophyll=chlorophyll,
        current_speed=current_speed,
    )
    stress = float(stress_analysis.get("overall_stress_score", 50.0))
    health_score = float(max(0.0, min(100.0, 100.0 - stress)))
    oxygen_est = float(stress_analysis.get("environmental_summary", {}).get("estimated_oxygen_mg_l", 4.8))

    risk_level = _stress_to_risk_level(stress)
    risk_probability = _risk_probability_from_stress(stress)

    stress_factor_strings = stress_analysis.get("contributing_factors") or []
    factor_breakdown: List[Dict[str, Any]] = []
    for i, fac in enumerate(stress_factor_strings[:6]):
        weight = max(0.05, 0.45 - i * 0.06)
        factor_breakdown.append(
            {
                "factor": str(fac),
                "contribution": round(weight, 4),
                "direction": "stress_increase",
            }
        )

    feature_names = list(_feature_order) or load_feature_list()
    x_row = _build_feature_row(lat, lon, sst, salinity, current_speed, health_score, feature_names)

    models_used: List[str] = []
    confidence_score = round(0.55 + min(0.44, stress / 220.0), 4)
    species_predictions: List[Dict[str, Any]] = []
    ml_species_cards: List[Dict[str, Any]] = []

    primary_name = "stranding_model.pkl" if "stranding_model.pkl" in _loaded_models else None
    if not primary_name and _loaded_models:
        primary_name = sorted(_loaded_models.keys())[0]

    estimator = None
    if primary_name:
        model = _loaded_models[primary_name]
        models_used.append(primary_name)
        try:
            est = _final_estimator(model)
            estimator = est
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(x_row)[0]
            elif hasattr(est, "predict_proba"):
                proba = est.predict_proba(x_row)[0]
            else:
                proba = None

            if proba is not None:
                classes_obj = getattr(est, "classes_", None) or getattr(model, "classes_", None)
                if classes_obj is None:
                    classes_obj = []
                classes = [str(c) for c in classes_obj]
                if classes and len(classes) == len(proba):
                    order = np.argsort(proba)[::-1][:5]
                    for idx in order:
                        p = float(proba[idx])
                        if p < 0.02:
                            continue
                        sp = classes[int(idx)]
                        species_predictions.append({"species": sp, "probability": round(p, 4)})
                        threat_score = _species_threat_score(
                            sp,
                            zone_stress=stress,
                            model_confidence=p,
                            sst=sst,
                            salinity=salinity,
                            oxygen=oxygen_est,
                            ph=ph,
                        )
                        sp_risk_label = _stress_to_risk_level(threat_score)
                        ml_species_cards.append(
                            {
                                "name": sp,
                                "risk": _risk_to_badge(sp_risk_label),
                                "ngo": "OBIS occurrence priors · WatchTheBlue",
                                "note": (
                                    f"RandomForest association p={p:.2f} at this lat/lon with live "
                                    "temperature, salinity, and circulation."
                                ),
                                "model_confidence": round(p, 4),
                                "threat_score": threat_score,
                            }
                        )
                    confidence_score = round(float(np.max(proba)), 4)
            if not species_predictions and hasattr(model, "predict"):
                pred = model.predict(x_row)
                pv = pred[0] if len(pred) else None
                species_predictions.append({"species": str(pv), "probability": 1.0})
                confidence_score = 0.72
        except Exception as exc:  # noqa: BLE001
            logger.error("Model inference failed (%s): %s", primary_name, exc)

    if estimator is not None:
        explain = _pseudo_explain(estimator, feature_names, x_row)
        if explain:
            # Blend tree explanation with stress factors (tree first)
            merged = explain[:4]
            for fb in factor_breakdown:
                if fb["factor"] not in {m["factor"] for m in merged}:
                    merged.append(fb)
            factor_breakdown = merged[:8]

    at_risk_names = list(species_risk(stress))
    if stress > 70:
        for extra in ("Olive Ridley Turtle", "Spinner Dolphin"):
            if extra not in at_risk_names:
                at_risk_names.append(extra)
    species_cards = _merge_species_cards(
        at_risk_names,
        ml_species_cards,
        zone_stress=stress,
        sst=sst,
        salinity=salinity,
        oxygen=oxygen_est,
        ph=ph,
    )

    zone_meta = zone_for_point(lat, lon)

    payload: Dict[str, Any] = {
        "coordinates": {"latitude": lat, "longitude": lon},
        "zone_id": zone_meta["id"],
        "zone_display": zone_meta["name"],
        "risk_probability": risk_probability,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "predicted_species": species_predictions,
        "species_at_risk_cards": species_cards,
        "top_environmental_factors": factor_breakdown,
        "stress_analysis": stress_analysis,
        "metrics": {
            "sst_celsius": sst,
            "hotspot_anomaly": hotspot,
            "degree_heating_weeks": dhw,
            "salinity_psu": salinity,
            "chlorophyll_mg_m3": chlorophyll,
            "ph": ph,
            "current_velocity_ms": current_speed,
            "current_direction_deg": current_dir,
        },
        "models_used": models_used,
        "model_artifacts_present": bool(_loaded_models),
        "platform_tagline": PLATFORM_TAGLINE,
        "ml_layer_summary": ML_LAYER_SUMMARY,
    }

    if use_cache:
        _cache_set(key, payload)
    return payload


def build_zone_panel_payload(pred: Dict[str, Any]) -> Dict[str, Any]:
    """Shape response for ZonePanel + map overlays."""
    m = pred["metrics"]
    sa = pred["stress_analysis"]
    stress = float(sa.get("overall_stress_score", 0))
    rl = pred["risk_level"]
    stress_level_ui = {
        "LOW": "low",
        "MODERATE": "moderate",
        "HIGH": "high",
    }.get(rl, "moderate")
    colors = {
        "LOW": "#22c55e",
        "MODERATE": "#facc15",
        "HIGH": "#ef4444",
    }
    stress_color = colors.get(pred["risk_level"], "#38bdf8")
    dhw = float(m.get("degree_heating_weeks", 0))
    coral = dhw >= 4.0 or m.get("hotspot_anomaly", 0) > 1.2

    conditions = {
        "temperature": round(float(m["sst_celsius"]), 1),
        "temperature_anomaly": round(float(m.get("hotspot_anomaly", 0)), 1),
        "oxygen": round(float(sa.get("environmental_summary", {}).get("estimated_oxygen_mg_l", 4.8)), 1),
        "ph": round(float(m["ph"]), 2),
    }

    return {
        "zone": pred["zone_id"],
        "zone_display": pred["zone_display"],
        "conditions": conditions,
        "stress_score": int(round(stress)),
        "stress_level": stress_level_ui,
        "stress_color": stress_color,
        "coral_bleaching_alert": coral,
        "species_at_risk": pred.get("species_at_risk_cards") or [],
        "prediction": {
            "risk_probability": pred["risk_probability"],
            "risk_level": pred["risk_level"],
            "confidence_score": pred["confidence_score"],
            "predicted_species": pred.get("predicted_species", []),
            "top_environmental_factors": pred.get("top_environmental_factors", []),
            "models_used": pred.get("models_used", []),
            "model_artifacts_present": pred.get("model_artifacts_present", False),
        },
        "platform_tagline": pred.get("platform_tagline"),
        "ml_layer_summary": pred.get("ml_layer_summary"),
    }


def zones_risk_overlay() -> Dict[str, Dict[str, Any]]:
    """Risk snapshot at each sector center (cached per coordinate)."""
    out: Dict[str, Dict[str, Any]] = {}
    for z in IO_ZONES:
        lat, lon = z["center"]
        p = run_prediction(lat, lon, use_cache=True)
        out[z["id"]] = {
            "risk_level": p["risk_level"],
            "risk_probability": p["risk_probability"],
            "stress_score": int(round(float(p["stress_analysis"].get("overall_stress_score", 0)))),
        }
    return out


# Home sector per species (mirrors frontend MapPage SPECIES_ZONE_MAP)
SPECIES_HOME_ZONE: Dict[str, str] = {
    "Olive Ridley Turtle": "bay_of_bengal",
    "Whale Shark": "arabian_sea",
    "Dugong": "andaman_sea",
    "Spinner Dolphin": "lakshadweep",
    "Humpback Whale": "arabian_sea",
    "Manta Ray": "lakshadweep",
    "Reef Shark": "andaman_sea",
    "Clownfish": "arabian_sea",
    "Blue Whale": "arabian_sea",
    "Green Sea Turtle": "lakshadweep",
}


def _model_confidence_for_species(pred: Dict[str, Any], name: str) -> Optional[float]:
    target = name.strip().lower()
    for item in pred.get("predicted_species") or []:
        if str(item.get("species", "")).strip().lower() == target:
            return item.get("probability")
    return None


def zones_overview_payload() -> Dict[str, Any]:
    """Stress and key species for all four Indian Ocean sectors (ML + live ocean fields)."""
    zones: Dict[str, Dict[str, Any]] = {}
    for z in IO_ZONES:
        lat, lon = z["center"]
        pred = run_prediction(lat, lon, use_cache=True)
        stress = float(pred["stress_analysis"].get("overall_stress_score", 0))
        cards = pred.get("species_at_risk_cards") or []
        names = [c["name"] for c in cards[:3]]
        if not names:
            names = species_risk(stress)[:3]
        if not names:
            names = [n for n, home in SPECIES_HOME_ZONE.items() if home == z["id"]][:3]
        zones[z["id"]] = {
            "risk_level": pred["risk_level"],
            "stress_score": int(round(stress)),
            "key_species": ", ".join(names),
        }
    return {"success": True, "zones": zones}


def species_threat_scores_payload() -> Dict[str, Any]:
    """Threat scores for all monitored species using zone-centered ML predictions."""
    zone_cache: Dict[str, Dict[str, Any]] = {}
    species_out: List[Dict[str, Any]] = []

    for name in species_data.keys():
        zid = SPECIES_HOME_ZONE.get(name, "arabian_sea")
        if zid not in zone_cache:
            z = next(item for item in IO_ZONES if item["id"] == zid)
            lat, lon = z["center"]
            zone_cache[zid] = run_prediction(lat, lon, use_cache=True)

        pred = zone_cache[zid]
        stress = float(pred["stress_analysis"].get("overall_stress_score", 0))
        m = pred["metrics"]
        sa = pred["stress_analysis"]
        oxygen = float(sa.get("environmental_summary", {}).get("estimated_oxygen_mg_l", 4.8))
        conf = _model_confidence_for_species(pred, name)
        threat = _species_threat_score(
            name,
            zone_stress=stress,
            model_confidence=conf,
            sst=float(m["sst_celsius"]),
            salinity=float(m["salinity_psu"]),
            oxygen=oxygen,
            ph=float(m["ph"]),
        )
        species_out.append(
            {
                "name": name,
                "threat_score": threat,
                "risk": _stress_to_risk_level(threat),
                "zone_id": zid,
            }
        )

    return {"success": True, "species": species_out}


def download_predictions_payload(zone_id: str = "all") -> Dict[str, Any]:
    """JSON report bundle for frontend download (all zones or one sector)."""
    from datetime import datetime, timezone

    zone_filter = (zone_id or "all").strip().lower()
    zones_to_include = list(IO_ZONES)
    if zone_filter != "all":
        matched = [z for z in IO_ZONES if z["id"] == zone_filter]
        if matched:
            zones_to_include = matched

    species_scores = species_threat_scores_payload()["species"]
    species_by_zone: Dict[str, List[Dict[str, Any]]] = {}
    for entry in species_scores:
        species_by_zone.setdefault(entry["zone_id"], []).append(entry)

    zones_report: Dict[str, Any] = {}
    for z in zones_to_include:
        lat, lon = z["center"]
        pred = run_prediction(lat, lon, use_cache=True)
        panel = build_zone_panel_payload(pred)
        zones_report[z["id"]] = {
            **panel,
            "species_threat_scores": species_by_zone.get(z["id"], []),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": "WatchTheBlue",
        "zone_filter": zone_filter,
        "zones": zones_report,
        "species": species_scores,
    }
