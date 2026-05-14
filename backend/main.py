import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environmental variables from .env
load_dotenv()

# Import local handlers
from obis_fetch import get_species_by_location
from noaa_fetch import fetch_noaa_with_fallback, get_bleaching_alert_level
from cmems_fetch import fetch_cmems_with_fallback, get_ocean_conditions
try:
    from drift.drift_model import backward_drift
except ImportError:
    backward_drift = None
from io_zones import IO_ZONES
from species_data import species_data
from datetime import datetime, timezone
from stress_score import calculate_marine_stress, get_species_stress_impact
from species_logic import species_risk
from ml_inference import (
    load_all_models,
    run_prediction,
    build_zone_panel_payload,
    zones_risk_overlay,
    get_loaded_model_names,
    predict_species_risk,
)

logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_all_models()
    logger.info("ML artifacts in memory: %s", get_loaded_model_names() or "(none)")
    yield


app = FastAPI(
    title="WatchTheBlue API Backend",
    description="Marine biodiversity, ecological stress, and ocean temperature forecasting server.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for seamless frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response Models
class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class MarineMetrics(BaseModel):
    sst_celsius: float
    hotspot_anomaly: float
    degree_heating_weeks: float
    salinity_psu: float
    chlorophyll_mg_m3: float
    ph: float
    current_velocity_ms: float
    current_direction_deg: float

class StressScoreResponse(BaseModel):
    coordinates: Coordinates
    metrics: MarineMetrics
    stress_analysis: Dict[str, Any]

@app.get("/")
def home():
    """
    Root directory metadata
    """
    return {"message": "OceanPulse Backend Running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": len(get_loaded_model_names()) > 0}

@app.get("/api/noaa/sst")
def get_noaa_sst(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate")
):
    """
    Fetch satellite-based Sea Surface Temperature (SST) metrics from NOAA.
    
    Returns:
    - sst_celsius: Current sea surface temperature
    - hotspot_anomaly: Difference from climatological normal (thermal stress indicator)
    - degree_heating_weeks: Accumulated thermal stress (coral bleaching indicator)
    - bleaching_alert: Risk level for coral bleaching
    
    No API key required. Uses public NOAA ERDDAP service.
    Falls back to realistic simulation if NOAA API unavailable.
    """
    result = fetch_noaa_with_fallback(lat, lon)
    
    # Add bleaching alert level
    dhw = result.get("degree_heating_weeks", 0)
    result["bleaching_alert"] = get_bleaching_alert_level(dhw)
    
    return result

@app.get("/api/cmems/marine-metrics")
def get_cmems_metrics(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate"),
    date: Optional[str] = Query(None, description="Date in format YYYY-MM-DD")
):
    """
    Retrieve oceanographic parameters (Salinity, pH, Chlorophyll, Currents) from Copernicus Marine.
    
    Returns real CMEMS data when available. If CMEMS API is unavailable,
    gracefully falls back to realistic oceanographic simulation.
    """
    return fetch_cmems_with_fallback(lat, lon, date)

@app.get("/api/ecological-stress", response_model=StressScoreResponse)
def get_ecological_stress(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate")
):
    """
    Perform deep statistical ecosystem mapping and output localized marine environmental stress scores.
    """
    # 1. Fetch NOAA data (SST, Anomaly, DHW) with fallback
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    sst = noaa_res.get("sst_celsius", 25.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    
    # 2. Fetch CMEMS data (Salinity, Chlorophyll, pH, Currents) with fallback
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
    ph = cmems_res.get("ph", 8.1)
    current_speed = cmems_res.get("current_velocity_ms", 0.15)
    current_dir = cmems_res.get("current_direction_deg", 0.0)
    
    # 3. Calculate Consolidated Stress
    stress_analysis = calculate_marine_stress(
        sst=sst,
        hotspot_anomaly=hotspot,
        degree_heating_weeks=dhw,
        ph=ph,
        salinity=salinity,
        chlorophyll=chlorophyll,
        current_speed=current_speed
    )
    
    return {
        "coordinates": {"latitude": lat, "longitude": lon},
        "metrics": {
            "sst_celsius": sst,
            "hotspot_anomaly": hotspot,
            "degree_heating_weeks": dhw,
            "salinity_psu": salinity,
            "chlorophyll_mg_m3": chlorophyll,
            "ph": ph,
            "current_velocity_ms": current_speed,
            "current_direction_deg": current_dir
        },
        "stress_analysis": stress_analysis
    }

@app.get("/api/species/habitat-suitability")
def get_habitat_suitability(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0)
):
    """
    Assess species habitat suitability and occurrence data under current environmental metrics at a coordinate.
    
    Returns:
    - Environmental metrics (SST, pH, Salinity) from NOAA and CMEMS
    - Species occurrence data from OBIS showing what lives in this area
    - Ecosystem stress score affecting species vulnerability
    - Species-specific vulnerability assessment based on current stress
    """
    # Fetch ambient environment
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    
    current_env = {
        "sst_celsius": noaa_res.get("sst_celsius"),
        "hotspot_anomaly": noaa_res.get("hotspot_anomaly"),
        "degree_heating_weeks": noaa_res.get("degree_heating_weeks"),
        "bleaching_alert": get_bleaching_alert_level(noaa_res.get("degree_heating_weeks", 0)),
        "ph": cmems_res.get("ph"),
        "salinity_psu": cmems_res.get("salinity_psu"),
        "chlorophyll_mg_m3": cmems_res.get("chlorophyll_mg_m3")
    }
    
    # Calculate ecosystem stress score
    sst = noaa_res.get("sst_celsius", 25.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
    ph = cmems_res.get("ph", 8.1)
    current_speed = cmems_res.get("current_velocity_ms", 0.15)
    
    stress_analysis = calculate_marine_stress(
        sst=sst,
        hotspot_anomaly=hotspot,
        degree_heating_weeks=dhw,
        ph=ph,
        salinity=salinity,
        chlorophyll=chlorophyll,
        current_speed=current_speed
    )
    ecosystem_stress_score = stress_analysis.get("overall_stress_score", 0)
    
    # Fetch species occurrence data from OBIS
    species_data = get_species_by_location(lat, lon)
    species_occurrences = species_data.get("occurrences", [])
    
    # Calculate species-specific vulnerabilities
    species_vulnerability = []
    for species in species_occurrences:
        species_name = species.get("scientific_name", "Unknown")
        impact = get_species_stress_impact(species_name, ecosystem_stress_score)
        species_vulnerability.append({
            "species_occurrence": species,
            "stress_impact": impact
        })
    
    return {
        "coordinates": {"latitude": lat, "longitude": lon},
        "environmental_metrics": current_env,
        "ecosystem_stress": {
            "stress_score": ecosystem_stress_score,
            "stress_level": stress_analysis.get("stress_level", "UNKNOWN"),
            "contributing_factors": stress_analysis.get("contributing_factors", [])
        },
        "species_occurrences": species_vulnerability,
        "species_count": species_data.get("count", 0),
        "data_source": species_data.get("source", "OBIS API")
    }


@app.get("/api/predict")
def api_predict(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
):
    """
    Core ML + stress fusion for a coordinate. Uses cached live fetches when possible.
    """
    try:
        pred = run_prediction(lat, lon, use_cache=True)
        return {"success": True, **pred}
    except Exception as exc:  # noqa: BLE001
        logger.exception("api_predict failed: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction pipeline failed") from exc


@app.get("/api/species-risk")
def api_species_risk(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
):
    """
    Stranding / drift focal point: full point prediction plus sector-wide risk overlay
    for map integration (cached per sector center).
    """
    try:
        pred = run_prediction(lat, lon, use_cache=True)
        overlay = zones_risk_overlay()
        return {
            "success": True,
            "focus_coordinates": pred["coordinates"],
            "point_prediction": pred,
            "zones_risk_overlay": overlay,
            "panel": build_zone_panel_payload(pred),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("api_species-risk failed: %s", exc)
        raise HTTPException(status_code=500, detail="Species risk analysis failed") from exc


@app.get("/api/zone-analysis")
def api_zone_analysis(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
):
    """
    Map zone click: live ocean conditions, stress, ML species ranking, and all-sector overlay.
    """
    try:
        pred = run_prediction(lat, lon, use_cache=True)
        panel = build_zone_panel_payload(pred)
        panel["zones_risk_overlay"] = zones_risk_overlay()
        panel["success"] = True
        return panel
    except Exception as exc:  # noqa: BLE001
        logger.exception("api_zone-analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail="Zone analysis failed") from exc


@app.get("/api/zone/{zone_id}")
def get_zone_by_id(zone_id: str):
    zone = next((z for z in IO_ZONES if z["id"] == zone_id), None)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    lat, lon = zone["center"]
    now = datetime.now(timezone.utc)
    month = now.month

    conds = get_ocean_conditions(lat, lon)
    temp = conds.get("temperature", 28.0)
    sal = conds.get("salinity", 35.0)
    o2 = conds.get("oxygen", 5.0)
    ph = conds.get("ph", 8.1)
    speed = conds.get("current_speed", 0.1)

    species_risks = []
    for sp in species_data.keys():
        risk = predict_species_risk(
            lat=lat, lon=lon,
            temperature=temp, salinity=sal, oxygen=o2, ph=ph, current_speed=speed,
            month=month, species_name=sp
        )
        species_risks.append({
            "species": sp,
            "risk_level": risk["risk_level"],
            "risk_probability": risk["risk_probability"],
            "top_factors": risk["top_factors"]
        })
    
    levels = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
    worst_level_str = "LOW"
    worst_level_int = 1
    max_prob = 0.0
    for r in species_risks:
        l = levels.get(r["risk_level"], 1)
        if l > worst_level_int:
            worst_level_int = l
            worst_level_str = r["risk_level"]
        if float(r["risk_probability"]) > max_prob:
            max_prob = float(r["risk_probability"])
            
    stress_score = int(max_prob * 100)

    return {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "conditions": conds,
        "overall_stress": worst_level_str,
        "stress_score": stress_score,
        "species_risks": species_risks,
        "timestamp": now.isoformat()
    }

@app.get("/api/drift")
def get_drift(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    date: str = Query(..., description="YYYY-MM-DD")
):
    if not backward_drift:
        raise HTTPException(status_code=500, detail="Drift model not available")
    return backward_drift(lat, lon, date)

@app.get("/api/species/{species_name}")
def get_species_risk_all_zones(species_name: str):
    if species_name not in species_data:
        raise HTTPException(status_code=404, detail="Species not found")
    
    now = datetime.now(timezone.utc)
    month = now.month
    zone_risks = []

    for z in IO_ZONES:
        lat, lon = z["center"]
        conds = get_ocean_conditions(lat, lon)
        temp = conds.get("temperature", 28.0)
        sal = conds.get("salinity", 35.0)
        o2 = conds.get("oxygen", 5.0)
        ph = conds.get("ph", 8.1)
        speed = conds.get("current_speed", 0.1)

        risk = predict_species_risk(
            lat=lat, lon=lon,
            temperature=temp, salinity=sal, oxygen=o2, ph=ph, current_speed=speed,
            month=month, species_name=species_name
        )
        zone_risks.append({
            "zone_id": z["id"],
            "zone_name": z["name"],
            "risk_level": risk["risk_level"],
            "risk_probability": risk["risk_probability"],
            "top_factors": risk["top_factors"]
        })
    
    return {
        "species": species_name,
        "timestamp": now.isoformat(),
        "zones": zone_risks
    }

@app.get("/api/overview")
def get_overview():
    now = datetime.now(timezone.utc)
    month = now.month
    overview = []

    for z in IO_ZONES:
        lat, lon = z["center"]
        conds = get_ocean_conditions(lat, lon)
        temp = conds.get("temperature", 28.0)
        sal = conds.get("salinity", 35.0)
        o2 = conds.get("oxygen", 5.0)
        ph = conds.get("ph", 8.1)
        speed = conds.get("current_speed", 0.1)

        species_risks = []
        for sp in species_data.keys():
            risk = predict_species_risk(
                lat=lat, lon=lon,
                temperature=temp, salinity=sal, oxygen=o2, ph=ph, current_speed=speed,
                month=month, species_name=sp
            )
            species_risks.append(risk)
            
        levels = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
        worst_level_str = "LOW"
        worst_level_int = 1
        max_prob = 0.0
        for r in species_risks:
            l = levels.get(r["risk_level"], 1)
            if l > worst_level_int:
                worst_level_int = l
                worst_level_str = r["risk_level"]
            if float(r["risk_probability"]) > max_prob:
                max_prob = float(r["risk_probability"])
                
        stress_score = int(max_prob * 100)

        overview.append({
            "zone_id": z["id"],
            "zone_name": z["name"],
            "overall_stress": worst_level_str,
            "stress_score": stress_score,
            "conditions": conds,
            "timestamp": now.isoformat()
        })

    return {"zones": overview}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
