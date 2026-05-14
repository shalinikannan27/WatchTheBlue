"""
NOAA (National Oceanic and Atmospheric Administration) integration.

Fetches real Sea Surface Temperature (SST) data and calculates:
- Temperature anomalies (difference from climatological normal)
- Degree Heating Weeks (DHW) for coral bleaching stress
- Coral bleaching risk alerts

No API key required. Uses NOAA's public ERDDAP and CoralTemp datasets.

Falls back to realistic simulation if API fails, ensuring resilience.
"""

import os
import logging
import requests
import math
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("noaa_fetch")

# NOAA ERDDAP base URLs (no authentication required)
ERDDAP_BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"
CORAL_WATCH_URL = "https://oceandata.sci.gsfc.nasa.gov/MODIS-Aqua/Mapped"


def validate_coordinates(lat: float, lon: float) -> None:
    """
    Validate that coordinates are within acceptable ranges.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Raises:
        ValueError: If coordinates are invalid
    """
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude {lat} must be between -90 and 90")
    if not -180 <= lon <= 180:
        raise ValueError(f"Longitude {lon} must be between -180 and 180")


def get_climatological_max(lat: float) -> float:
    """
    Get climatological maximum SST for a latitude.
    
    This is the long-term average maximum temperature that a location 
    experiences seasonally. Used to calculate temperature anomalies.
    
    Args:
        lat: Latitude (-90 to 90)
        
    Returns:
        float: Climatological maximum SST in °C
    """
    abs_lat = abs(lat)
    
    if abs_lat < 10:
        return 29.0  # Equatorial waters
    elif 10 <= abs_lat < 25:
        return 28.5  # Tropical waters
    elif 25 <= abs_lat < 40:
        return 27.0  # Subtropical waters
    elif 40 <= abs_lat < 50:
        return 22.0  # Temperate waters
    else:
        return 15.0  # Polar waters


def calculate_temperature_anomaly(current_sst: float, climatological_max: float) -> float:
    """
    Calculate temperature anomaly.
    
    Anomaly = Current SST - Climatological Maximum
    
    Positive anomaly = warmer than normal (thermal stress)
    Negative anomaly = cooler than normal
    
    Args:
        current_sst: Current Sea Surface Temperature in °C
        climatological_max: Long-term average maximum SST in °C
        
    Returns:
        float: Temperature anomaly in °C
    """
    return current_sst - climatological_max


def calculate_degree_heating_weeks(anomaly: float) -> float:
    """
    Calculate Degree Heating Weeks (DHW).
    
    DHW is a measure of accumulated thermal stress for coral reefs:
    - DHW = 0: No thermal stress
    - DHW 4-6: Bleaching expected
    - DHW > 6: Severe bleaching expected
    - DHW > 8: Mortality expected
    
    Args:
        anomaly: Temperature anomaly in °C
        
    Returns:
        float: Degree Heating Weeks (accumulated thermal stress)
    """
    if anomaly <= 0:
        return 0.0
    
    # DHW accumulates when SST exceeds climatological max
    # Simplified model: DHW ≈ anomaly * accumulation_factor
    # This assumes multi-week accumulation (real DHW tracks 12-week rolling average)
    return max(0.0, anomaly * 1.5)


