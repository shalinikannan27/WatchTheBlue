import logging
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("species_logic")

# Standardized database of indicator species and their environmental thresholds
# Acropora cervicornis (Staghorn Coral) -> Highly sensitive
# Carcharodon carcharias (Great White Shark) -> Resilient
# Tridacna gigas (Giant Clam) -> Moderate
# Acanthaster planci (Crown-of-Thorns Starfish) -> Resilient / Invasive threat
SPECIES_THRESHOLDS = {
    "acropora cervicornis": {
        "common_name": "Staghorn Coral",
        "iucn_status": "Critically Endangered",
        "min_sst": 20.0,
        "max_sst": 29.0,
        "min_ph": 7.95,
        "min_salinity": 32.0,
        "max_salinity": 38.0,
        "sensitivity": "HIGH",
        "bleaching_indicator": True,
        "conservation_priority": "CRITICAL"
    },
    "tridacna gigas": {
        "common_name": "Giant Clam",
        "iucn_status": "Vulnerable",
        "min_sst": 22.0,
        "max_sst": 30.0,
        "min_ph": 7.90,
        "min_salinity": 30.0,
        "max_salinity": 39.0,
        "sensitivity": "MEDIUM",
        "bleaching_indicator": True,
        "conservation_priority": "HIGH"
    },
    "carcharodon carcharias": {
        "common_name": "Great White Shark",
        "iucn_status": "Vulnerable",
        "min_sst": 12.0,
        "max_sst": 24.0,
        "min_ph": 7.60,
        "min_salinity": 28.0,
        "max_salinity": 40.0,
        "sensitivity": "LOW",
        "bleaching_indicator": False,
        "conservation_priority": "MEDIUM"
    },
    "acanthaster planci": {
        "common_name": "Crown-of-Thorns Starfish",
        "iucn_status": "Least Concern (Invasive Threat)",
        "min_sst": 18.0,
        "max_sst": 31.0,
        "min_ph": 7.70,
        "min_salinity": 26.0,
        "max_salinity": 42.0,
        "sensitivity": "LOW",
        "bleaching_indicator": False,
        "conservation_priority": "MONITOR_OUTBREAKS",
        "note": "Outbreaks feed aggressively on living coral reefs."
    }
}

def get_species_profile(scientific_name: str) -> Optional[Dict[str, Any]]:
    """
    Look up predefined thresholds and metadata for a given species name.
    """
    clean_name = scientific_name.lower().strip()
    return SPECIES_THRESHOLDS.get(clean_name)

def analyze_habitat_suitability(scientific_name: str, current_env: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze if the current ocean environment satisfies the biological requirements 
    of a specific marine species.
    """
    profile = get_species_profile(scientific_name)
    if not profile:
        # Default fallback for unknown species
        return {
            "species": scientific_name,
            "profile_found": False,
            "suitability_score": 100.0,
            "suitability_status": "UNKNOWN",
            "warnings": ["Species profile not in indicator database. Assuming default resilience."]
        }
        
    warnings = []
    suitability_score = 100.0
    
    sst = current_env.get("sst_celsius")
    ph = current_env.get("ph")
    salinity = current_env.get("salinity_psu")
    
    # 1. SST Evaluation
    if sst is not None:
        if sst > profile["max_sst"]:
            diff = sst - profile["max_sst"]
            penalty = min(40.0, diff * 15)
            suitability_score -= penalty
            warnings.append(f"Temperature is too warm ({sst}°C) for {profile['common_name']}. Threshold: {profile['max_sst']}°C")
        elif sst < profile["min_sst"]:
            diff = profile["min_sst"] - sst
            penalty = min(30.0, diff * 10)
            suitability_score -= penalty
            warnings.append(f"Temperature is too cold ({sst}°C) for {profile['common_name']}. Threshold: {profile['min_sst']}°C")
            
    # 2. pH Evaluation
    if ph is not None:
        if ph < profile["min_ph"]:
            diff = profile["min_ph"] - ph
            penalty = min(35.0, diff * 100) # highly sensitive to acidification
            suitability_score -= penalty
            warnings.append(f"Critical ocean acidification (pH {ph}) detected. Threshold: {profile['min_ph']}")
            
    # 3. Salinity Evaluation
    if salinity is not None:
        if salinity < profile["min_salinity"] or salinity > profile["max_salinity"]:
            suitability_score -= 15.0
            warnings.append(f"Osmotic stress! Salinity ({salinity} psu) is outside healthy range ({profile['min_salinity']}-{profile['max_salinity']} psu)")

    suitability_score = round(max(0.0, suitability_score), 1)
    
    if suitability_score >= 80:
        status = "OPTIMAL"
    elif suitability_score >= 50:
        status = "STRESSED"
    else:
        status = "CRITICAL / UNFITTING"

    return {
        "species": scientific_name,
        "common_name": profile["common_name"],
        "iucn_status": profile["iucn_status"],
        "conservation_priority": profile["conservation_priority"],
        "profile_found": True,
        "suitability_score": suitability_score,
        "suitability_status": status,
        "warnings": warnings
    }

def clean_obis_coordinates(occurrences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse raw OBIS occurrence results to extract clean, mappable records
    with essential coordinates and dates, filtering out invalid records.
    """
    records = occurrences.get("results", [])
    clean_records = []
    
    for r in records:
        lat = r.get("decimalLatitude")
        lon = r.get("decimalLongitude")
        
        # Must have valid geographic coordinates
        if lat is None or lon is None:
            continue
            
        clean_records.append({
            "id": r.get("id"),
            "scientificName": r.get("scientificName"),
            "decimalLatitude": float(lat),
            "decimalLongitude": float(lon),
            "eventDate": r.get("eventDate") or r.get("date_year", "Unknown"),
            "depth": r.get("depth"),
            "country": r.get("country", "Open Ocean")
        })
        
    return clean_records

def species_risk(stress_score: float) -> List[str]:
    """
    Determine which marine species are at risk based on the given ecosystem stress score.
    Utilizes the pre-coded SPECIES_THRESHOLDS sensitivity levels.
    """
    at_risk_species = []
    
    for scientific_name, profile in SPECIES_THRESHOLDS.items():
        sensitivity = profile.get("sensitivity")
        common_name = profile.get("common_name")
        
        # Determine risk based on stress_score and species sensitivity
        is_at_risk = False
        if sensitivity == "HIGH" and stress_score > 40:
            is_at_risk = True
        elif sensitivity == "MEDIUM" and stress_score > 60:
            is_at_risk = True
        elif sensitivity == "LOW" and stress_score > 80:
            is_at_risk = True
            
        if is_at_risk:
            at_risk_species.append(str(common_name))
            
    return at_risk_species

