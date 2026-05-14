"""
Marine Stress Score Calculation Engine.

Implements the core stress scoring formula:
stress_score = (temp_anomaly × 0.4) + (oxygen_depletion × 0.35) + (ph_drop × 0.25)

Scaled to 0-100 range to provide a unified metric for marine ecosystem health.

Reference Thresholds (Healthy Marine Ecosystems):
- Temperature: 22°C - 30°C (varies by latitude)
- Oxygen (Dissolved): > 5 mg/L
- pH: 8.1 (healthy), < 7.5 indicates severe acidification
- Salinity: ~35 PSU (practical salinity units)
"""

from typing import Dict, Any, List, Tuple, Optional
from species_logic import get_species_profile


# Healthy baseline thresholds for marine ecosystems
HEALTHY_TEMPERATURE = 25.0  # °C (species-dependent, but ~25 is baseline)
HEALTHY_OXYGEN = 5.0  # mg/L (above this is healthy)
HEALTHY_PH = 8.1  # pH units


def normalize_temperature_anomaly(temp_anomaly: float) -> float:
    """
    Normalize temperature anomaly to 0-10 stress component scale.
    
    Parameters:
    - temp_anomaly: Degrees Celsius above healthy baseline
    
    Returns:
    - Component score 0-10 (0 = no stress, 10 = maximum stress)
    
    Formula: Non-linear to reflect that small deviations are tolerable,
    but large deviations cause exponential stress.
    """
    if temp_anomaly <= 0:
        return 0.0
    
    # Each 0.5°C above baseline = ~1 stress unit
    # Plateaus at 10 for extreme conditions
    component = min(10.0, temp_anomaly * 2.0)
    return round(component, 2)


def normalize_oxygen_depletion(oxygen_mg_l: float) -> float:
    """
    Normalize dissolved oxygen level to 0-10 stress component scale.
    
    Parameters:
    - oxygen_mg_l: Dissolved oxygen concentration in mg/L
    
    Returns:
    - Component score 0-10 (0 = no stress, 10 = maximum stress)
    
    Reference:
    - > 5 mg/L: Healthy (no stress)
    - 4-5 mg/L: Moderate stress (some organisms affected)
    - 2-4 mg/L: Severe stress (hypoxia zone)
    - < 1 mg/L: Anoxia (anaerobic conditions)
    """
    if oxygen_mg_l >= HEALTHY_OXYGEN:
        return 0.0
    
    # Depletion below healthy threshold
    depletion = HEALTHY_OXYGEN - oxygen_mg_l
    
    # Non-linear response: depletion < 1 is moderate, < 2 is severe
    if depletion < 1:
        component = depletion * 3.0  # 0-3 for 0-1 mg/L depletion
    elif depletion < 2:
        component = 3.0 + (depletion - 1) * 4.0  # 3-7 for 1-2 mg/L depletion
    else:
        component = min(10.0, 7.0 + (depletion - 2) * 1.5)  # 7-10 for 2+ mg/L
    
    return round(component, 2)


def normalize_ph_drop(current_ph: float) -> float:
    """
    Normalize pH level to 0-10 stress component scale.
    
    Parameters:
    - current_ph: Current ocean pH (typical range 7.5-8.4)
    
    Returns:
    - Component score 0-10 (0 = no stress, 10 = maximum stress)
    
    Reference (Ocean Acidification):
    - 8.1: Healthy baseline
    - 8.0: Minimal stress
    - 7.9: Moderate acidification
    - 7.7: Critical acidification
    - 7.5: Severe acidification (shell-forming organisms at risk)
    """
    if current_ph >= HEALTHY_PH:
        return 0.0
    
    # pH drop below healthy level
    ph_drop = HEALTHY_PH - current_ph
    
    # Non-linear: each 0.1 units = higher stress (log-scale response)
    # 0.1 drop = 1 stress, 0.2 drop = 2.5 stress, 0.3 drop = 4.5 stress, etc.
    if ph_drop < 0.1:
        component = ph_drop * 10.0  # 0-1 for 0-0.1 drop
    elif ph_drop < 0.2:
        component = 1.0 + (ph_drop - 0.1) * 15.0  # 1-2.5 for 0.1-0.2 drop
    elif ph_drop < 0.4:
        component = 2.5 + (ph_drop - 0.2) * 10.0  # 2.5-4.5 for 0.2-0.4 drop
    else:
        component = min(10.0, 4.5 + (ph_drop - 0.4) * 15.0)  # 4.5-10 for 0.4+ drop
    
    return round(component, 2)


