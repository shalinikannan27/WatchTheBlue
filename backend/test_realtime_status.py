
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, ".")

from noaa_fetch import fetch_noaa_with_fallback
from cmems_fetch import fetch_cmems_with_fallback
from obis_fetch import get_species_by_location
from io_zones import IO_ZONES

def test_realtime_data_fetching():
    print(f"\n{'='*80}")
    print(f"REAL-TIME DATA FETCHING STATUS TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    locations = IO_ZONES
    
    results = []
    
    for zone in locations:
        zone_id = zone['id']
        zone_name = zone['name']
        lat, lon = zone['center']
        
        print(f"\n>>> Testing Location: {zone_name} ({lat}, {lon})")
        
        # 1. Test NOAA Fetching
        print("  Checking NOAA SST...")
        try:
            noaa_data = fetch_noaa_with_fallback(lat, lon)
            noaa_source = noaa_data.get("source", "Unknown")
            is_noaa_real = "Real" in noaa_source
            print(f"    - Source: {noaa_source}")
            print(f"    - Status: {'[REAL]' if is_noaa_real else '[SIMULATED]'}")
        except Exception as e:
            print(f"    - Error: {e}")
            is_noaa_real = False
            noaa_source = f"Error: {e}"
            
        # 2. Test CMEMS Fetching
        print("  Checking CMEMS Marine Metrics...")
        try:
            cmems_data = fetch_cmems_with_fallback(lat, lon)
            cmems_source = cmems_data.get("source", "Unknown")
            is_cmems_real = "Real" in cmems_source
            print(f"    - Source: {cmems_source}")
            print(f"    - Status: {'[REAL]' if is_cmems_real else '[SIMULATED]'}")
        except Exception as e:
            print(f"    - Error: {e}")
            is_cmems_real = False
            cmems_source = f"Error: {e}"
            
        # 3. Test OBIS Fetching
        print("  Checking OBIS Species Data...")
        try:
            obis_data = get_species_by_location(lat, lon, limit=5)
            obis_source = obis_data.get("source", "Unknown")
            is_obis_real = "Real" in obis_source
            print(f"    - Source: {obis_source}")
            print(f"    - Status: {'[REAL]' if is_obis_real else '[SIMULATED]'}")
        except Exception as e:
            print(f"    - Error: {e}")
            is_obis_real = False
            obis_source = f"Error: {e}"
            
        results.append({
            "zone": zone_name,
            "noaa": is_noaa_real,
            "cmems": is_cmems_real,
            "obis": is_obis_real
        })

    print(f"\n\n{'='*80}")
    print(f"{'Location':<25} | {'NOAA (SST)':<12} | {'CMEMS':<12} | {'OBIS':<12}")
    print(f"{'-'*80}")
    for res in results:
        noaa_status = "REAL" if res['noaa'] else "SIMULATED"
        cmems_status = "REAL" if res['cmems'] else "SIMULATED"
        obis_status = "REAL" if res['obis'] else "SIMULATED"
        print(f"{res['zone']:<25} | {noaa_status:<12} | {cmems_status:<12} | {obis_status:<12}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_realtime_data_fetching()
