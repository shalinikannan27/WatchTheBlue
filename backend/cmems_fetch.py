"""
CMEMS (Copernicus Marine Environmental Monitoring Service) integration.

Fetches real ocean condition data (Temperature, Oxygen, Salinity, pH)
from the official CMEMS API.

Falls back to realistic simulation if API fails, ensuring the application
never breaks even if CMEMS is temporarily unavailable.
"""

import os
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Try to import CMEMS library, gracefully degrade if not available
try:
    import copernicusmarine
    CMEMS_AVAILABLE = True
except ImportError:
    CMEMS_AVAILABLE = False
    logging.warning("copernicusmarine not installed. Falling back to simulation.")

try:
    import xarray as xr
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cmems_fetch")

load_dotenv()

CMEMS_USERNAME = os.getenv("CMEMS_USERNAME", "")
CMEMS_PASSWORD = os.getenv("CMEMS_PASSWORD", "")


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


def fetch_cmems_marine_data(
    lat: float,
    lon: float,
    date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch REAL marine condition data from CMEMS API.
    
    Retrieves:
    - Temperature (°C)
    - Oxygen (mol/m³)
    - Salinity (PSU)
    - pH
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        date_str: Optional date in format YYYY-MM-DD
        
    Returns:
        dict: Marine metrics from CMEMS
        
    Raises:
        ValueError: If coordinates are invalid
    """
    validate_coordinates(lat, lon)
    
    # If credentials not set, raise error (don't fall back here)
    if not CMEMS_USERNAME or not CMEMS_PASSWORD:
        raise ValueError(
            "CMEMS credentials not configured. "
            "Set CMEMS_USERNAME and CMEMS_PASSWORD in .env file"
        )
    
    if not CMEMS_AVAILABLE:
        raise ImportError(
            "copernicusmarine library not installed. "
            "Run: pip install copernicusmarine"
        )
    
    try:
        logger.info(
            f"Fetching CMEMS data for Lat={lat}, Lon={lon}, Date={date_str}"
        )
        
        # Use CMEMS Global Physical Analysis and Forecast model
        # Daily data at 0.083° resolution (~9 km)
        dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_P1D-m"
        
        # Set date range
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            # Use yesterday's data (CMEMS has ~1 day latency)
            target_date = datetime.now() - timedelta(days=1)
            date_str = target_date.strftime("%Y-%m-%d")
        
        start_datetime = f"{date_str}T00:00:00"
        end_datetime = f"{date_str}T23:59:59"
        
        # Fetch data from CMEMS
        dataset = copernicusmarine.subset(
            dataset_id=dataset_id,
            variables=[
                "thetao",  # Temperature (K, will convert to °C)
                "so",      # Salinity (PSU)
                "o2"       # Oxygen (mol/m³)
            ],
            minimum_longitude=lon,
            maximum_longitude=lon,
            minimum_latitude=lat,
            maximum_latitude=lat,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            username=CMEMS_USERNAME,
            password=CMEMS_PASSWORD
        )
        
        # Parse the NetCDF dataset
        if XARRAY_AVAILABLE and hasattr(dataset, 'data_vars'):
            # Using xarray Dataset
            data = _parse_xarray_data(dataset, lat, lon)
        else:
            # Fallback to raw NetCDF parsing
            data = _parse_netcdf_data(dataset, lat, lon)
        
        # Add metadata
        data["source"] = "Copernicus Marine (CMEMS) Real API"
        data["coordinates"] = {"latitude": lat, "longitude": lon}
        data["timestamp"] = datetime.now().isoformat()
        data["data_date"] = date_str
        
        logger.info(f"Successfully fetched CMEMS data: {data}")
        return data
        
    except Exception as e:
        logger.error(f"CMEMS API error: {str(e)}")
        raise


def _parse_xarray_data(dataset, lat: float, lon: float) -> Dict[str, Any]:
    """
    Parse xarray Dataset from CMEMS.
    
    Args:
        dataset: xarray Dataset
        lat: Target latitude
        lon: Target longitude
        
    Returns:
        dict: Extracted ocean conditions
    """
    try:
        # Extract values at the nearest grid point
        data_nearest = dataset.sel(latitude=lat, longitude=lon, method="nearest")
        
        # Get first (and usually only) time step
        if "time" in data_nearest.dims:
            data_at_time = data_nearest.isel(time=0)
        else:
            data_at_time = data_nearest
        
        # Extract variables with proper unit conversions
        temperature_k = float(data_at_time["thetao"].values)
        temperature_c = temperature_k - 273.15  # Convert Kelvin to Celsius
        
        salinity = float(data_at_time["so"].values)
        oxygen = float(data_at_time["o2"].values)
        
        return {
            "temperature_celsius": round(temperature_c, 2),
            "salinity_psu": round(salinity, 2),
            "oxygen_mol_m3": round(oxygen, 2),
            "ph": None  # Not available in most CMEMS global datasets
        }
        
    except Exception as e:
        logger.error(f"Error parsing xarray data: {str(e)}")
        raise


def _parse_netcdf_data(dataset, lat: float, lon: float) -> Dict[str, Any]:
    """
    Parse raw NetCDF data from CMEMS.
    
    Args:
        dataset: NetCDF file path or dataset
        lat: Target latitude
        lon: Target longitude
        
    Returns:
        dict: Extracted ocean conditions
    """
    try:
        # If dataset is a file path (string), open it
        if isinstance(dataset, str):
            import netCDF4
            nc = netCDF4.Dataset(dataset, 'r')
        else:
            nc = dataset
        
        # Find nearest grid point
        lats = nc.variables['latitude'][:]
        lons = nc.variables['longitude'][:]
        
        # Find closest indices
        lat_idx = (abs(lats - lat)).argmin()
        lon_idx = (abs(lons - lon)).argmin()
        
        # Extract variables
        temperature_k = float(nc.variables['thetao'][0, 0, lat_idx, lon_idx])
        temperature_c = temperature_k - 273.15
        
        salinity = float(nc.variables['so'][0, 0, lat_idx, lon_idx])
        oxygen = float(nc.variables['o2'][0, 0, lat_idx, lon_idx])
        
        if isinstance(dataset, str):
            nc.close()
        
        return {
            "temperature_celsius": round(temperature_c, 2),
            "salinity_psu": round(salinity, 2),
            "oxygen_mol_m3": round(oxygen, 2),
            "ph": None
        }
        
    except Exception as e:
        logger.error(f"Error parsing NetCDF data: {str(e)}")
        raise


def fetch_cmems_with_fallback(
    lat: float,
    lon: float,
    date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch CMEMS data with graceful fallback to simulation.
    
    Tries to get REAL data from CMEMS API first.
    If API fails (network error, invalid credentials, timeout),
    falls back to realistic oceanographic simulation.
    
    This ensures the application never breaks, even if CMEMS is unavailable.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        date_str: Optional date in format YYYY-MM-DD
        
    Returns:
        dict: Marine metrics (real or simulated)
    """
    try:
        return fetch_cmems_marine_data(lat, lon, date_str)
    except Exception as e:
        logger.warning(
            f"CMEMS API unavailable ({type(e).__name__}: {str(e)}). "
            "Using simulated oceanographic data."
        )
        return _simulate_ocean_conditions(lat, lon, date_str)


def _simulate_ocean_conditions(
    lat: float,
    lon: float,
    date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate realistic oceanographic simulation as fallback.
    
    Uses physics-based geospatial modeling to predict ocean conditions
    when real API data is unavailable.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        date_str: Optional date
        
    Returns:
        dict: Simulated ocean conditions
    """
    validate_coordinates(lat, lon)
    
    logger.info(f"Simulating ocean conditions for Lat={lat}, Lon={lon}")
    
    abs_lat = abs(lat)
    
    # TEMPERATURE SIMULATION (°C)
    # Equator: warm, Poles: cold, Depth increases cooling
    if abs_lat < 10:
        base_temp = 26.0 + (2.0 * math.sin(lon / 30.0))  # Equatorial
    elif 10 <= abs_lat < 30:
        base_temp = 20.0 + (3.0 * math.sin(lon / 20.0))  # Tropical
    elif 30 <= abs_lat < 45:
        base_temp = 12.0 + (2.0 * math.sin(lon / 25.0))  # Temperate
    else:
        base_temp = 5.0 - (2.0 * math.sin(lon / 15.0))   # Polar
    
    temperature = base_temp + (0.5 * math.cos(lat / 20.0))
    temperature = max(-2.0, min(40.0, temperature))
    
    # SALINITY SIMULATION (PSU)
    if abs_lat < 10:
        base_salinity = 34.2  # Equatorial (high precipitation)
    elif 15 <= abs_lat <= 30:
        base_salinity = 36.5  # Subtropical (high evaporation)
    else:
        base_salinity = 33.8  # Temperate/Polar
    
    # Estuary/river discharge effects
    if (5 < lat < 10 and -60 < lon < -45):  # Amazon
        base_salinity -= 4.0
    elif (10 < lat < 22 and 80 < lon < 95):  # Bay of Bengal
        base_salinity -= 2.0
    elif (54 < lat < 66 and 15 < lon < 30):  # Baltic Sea
        base_salinity -= 3.0
    
    salinity = base_salinity + (0.5 * math.cos(lon / 10.0))
    salinity = max(5.0, min(41.0, salinity))
    
    # OXYGEN SIMULATION (mol/m³)
    # Oxygen varies with temperature (cold = more oxygen) and productivity
    base_oxygen = 250.0 - (temperature * 3.0)  # Inverse temperature relationship
    
    # Productivity zones (upwelling, etc) have less O2 at depth
    is_coastal_upwelling = (30 < abs_lat < 45) and (lon < -115 or -20 < lon < -10)
    if is_coastal_upwelling:
        base_oxygen -= 40.0  # Upwelling zones have hypoxic waters
    
    oxygen = base_oxygen + (30.0 * math.sin(lat / 15.0))
    oxygen = max(0.0, min(400.0, oxygen))
    
    # pH SIMULATION
    # Modern surface ocean: ~8.1 (was 8.2 pre-industrial)
    # Cold waters: slightly higher pH
    # Upwelling: lower pH (deep water is more acidic)
    base_ph = 8.11 - (temperature * 0.01)  # Slight warming effect
    
    if is_coastal_upwelling:
        base_ph -= 0.15  # Upwelled water is more acidic
    if salinity < 30:
        base_ph -= 0.08  # Freshwater is less buffered
    
    ph = base_ph + (0.02 * math.sin(lat / 10.0))
    ph = max(7.5, min(8.3, ph))
    
    return {
        "temperature_celsius": round(temperature, 2),
        "salinity_psu": round(salinity, 2),
        "oxygen_mol_m3": round(oxygen, 2),
        "ph": round(ph, 3),
        "source": "Simulated Oceanographic Model (CMEMS API unavailable)",
        "coordinates": {"latitude": lat, "longitude": lon},
        "timestamp": datetime.now().isoformat(),
        "data_date": date_str or datetime.now().strftime("%Y-%m-%d"),
        "note": "Using realistic simulation. Real CMEMS data not available."
    }