def calculate_stress_components(
    temp_anomaly: float,
    oxygen_mg_l: float,
    ph: float
) -> Dict[str, float]:
    """
    Calculate individual stress components for diagnostic purposes.
    
    Parameters:
    - temp_anomaly: Temperature anomaly in °C (above baseline)
    - oxygen_mg_l: Dissolved oxygen in mg/L
    - ph: Ocean pH
    
    Returns:
    - Dictionary with normalized components and weighted stress score
    """
    temp_component = normalize_temperature_anomaly(temp_anomaly)
    oxygen_component = normalize_oxygen_depletion(oxygen_mg_l)
    ph_component = normalize_ph_drop(ph)
    
    # Apply weights (40%, 35%, 25%)
    weighted_score = (
        (temp_component * 0.4)
        + (oxygen_component * 0.35)
        + (ph_component * 0.25)
    )
    
    # Scale to 0-100 range
    stress_score = min(100.0, weighted_score * 10)
    
    return {
        "temperature_component": temp_component,
        "oxygen_component": oxygen_component,
        "ph_component": ph_component,
        "weighted_score": round(weighted_score, 2),
        "stress_score": round(stress_score, 2)
    }


def calculate_marine_stress(
    sst: float,
    hotspot_anomaly: float,
    degree_heating_weeks: float,
    ph: float,
    salinity: float,
    chlorophyll: float,
    current_speed: float
) -> Dict[str, Any]:
    """
    Calculate comprehensive marine stress score and analysis.
    
    Uses the core formula:
    stress_score = (temp_anomaly × 0.4) + (oxygen_depletion × 0.35) + (ph_drop × 0.25)
    
    Parameters:
    - sst: Sea surface temperature (°C)
    - hotspot_anomaly: Temperature anomaly above normal (°C)
    - degree_heating_weeks: Accumulated thermal stress (DHW)
    - ph: Ocean pH
    - salinity: Practical salinity units (PSU)
    - chlorophyll: Chlorophyll-a concentration (mg/m³) - proxy for oxygenation
    - current_speed: Water current speed (m/s) - affects oxygenation
    
    Returns:
    - Dictionary with stress score (0-100), components, level, and factors
    """
    
    # Use hotspot anomaly as primary temperature anomaly
    temp_anomaly = max(hotspot_anomaly, degree_heating_weeks * 0.5)
    
    # Estimate dissolved oxygen from chlorophyll and current speed
    # Chlorophyll indicates productivity (oxygen generation)
    # Current speed affects oxygenation mixing
    # Below 5 mg/L is concerning for most marine life
    base_oxygen = 5.0
    # More aggressive penalty for low chlorophyll
    chlorophyll_factor = max(-3.0, (chlorophyll - 0.3) / 0.4)  # Penalty if <0.3
    current_factor = min(0.5, current_speed / 0.3)  # Current helps oxygenation
    estimated_oxygen = base_oxygen + (chlorophyll_factor * 2.0) + (current_factor * 0.5)
    estimated_oxygen = min(10.0, max(0.5, estimated_oxygen))
    
    # Calculate components using core formula
    components = calculate_stress_components(
        temp_anomaly=temp_anomaly,
        oxygen_mg_l=estimated_oxygen,
        ph=ph
    )
    
    stress_score = components["stress_score"]
    
    # Classify stress level
    stress_level, level_description = classify_stress_level(stress_score)
    
    # Identify contributing factors (ordered by impact)
    contributing_factors = _identify_contributing_factors(
        temp_component=components["temperature_component"],
        oxygen_component=components["oxygen_component"],
        ph_component=components["ph_component"],
        salinity=salinity,
        chlorophyll=chlorophyll,
        current_speed=current_speed
    )
    
    return {
        "overall_stress_score": round(stress_score, 2),
        "stress_level": stress_level,
        "stress_description": level_description,
        "temperature_component": components["temperature_component"],
        "oxygen_component": components["oxygen_component"],
        "ph_component": components["ph_component"],
        "contributing_factors": contributing_factors,
        "environmental_summary": {
            "temperature_anomaly_celsius": round(temp_anomaly, 2),
            "estimated_oxygen_mg_l": round(estimated_oxygen, 2),
            "current_ph": ph,
            "current_salinity_psu": salinity,
            "estimated_chlorophyll_mg_m3": round(chlorophyll, 2),
            "current_speed_ms": current_speed
        }
    }


