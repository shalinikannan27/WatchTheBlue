"""
Integration test to verify endpoint responses before deploying server.
Tests the stress scoring and species vulnerability integration.
"""

import sys
sys.path.insert(0, ".")

from noaa_fetch import fetch_noaa_with_fallback, get_bleaching_alert_level
from cmems_fetch import fetch_cmems_with_fallback
from obis_fetch import get_species_by_location
from stress_score import calculate_marine_stress, get_species_stress_impact

def test_ecological_stress_endpoint():
    """Test /api/ecological-stress endpoint logic"""
    print("\n=== Testing /api/ecological-stress ===")
    
    lat, lon = 10.0, 100.0
    
    # Fetch NOAA data
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    sst = noaa_res.get("sst_celsius", 25.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    
    # Fetch CMEMS data
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
    ph = cmems_res.get("ph", 8.1)
    current_speed = cmems_res.get("current_velocity_ms", 0.15)
    
    # Calculate stress
    stress_analysis = calculate_marine_stress(
        sst=sst,
        hotspot_anomaly=hotspot,
        degree_heating_weeks=dhw,
        ph=ph,
        salinity=salinity,
        chlorophyll=chlorophyll,
        current_speed=current_speed
    )
    
    print(f"Coordinates: ({lat}, {lon})")
    print(f"SST: {sst}°C")
    print(f"Hotspot Anomaly: {hotspot}°C")
    print(f"DHW: {dhw}")
    print(f"pH: {ph}")
    print(f"Stress Score: {stress_analysis.get('overall_stress_score')}")
    print(f"Stress Level: {stress_analysis.get('stress_level')}")
    print(f"Primary Stressors: {stress_analysis.get('contributing_factors')}")
    
    assert stress_analysis.get('overall_stress_score') is not None
    assert stress_analysis.get('stress_level') in ['HEALTHY', 'STRESSED', 'CRITICAL', 'SEVERE']
    print("[OK] /api/ecological-stress logic verified")

def test_habitat_suitability_endpoint():
    """Test /api/species/habitat-suitability endpoint logic"""
    print("\n=== Testing /api/species/habitat-suitability ===")
    
    lat, lon = 10.0, 100.0
    
    # Fetch environment
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    
    sst = noaa_res.get("sst_celsius", 25.0)
    hotspot = noaa_res.get("hotspot_anomaly", 0.0)
    dhw = noaa_res.get("degree_heating_weeks", 0.0)
    salinity = cmems_res.get("salinity_psu", 35.0)
    chlorophyll = cmems_res.get("chlorophyll_mg_m3", 0.1)
    ph = cmems_res.get("ph", 8.1)
    current_speed = cmems_res.get("current_velocity_ms", 0.15)
    
    # Calculate ecosystem stress
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
    
    # Fetch species
    species_data = get_species_by_location(lat, lon)
    species_occurrences = species_data.get("occurrences", [])
    
    print(f"Coordinates: ({lat}, {lon})")
    print(f"Ecosystem Stress Score: {ecosystem_stress_score}")
    print(f"Species Found: {len(species_occurrences)}")
    
    # Test species vulnerability calculation
    if species_occurrences:
        for i, species in enumerate(species_occurrences[:3]):  # Test first 3
            species_name = species.get("scientific_name", "Unknown")
            impact = get_species_stress_impact(species_name, ecosystem_stress_score)
            print(f"\n  Species {i+1}: {species_name}")
            print(f"    Vulnerability: {impact.get('vulnerability')}")
            print(f"    Recommendation: {impact.get('recommendation')}")
            
            assert impact.get('vulnerability') in ['LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'UNKNOWN']
            assert impact.get('recommendation') is not None
    
    print("[OK] /api/species/habitat-suitability logic verified")

def test_response_formats():
    """Verify response structures match endpoint specs"""
    print("\n=== Testing Response Formats ===")
    
    lat, lon = 10.0, 100.0
    
    # Test ecological-stress response
    noaa_res = fetch_noaa_with_fallback(lat, lon)
    cmems_res = fetch_cmems_with_fallback(lat, lon)
    
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
    
    response = {
        "coordinates": {"latitude": lat, "longitude": lon},
        "metrics": {
            "sst_celsius": sst,
            "hotspot_anomaly": hotspot,
            "degree_heating_weeks": dhw,
            "salinity_psu": salinity,
            "chlorophyll_mg_m3": chlorophyll,
            "ph": ph,
            "current_velocity_ms": current_speed,
            "current_direction_deg": 0.0
        },
        "stress_analysis": stress_analysis
    }
    
    # Verify required fields
    assert response["coordinates"]["latitude"] == lat
    assert response["metrics"]["sst_celsius"] is not None
    assert response["stress_analysis"]["overall_stress_score"] is not None
    assert response["stress_analysis"]["stress_level"] is not None
    
    print("[OK] Response format verified (all required fields present)")

if __name__ == "__main__":
    try:
        test_ecological_stress_endpoint()
        test_habitat_suitability_endpoint()
        test_response_formats()
        print("\n" + "="*60)
        print("[OK] All endpoint integration tests passed!")
        print("="*60)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
