import os
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environmental variables from .env
load_dotenv()

# Import local handlers
from obis_fetch import fetch_obis_occurrences, fetch_taxon_info, search_taxon
from noaa_fetch import fetch_noaa_sst_data
from cmems_fetch import fetch_cmems_marine_data
from stress_score import calculate_marine_stress
from species_logic import analyze_habitat_suitability, clean_obis_coordinates, get_species_profile

app = FastAPI(
    title="WatchTheBlue API Backend",
    description="Marine biodiversity, ecological stress, and ocean temperature forecasting server.",
    version="1.0.0"
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
def read_root():
    """
    Root directory metadata
    """
    return {
        "app": "WatchTheBlue Backend Service",
        "version": "1.0.0",
        "status": "Online",
        "documentation": "/docs",
        "endpoints": {
            "obis_occurrences": "/api/obis/occurrences",
            "noaa_sst": "/api/noaa/sst",
            "cmems_marine_metrics": "/api/cmems/marine-metrics",
            "ecological_stress": "/api/ecological-stress",
            "species_habitat_suitability": "/api/species/habitat-suitability"
        }
    }

@app.get("/api/obis/occurrences")
def get_obis_occurrences(
    scientific_name: Optional[str] = Query(None, description="Scientific name of species to fetch"),
    taxon_id: Optional[int] = Query(None, description="AphiaID/taxonid of species"),
    geometry: Optional[str] = Query(None, description="WKT boundary spatial polygon"),
    size: int = Query(100, ge=1, le=1000, description="Max records to return")
):
    """
    Retrieve geolocated species records from the OBIS database.
    """
    if not scientific_name and not taxon_id:
        raise HTTPException(status_code=400, detail="Please provide either 'scientific_name' or 'taxon_id'")
        
    raw_data = fetch_obis_occurrences(
        scientific_name=scientific_name,
        taxon_id=taxon_id,
        geometry=geometry,
        size=size
    )
    
    clean_records = clean_obis_coordinates(raw_data)
    
    return {
        "query": {
            "scientific_name": scientific_name,
            "taxon_id": taxon_id,
            "size": size
        },
        "count_returned": len(clean_records),
        "count_total_raw": raw_data.get("count", 0),
        "results": clean_records
    }

@app.get("/api/noaa/sst")
def get_noaa_sst(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate")
):
    """
    Fetch satellite-based Sea Surface Temperature (SST) metrics from NOAA.
    """
    return fetch_noaa_sst_data(lat, lon)

@app.get("/api/cmems/marine-metrics")
def get_cmems_metrics(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate"),
    date: Optional[str] = Query(None, description="Date in format YYYY-MM-DD")
):
    """
    Retrieve oceanographic parameters (Salinity, pH, Chlorophyll, Currents) from Copernicus Marine.
    """
    return fetch_cmems_marine_data(lat, lon, date)

@app.get("/api/ecological-stress", response_model=StressScoreResponse)
def get_ecological_stress(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate")
):
    """
    Perform deep statistical ecosystem mapping and output localized marine environmental stress scores.
    """
    # 1. Fetch NOAA data (SST, Anomaly, DHW)
    noaa_res = fetch_noaa_sst_data(lat, lon)
    sst = noaa_res.get("sst_celsius", 25.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    
    # 2. Fetch CMEMS data (Salinity, Chlorophyll, pH, Currents)
    cmems_res = fetch_cmems_marine_data(lat, lon)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
    ph = cmems_res.get("ph", 8.1)
    current_speed = cmems_res.get("current_velocity_ms", 0.15)
    current_dir = cmems_res.get("current_direction_deg", 0.0)
    
    # 3. Calculate Consolidated Stress
    stress_analysis = calculate_marine_stress(
        sst=sst,
        hotspot=hotspot,
        dhw=dhw,
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
    scientific_name: str = Query(..., description="Scientific name of species to evaluate"),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0)
):
    """
    Assess species habitat sustainability under current environmental metrics at a coordinate.
    """
    # Fetch ambient environment
    noaa_res = fetch_noaa_sst_data(lat, lon)
    cmems_res = fetch_cmems_marine_data(lat, lon)
    
    current_env = {
        "sst_celsius": noaa_res.get("sst_celsius"),
        "ph": cmems_res.get("ph"),
        "salinity_psu": cmems_res.get("salinity_psu")
    }
    
    analysis = analyze_habitat_suitability(scientific_name, current_env)
    return {
        "coordinates": {"latitude": lat, "longitude": lon},
        "environmental_metrics": current_env,
        "suitability_analysis": analysis
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main.py:app", host=host, port=port, reload=True)
