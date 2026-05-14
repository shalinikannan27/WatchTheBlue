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
from cmems_fetch import fetch_cmems_with_fallback
from stress_score import calculate_marine_stress, get_species_stress_impact
from species_logic import species_risk
from ml_inference import (
    load_all_models,
    run_prediction,
    build_zone_panel_payload,
    zones_risk_overlay,
    get_loaded_model_names,
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
    allow_origins=["*"],  # Adjust for production security
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


@app.get("/api/health/prediction")
def api_prediction_health():
    """
    Lightweight health endpoint for frontend preflight status.
    Checks model artifact availability and one cached-safe inference path.
    """
    model_names = get_loaded_model_names()
    try:
        sample = run_prediction(13.0, 80.0, use_cache=True)
        return {
            "success": True,
            "status": "online",
            "message": "Prediction inference available",
            "model_artifacts_present": bool(model_names),
            "models_loaded": model_names,
            "sample_zone": sample.get("zone_display"),
            "sample_risk_level": sample.get("risk_level"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("api_prediction_health failed: %s", exc)
        return {
            "success": False,
            "status": "offline",
            "message": "Prediction inference unavailable",
            "model_artifacts_present": bool(model_names),
            "models_loaded": model_names,
        }


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


def get_zone_name(lat: float, lon: float) -> str:
    if 8 <= lat <= 12 and 71 <= lon <= 74:
        return "Lakshadweep"
    elif 6 <= lat <= 14 and 92 <= lon <= 94:
        return "Andaman and Nicobar"
    elif 8 <= lat <= 25 and 65 <= lon <= 77:
        return "Arabian Sea"
    elif 8 <= lat <= 22 and 78 <= lon <= 90:
        return "Bay of Bengal"
    elif -20 <= lat <= 30 and 40 <= lon <= 100:
        return "Indian Ocean"
    else:
        return "Open Ocean"

@app.get("/api/zone")
def get_zone(lat: float, lon: float):
    zone_name = get_zone_name(lat, lon)
    
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    
    sst = noaa_res.get("sst_celsius", 29.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    
    ph = cmems_res.get("ph", 7.8)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
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
    
    stress = stress_analysis.get("overall_stress_score", 72)
    
    if stress > 70:
        risk_level = "High"
    elif stress > 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    conditions = {
        "temperature": round(sst, 1),
        "oxygen": 4.5,
        "ph": round(ph, 1)
    }

    at_risk = species_risk(stress)
    
    # Ensure example species are included if stress is high as requested
    if stress > 70:
        if "Olive Ridley Turtle" not in at_risk:
            at_risk.append("Olive Ridley Turtle")
        if "Spinner Dolphin" not in at_risk:
            at_risk.append("Spinner Dolphin")

    return {
        "zone": zone_name,
        "stress_score": stress,
        "risk_level": risk_level,
        "conditions": conditions,
        "species_at_risk": at_risk
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