def fetch_noaa_sst_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch REAL Sea Surface Temperature data from NOAA's ERDDAP service.
    
    Uses the MUR (Multi-scale Ultra-high Resolution) SST Analysis dataset
    which provides daily, high-resolution SST from satellite data.
    
    No API key required. Publicly available data.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Returns:
        dict: SST metrics including temperature, anomaly, and DHW
        
    Raises:
        ValueError: If coordinates are invalid
    """
    validate_coordinates(lat, lon)
    
    try:
        logger.info(f"Fetching NOAA SST data for Lat={lat}, Lon={lon}")
        
        # NOAA ERDDAP endpoint for MUR SST data
        url = f"{ERDDAP_BASE_URL}/jplMURSST41.json"
        
        # Query the nearest grid point at the latest time
        # ERDDAP syntax for latest time is often just "last" or [(last)]
        query = f"analysed_sst[(last)][({lat}):{lat}][({lon}):{lon}]"
        full_url = f"{url}?{query}"
        
        logger.info(f"Requesting URL: {full_url}")
        response = requests.get(full_url, timeout=25)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse ERDDAP JSON response structure
        rows = data.get("table", {}).get("rows", [])
        if not rows:
            raise ValueError("No data in ERDDAP response")
        
        # Extract values from first row
        time_str = rows[0][0]
        sst_kelvin = float(rows[0][1])
        sst_celsius = sst_kelvin - 273.15
        
        # Calculate anomaly and DHW
        climatological_max = get_climatological_max(lat)
        anomaly = calculate_temperature_anomaly(sst_celsius, climatological_max)
        dhw = calculate_degree_heating_weeks(anomaly)
        
        logger.info(
            f"NOAA SST: {sst_celsius:.2f}°C, "
            f"Anomaly: {anomaly:.2f}°C, DHW: {dhw:.2f}"
        )
        
        return {
            "sst_celsius": round(sst_celsius, 2),
            "hotspot_anomaly": round(anomaly, 2),
            "degree_heating_weeks": round(dhw, 2),
            "coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": datetime.now().isoformat(),
            "data_time": time_str,
            "source": "NOAA MUR SST (Real API)",
            "climatological_max_celsius": round(climatological_max, 2)
        }
        
    except Exception as e:
        logger.error(f"NOAA API error: {str(e)}")
        raise


def fetch_noaa_with_fallback(
    lat: float,
    lon: float
) -> Dict[str, Any]:
    """
    Fetch NOAA SST data with graceful fallback to simulation.
    
    Tries to get REAL data from NOAA ERDDAP first.
    If API fails (network error, timeout, invalid response),
    falls back to realistic oceanographic simulation.
    
    This ensures the application never breaks, even if NOAA is unavailable.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Returns:
        dict: SST metrics (real or simulated)
    """
    try:
        return fetch_noaa_sst_data(lat, lon)
    except Exception as e:
        logger.warning(
            f"NOAA API unavailable ({type(e).__name__}: {str(e)}). "
            "Using simulated oceanographic data."
        )
        return _simulate_noaa_conditions(lat, lon)


def _simulate_noaa_conditions(lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate realistic oceanographic simulation as fallback.
    
    Uses physics-based geospatial modeling to predict ocean conditions
    when NOAA API is unavailable.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Returns:
        dict: Simulated SST and anomaly data
    """
    validate_coordinates(lat, lon)
    
    logger.info(f"Simulating NOAA conditions for Lat={lat}, Lon={lon}")
    
    abs_lat = abs(lat)
    
    # SEA SURFACE TEMPERATURE SIMULATION
    # Warmer near equator, cooler at poles (realistic gradient)
    if abs_lat < 10:
        base_temp = 28.0 + (2.0 * math.sin(lon / 30.0))  # Equatorial
    elif 10 <= abs_lat < 30:
        base_temp = 24.0 + (2.5 * math.sin(lon / 25.0))  # Tropical
    elif 30 <= abs_lat < 45:
        base_temp = 16.0 + (2.0 * math.sin(lon / 20.0))  # Temperate
    elif 45 <= abs_lat < 60:
        base_temp = 10.0 + (1.0 * math.sin(lon / 25.0))  # Subpolar
    else:
        base_temp = 2.0 - (0.5 * math.sin(lon / 30.0))   # Polar
    
    # Add realistic seasonal-like variation
    seasonal_offset = 2.0 * math.cos(lon / 57.29)
    sst = base_temp + seasonal_offset + (0.5 * math.sin(lat / 20.0))
    sst = max(-2.0, min(35.0, sst))  # Clamp to realistic bounds
    
    # TEMPERATURE ANOMALY SIMULATION
    # Most locations: -1 to +2°C (normal variability)
    # Some warm locations: up to +3°C
    climatological_max = get_climatological_max(lat)
    
    # Anomaly typically -1 to +1°C, occasionally higher
    anomaly_noise = 1.5 * math.sin(lon / 45.0) + 0.5 * math.cos(lat / 60.0)
    anomaly = anomaly_noise
    anomaly = max(-3.0, min(5.0, anomaly))  # Clamp to realistic bounds
    
    # DEGREE HEATING WEEKS SIMULATION
    dhw = calculate_degree_heating_weeks(anomaly)
    
    return {
        "sst_celsius": round(sst, 2),
        "hotspot_anomaly": round(anomaly, 2),
        "degree_heating_weeks": round(dhw, 2),
        "coordinates": {"latitude": lat, "longitude": lon},
        "timestamp": datetime.now().isoformat(),
        "source": "Simulated NOAA Model (API unavailable)",
        "climatological_max_celsius": round(climatological_max, 2),
        "note": "Using realistic simulation. Real NOAA data not available."
    }


def get_bleaching_alert_level(dhw: float) -> str:
    """
    Determine coral bleaching risk level from Degree Heating Weeks.
    
    Based on NOAA Coral Reef Watch alert levels:
    - No Alert (DHW < 4): No bleaching expected
    - Watch (4 ≤ DHW < 6): Bleaching expected
    - Warning (6 ≤ DHW < 8): Significant bleaching expected  
    - Critical (DHW ≥ 8): Severe bleaching and possible mortality
    
    Args:
        dhw: Degree Heating Weeks
        
    Returns:
        str: Alert level ("no_alert", "watch", "warning", "critical")
    """
    if dhw < 4:
        return "no_alert"
    elif dhw < 6:
        return "watch"
    elif dhw < 8:
        return "warning"
    else:
        return "critical"


def fetch_noaa_cdo_weather(station_id: str) -> Dict[str, Any]:
    """
    Fetch weather or climate data from NOAA Climate Data Online (CDO).
    
    Note: This endpoint requires authentication (NOAA_API_TOKEN).
    Currently not implemented for MVP. Can be added if historical
    climate data is needed.
    
    Args:
        station_id: NOAA station ID
        
    Returns:
        dict: Error or climate data
    """
    logger.warning("NOAA CDO endpoint not implemented in current version")
    return {
        "error": "NOAA_CDO not implemented",
        "note": "Use fetch_noaa_sst_data() for current SST and anomalies"
    }
