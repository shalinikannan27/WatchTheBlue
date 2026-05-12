import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stress_score")

def calculate_marine_stress(
    sst: float,
    hotspot: float,
    dhw: float,
    ph: float,
    salinity: float,
    chlorophyll: float,
    current_speed: float = 0.15
) -> Dict[str, Any]:
    """
    Calculate an integrated marine ecological stress score (0 to 100) based on
    sea surface temperature, thermal anomalies, pH, salinity, chlorophyll, and currents.
    This is highly optimized for assessing coral reef bleaching risks and general habitat degradation.
    
    Args:
        sst (float): Sea Surface Temp in Celsius
        hotspot (float): Hotspot thermal anomaly (SST - maximum climatological monthly mean)
        dhw (float): Degree Heating Weeks (accumulated thermal stress)
        ph (float): Ocean pH level (typically 7.8 - 8.3)
        salinity (float): Salinity in PSU (typically 30 - 38)
        chlorophyll (float): Chlorophyll-a concentration in mg/m3
        current_speed (float): Sea current speed in m/s
        
    Returns:
        dict: Detailed stress score report with sub-component stress levels and recommendation alerts.
    """
    logger.info("Calculating marine stress score...")
    
    # 1. Thermal Stress Component (0 - 100)
    # Based on NOAA's standard definitions: 
    # Hotspot >= 1C is the threshold for bleaching stress.
    # DHW >= 4 leads to significant bleaching, DHW >= 8 leads to widespread bleaching and mortality.
    thermal_stress = 0.0
    if dhw >= 8.0:
        thermal_stress = 100.0
    elif dhw >= 4.0:
        thermal_stress = 75.0 + (dhw - 4.0) * 6.25 # Scale 75 to 100
    elif hotspot >= 1.0:
        thermal_stress = 50.0 + (hotspot - 1.0) * 8.33 # Scale 50 to 75
    else:
        thermal_stress = max(0.0, hotspot * 50.0) # Scale 0 to 50
        
    # 2. Acidification Stress Component (0 - 100)
    # Ocean pH historically 8.2, currently ~8.1.
    # pH < 7.9 causes severe calcification stress. pH < 7.7 is lethal to many reef builders.
    acid_stress = 0.0
    if ph < 8.1:
        # Standardize: 8.1 -> 0 stress, 7.7 -> 100 stress
        acid_stress = min(100.0, max(0.0, (8.1 - ph) / 0.4 * 100.0))
    elif ph > 8.35: # Alkalinity spike (rare but stressful)
        acid_stress = min(100.0, max(0.0, (ph - 8.35) / 0.15 * 100.0))

    # 3. Salinity Stress Component (0 - 100)
    # Reef corals prefer stable salinity of 34-36 psu.
    # Salinity < 30 (extreme rain/runoff) or > 38 causes osmolarity stress.
    salinity_stress = 0.0
    if salinity < 34.0:
        # 34 -> 0 stress, 25 -> 100 stress
        salinity_stress = min(100.0, max(0.0, (34.0 - salinity) / 9.0 * 100.0))
    elif salinity > 36.0:
        # 36 -> 0 stress, 42 -> 100 stress
        salinity_stress = min(100.0, max(0.0, (salinity - 36.0) / 6.0 * 100.0))

    # 4. Eutrophication / Chlorophyll Stress Component (0 - 100)
    # Highly nutrient-rich waters cause algal blooms, shading corals, and hypoxia.
    # Chlorophyll < 0.05 is starving; Chlorophyll > 5.0 is highly eutrophic (algal bloom risk).
    chla_stress = 0.0
    if chlorophyll > 1.0:
        # 1.0 -> 0 stress, 8.0 -> 100 stress
        chla_stress = min(100.0, max(0.0, (chlorophyll - 1.0) / 7.0 * 100.0))
    elif chlorophyll < 0.02:
        chla_stress = 30.0 # moderate starvation stress

    # 5. Stagnation / Hypoxia Risk Component (0 - 100)
    # Low currents (< 0.03 m/s) prevent oxygenation and waste removal.
    # High currents (> 1.5 m/s) can cause mechanical damage.
    current_stress = 0.0
    if current_speed < 0.05:
        current_stress = min(100.0, (0.05 - current_speed) / 0.05 * 80.0)
    elif current_speed > 1.5:
        current_stress = min(100.0, (current_speed - 1.5) / 1.0 * 100.0)

    # Weighted Average Stress Score
    # Thermal is primary driver of modern coral mortality (weight = 0.40)
    # Acidification is chronic threat (weight = 0.25)
    # Salinity and Chlorophyll run-off/eutrophication (weight = 0.15 each)
    # Current velocity/Oxygenation (weight = 0.05)
    weighted_score = (
        (thermal_stress * 0.40) +
        (acid_stress * 0.25) +
        (salinity_stress * 0.15) +
        (chla_stress * 0.15) +
        (current_stress * 0.05)
    )
    
    # Categorization and warning levels
    if weighted_score < 25.0:
        alert_level = "HEALTHY"
        color_code = "#059669" # Green
        description = "This marine region is highly stable. Ideal conditions for marine biodiversity."
    elif weighted_score < 50.0:
        alert_level = "WATCH"
        color_code = "#EAB308" # Yellow
        description = "Mild environmental fluctuations detected. Keep a close watch for accumulating thermal stress."
    elif weighted_score < 75.0:
        alert_level = "ALERT LEVEL 1"
        color_code = "#F97316" # Orange
        description = "High thermal anomaly or acidification stress. Bleaching of sensitive species is likely."
    else:
        alert_level = "ALERT LEVEL 2 (CRITICAL)"
        color_code = "#EF4444" # Red
        description = "Severe thermal stress and severe ocean acidification. High probability of coral bleaching and mortality."

    return {
        "overall_stress_score": round(weighted_score, 1),
        "alert_level": alert_level,
        "color_code": color_code,
        "description": description,
        "stress_breakdown": {
            "thermal_stress": round(thermal_stress, 1),
            "acidification_stress": round(acid_stress, 1),
            "salinity_stress": round(salinity_stress, 1),
            "eutrophication_stress": round(chla_stress, 1),
            "flow_stagnation_stress": round(current_stress, 1)
        }
    }
