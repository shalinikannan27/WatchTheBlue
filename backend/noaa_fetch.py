import os
import logging
import requests
from typing import Dict, Any, Optional
  
# Set up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("noaa_fetch")

NOAA_TOKEN = os.getenv("NOAA_API_TOKEN", "")

# NOAA Coral Reef Watch (CRW) data is often queried via the coastwatch or pacioos ERDDAP servers.
# Alternatively, NOAA has regional virtual stations. Let's provide a robust fetcher for ERDDAP griddap 
# or a simple fallback for specific coordinates to get Sea Surface Temperature (SST) and Hotspot metrics.
ERDDAP_BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"

def fetch_noaa_sst_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch Sea Surface Temperature (SST) and anomalies for a given coordinate 
    using NOAA's CoastWatch ERDDAP service or falling back to a structured 
    environmental query if unavailable.
    """
    # For a given lat/lon, we can query NOAA's Coral Reef Watch 5km daily product.
    # Dataset ID: NOAA_DHW_5km (Degree Heating Weeks)
    # We will construct a lightweight request to get local satellite data.
    # As ERDDAP queries can be complex, we provide a clean interface and robust mock fallbacks if the server is unreachable.
    
    url = f"{ERDDAP_BASE_URL}/jplMURSST41.json"  # Multi-scale Ultra-high Resolution (MUR) SST Analysis
    
    # We will query the nearest grid point for the most recent day.
    params = {
        "analysed_sst[(last)][({lat})][({lon})]": ""
    }
    
    try:
        logger.info(f"Fetching NOAA SST data for lat: {lat}, lon: {lon}")
        # NOAA coastwatch ERDDAP can be slow or blocked, so we set a tight timeout of 8 seconds
        response = requests.get(url, params=params, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            # Extract sst from ERDDAP json structure
            try:
                # Structure: table -> rows
                rows = data.get("table", {}).get("rows", [])
                if rows:
                    time_str = rows[0][0]
                    sst_kelvin = rows[0][1]
                    sst_celsius = sst_kelvin - 273.15
                    return {
                        "status": "success",
                        "latitude": lat,
                        "longitude": lon,
                        "sst_celsius": round(sst_celsius, 2),
                        "time": time_str,
                        "source": "NOAA MUR SST"
                    }
            except Exception as parse_err:
                logger.warning(f"Error parsing NOAA response: {parse_err}. Using intelligent simulation.")
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"NOAA ERDDAP request failed ({e}). Generating simulated NOAA environmental values.")
    
    # Intelligent simulation based on Latitude (warmer near equator)
    # Equatorial regions (latitude near 0) have higher SST around 28-30C.
    # Polar regions (latitude near 90) are close to 0C.
    import math
    base_temp = 28.0 - (abs(lat) * 0.3)  # simple linear gradient
    # Add minor seasonal variance based on lat/lon
    seasonal_offset = 2.0 * math.sin(lon / 57.29) 
    simulated_sst = max(-1.8, min(34.0, base_temp + seasonal_offset))
    
    # Calculate degree heating weeks (DHW) / hotspots mockup
    # Usually SST above climatological maximum (e.g. 28C) leads to thermal stress
    climatology_max = 28.0 - (abs(lat) * 0.28)
    hotspot = max(0.0, simulated_sst - climatology_max)
    dhw = hotspot * 1.5 if hotspot > 0 else 0.0 # simple simulated accumulative stress
    
    return {
        "status": "simulated",
        "latitude": lat,
        "longitude": lon,
        "sst_celsius": round(simulated_sst, 2),
        "hotspot_anomaly": round(hotspot, 2),
        "degree_heating_weeks": round(dhw, 2),
        "source": "NOAA Satellite Climate Model (Simulated)"
    }

def fetch_noaa_cdo_weather(station_id: str) -> Dict[str, Any]:
    """
    Fetch weather or climate data from NOAA Climate Data Online (CDO).
    Requires a valid NOAA_API_TOKEN in the environment.
    """
    if not NOAA_TOKEN:
        logger.warning("NOAA_API_TOKEN is not set. Cannot query CDO API.")
        return {"error": "NOAA_API_TOKEN not configured"}
        
    url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": NOAA_TOKEN}
    params = {
        "datasetid": "GHCND", # Global Historical Climatology Network daily
        "stationid": station_id,
        "limit": 10
    }
    
    try:
        logger.info(f"Fetching NOAA CDO weather for station: {station_id}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching NOAA CDO: {e}")
        return {"error": str(e)}
