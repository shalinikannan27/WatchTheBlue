import os
import math
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

try:
    import copernicusmarine
    import xarray as xr
    CMEMS_AVAILABLE = True
except ImportError:
    CMEMS_AVAILABLE = False

load_dotenv()
CMEMS_USERNAME = os.getenv("CMEMS_USERNAME", "")
CMEMS_PASSWORD = os.getenv("CMEMS_PASSWORD", "")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from io_zones import zone_for_point
except ImportError:
    def zone_for_point(lat, lon):
        return {"id": "unknown", "name": "Unknown"}

logger = logging.getLogger("drift_model")

def backward_drift(strand_lat: float, strand_lon: float, strand_date: str, hours: int = 72) -> Dict[str, Any]:
    """
    Backward drift simulation — traces where a stranded animal came from.
    """
    try:
        # Handle both date-only and isoformat
        if "T" in strand_date:
            end_date = datetime.fromisoformat(strand_date.replace("Z", "+00:00")).replace(tzinfo=None)
        else:
            end_date = datetime.strptime(strand_date, "%Y-%m-%d")
    except ValueError:
        # Fallback to current time if unparseable
        end_date = datetime.now(timezone.utc)

    start_date = end_date - timedelta(hours=hours)

    start_dt_str = start_date.strftime("%Y-%m-%dT00:00:00")
    end_dt_str = end_date.strftime("%Y-%m-%dT23:59:59")

    if not CMEMS_USERNAME or not CMEMS_PASSWORD or not CMEMS_AVAILABLE:
        logger.warning("CMEMS not available or no credentials, using fallback simulated drift.")
        return _fallback_drift(strand_lat, strand_lon, hours)

    try:
        ds = copernicusmarine.subset(
            dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
            variables=["uo", "vo"],
            minimum_longitude=strand_lon - 3.0,
            maximum_longitude=strand_lon + 3.0,
            minimum_latitude=strand_lat - 3.0,
            maximum_latitude=strand_lat + 3.0,
            start_datetime=start_dt_str,
            end_datetime=end_dt_str,
            username=CMEMS_USERNAME,
            password=CMEMS_PASSWORD,
            force_download=True
        )

        if "depth" in ds.dims:
            ds = ds.isel(depth=0)
        elif "elevation" in ds.dims:
            ds = ds.isel(elevation=0)

        # Force load into memory to avoid multiple disk reads
        ds = ds.load()

        dt_hours = 1

        def get_uv(curr_lat, curr_lon, dt_offset_hours):
            target_time = end_date - timedelta(hours=dt_offset_hours)
            try:
                pt = ds.sel(time=target_time, latitude=curr_lat, longitude=curr_lon, method="nearest")
                u = float(pt["uo"].values)
                v = float(pt["vo"].values)
                if math.isnan(u) or math.isnan(v):
                    return 0.0, 0.0
                return u, v
            except Exception:
                return 0.0, 0.0

        def simulate_path(start_lat, start_lon):
            path = [{"lat": float(start_lat), "lon": float(start_lon), "hour": 0}]
            curr_lat, curr_lon = start_lat, start_lon

            for t in range(1, hours + 1):
                u, v = get_uv(curr_lat, curr_lon, t - 1)
                
                lat_rad = math.radians(curr_lat)
                # Ensure we don't divide by zero at poles, though unlikely in Indian Ocean
                cos_lat = max(abs(math.cos(lat_rad)), 1e-5) * (1 if math.cos(lat_rad) > 0 else -1)

                # lat = lat - (v * dt_hours * 3600) / 111000
                # lon = lon - (u * dt_hours * 3600) / (111000 * cos(lat))
                curr_lat = curr_lat - (v * dt_hours * 3600.0) / 111000.0
                curr_lon = curr_lon - (u * dt_hours * 3600.0) / (111000.0 * cos_lat)

                path.append({
                    "lat": round(float(curr_lat), 4),
                    "lon": round(float(curr_lon), 4),
                    "hour": t
                })
            return path

        main_path = simulate_path(strand_lat, strand_lon)

        offsets = [
            (0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1),
            (0.07, 0.07), (-0.07, 0.07), (0.07, -0.07), (-0.07, -0.07)
        ]

        uncertainty_cone = []
        for dlat, dlon in offsets:
            cone_path = simulate_path(strand_lat + dlat, strand_lon + dlon)
            uncertainty_cone.append([{"lat": p["lat"], "lon": p["lon"]} for p in cone_path])

        origin_est = {"lat": main_path[-1]["lat"], "lon": main_path[-1]["lon"]}
        
        zone_info = zone_for_point(origin_est["lat"], origin_est["lon"])
        origin_zone = zone_info.get("name", "Unknown Zone")

        return {
            "origin_estimate": origin_est,
            "drift_path": main_path,
            "uncertainty_cone": uncertainty_cone,
            "origin_zone": origin_zone
        }

    except Exception as e:
        logger.error(f"backward_drift failed: {e}")
        return _fallback_drift(strand_lat, strand_lon, hours)

def _fallback_drift(strand_lat: float, strand_lon: float, hours: int) -> Dict[str, Any]:
    """Fallback simulation to ensure the app doesn't crash when CMEMS is down."""
    import random
    
    dt_hours = 1
    def simulate_path(start_lat, start_lon):
        path = [{"lat": float(start_lat), "lon": float(start_lon), "hour": 0}]
        curr_lat, curr_lon = start_lat, start_lon
        for t in range(1, hours + 1):
            # Realistic average Indian Ocean current
            u = 0.2 + random.uniform(-0.1, 0.1)
            v = 0.1 + random.uniform(-0.1, 0.1)
            
            lat_rad = math.radians(curr_lat)
            cos_lat = max(abs(math.cos(lat_rad)), 1e-5) * (1 if math.cos(lat_rad) > 0 else -1)
            
            curr_lat = curr_lat - (v * dt_hours * 3600.0) / 111000.0
            curr_lon = curr_lon - (u * dt_hours * 3600.0) / (111000.0 * cos_lat)
            
            path.append({
                "lat": round(float(curr_lat), 4),
                "lon": round(float(curr_lon), 4),
                "hour": t
            })
        return path

    main_path = simulate_path(strand_lat, strand_lon)
    
    offsets = [
        (0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1),
        (0.07, 0.07), (-0.07, 0.07), (0.07, -0.07), (-0.07, -0.07)
    ]
    
    uncertainty_cone = []
    for dlat, dlon in offsets:
        cone_path = simulate_path(strand_lat + dlat, strand_lon + dlon)
        uncertainty_cone.append([{"lat": p["lat"], "lon": p["lon"]} for p in cone_path])

    origin_est = {"lat": main_path[-1]["lat"], "lon": main_path[-1]["lon"]}
    zone_info = zone_for_point(origin_est["lat"], origin_est["lon"])
    origin_zone = zone_info.get("name", "Unknown Zone")

    return {
        "origin_estimate": origin_est,
        "drift_path": main_path,
        "uncertainty_cone": uncertainty_cone,
        "origin_zone": origin_zone
    }