def classify_stress_level(stress_score: float) -> Tuple[str, str]:
    """
    Classify stress score into human-readable category.
    
    Parameters:
    - stress_score: Numeric stress score (0-100)
    
    Returns:
    - Tuple of (level_name, description)
    """
    if stress_score < 20:
        return "HEALTHY", "Marine ecosystem is in good health with minimal environmental stress."
    elif stress_score < 50:
        return "STRESSED", "Marine ecosystem experiencing moderate stress; watch conditions closely."
    elif stress_score < 80:
        return "CRITICAL", "Marine ecosystem in critical condition; intervention may be needed."
    else:
        return "SEVERE", "Extreme environmental stress; ecosystem collapse risk is high."


def _identify_contributing_factors(
    temp_component: float,
    oxygen_component: float,
    ph_component: float,
    salinity: float,
    chlorophyll: float,
    current_speed: float
) -> List[str]:
    """
    Identify and rank the primary stressors affecting the ecosystem.
    
    Parameters:
    - Individual stress components and environmental metrics
    
    Returns:
    - List of factors ranked by severity (highest impact first)
    """
    factors = []
    
    # Add temperature factor
    if temp_component > 3:
        factors.append(("temperature_anomaly", temp_component))
    
    # Add oxygen factor
    if oxygen_component > 3:
        factors.append(("oxygen_depletion", oxygen_component))
    
    # Add pH/acidification factor
    if ph_component > 2:
        factors.append(("ocean_acidification", ph_component))
    
    # Add secondary factors
    if salinity < 32 or salinity > 38:
        factors.append(("osmotic_stress", abs(35 - salinity) * 5))
    
    if chlorophyll < 0.2:
        factors.append(("low_productivity", 5.0))
    
    if current_speed < 0.05:
        factors.append(("poor_circulation", 3.0))
    
    # Sort by severity (highest component/score first)
    factors.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the factor names
    return [f[0] for f in factors]


def get_species_stress_impact(
    species_name: str,
    stress_score: float
) -> Dict[str, Any]:
    """
    Calculate species-specific stress impact based on ecosystem stress score.
    
    Parameters:
    - species_name: Scientific name of species
    - stress_score: Overall ecosystem stress score (0-100)
    
    Returns:
    - Dictionary with species-specific stress assessment
    """
    profile = get_species_profile(species_name)
    
    if not profile:
        # Default assessment for unknown species
        stress_level = "LOW" if stress_score < 30 else "MODERATE" if stress_score < 60 else "HIGH"
        return {
            "species": species_name,
            "profile_found": False,
            "stress_level": stress_level,
            "vulnerability": "UNKNOWN",
            "conservation_priority": "UNKNOWN",
            "recommendation": "Species not in indicator database; default resilience assumed."
        }
    
    # Species-specific vulnerability assessment
    sensitivity = profile.get("sensitivity", "UNKNOWN")
    
    # Map sensitivity to vulnerability at different stress levels
    if sensitivity == "HIGH":
        if stress_score < 30:
            vulnerability = "LOW"
        elif stress_score < 50:
            vulnerability = "MODERATE"
        elif stress_score < 70:
            vulnerability = "HIGH"
        else:
            vulnerability = "VERY_HIGH"
    elif sensitivity == "MEDIUM":
        if stress_score < 40:
            vulnerability = "LOW"
        elif stress_score < 65:
            vulnerability = "MODERATE"
        elif stress_score < 85:
            vulnerability = "HIGH"
        else:
            vulnerability = "VERY_HIGH"
    else:  # LOW sensitivity
        if stress_score < 60:
            vulnerability = "LOW"
        elif stress_score < 80:
            vulnerability = "MODERATE"
        else:
            vulnerability = "HIGH"
    
    return {
        "species": species_name,
        "common_name": profile.get("common_name", species_name),
        "profile_found": True,
        "stress_level": "CRITICAL" if stress_score > 50 else "MODERATE" if stress_score > 20 else "HEALTHY",
        "vulnerability": vulnerability,
        "sensitivity": sensitivity,
        "conservation_priority": profile.get("conservation_priority", "MONITOR"),
        "bleaching_indicator": profile.get("bleaching_indicator", False),
        "recommendation": _generate_species_recommendation(
            species_name,
            sensitivity,
            vulnerability,
            stress_score
        )
    }


def _generate_species_recommendation(
    species_name: str,
    sensitivity: str,
    vulnerability: str,
    stress_score: float
) -> str:
    """Generate conservation/monitoring recommendation for species."""
    if vulnerability == "VERY_HIGH":
        return f"{species_name} is at critical risk. Immediate conservation intervention required."
    elif vulnerability == "HIGH":
        return f"{species_name} is vulnerable. Increase monitoring and consider protective measures."
    elif vulnerability == "MODERATE":
        return f"{species_name} is moderately stressed. Continue monitoring conditions."
    else:
        return f"{species_name} appears resilient to current conditions. Maintain monitoring."
