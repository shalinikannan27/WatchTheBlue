"""
OBIS (Ocean Biodiversity Information System) API integration.

Fetches species occurrence data from OBIS for a given location.
No API key required - OBIS provides free public API access.

Falls back to realistic simulated species data if API unavailable.
"""

import os
import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obis_fetch")


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


def get_species_occurrences(
    lat: float,
    lon: float,
    radius_km: float = 10.0,
    limit: int = 100,
    geometry: str = "polygon"
) -> Dict[str, Any]:
    """
    Fetch species occurrence data from real OBIS API.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        radius_km: Search radius in kilometers (for circular searches)
        limit: Maximum number of results to return (1-50000)
        geometry: Geometry type ('polygon' for square around point)

    Returns:
        dict: OBIS API response with occurrence data

    Raises:
        ValueError: If coordinates invalid
    """
    validate_coordinates(lat, lon)

    try:
        # Build OBIS API query
        # OBIS API endpoint for geographic queries
        url = "https://api.obis.org/v3/occurrence"

        # Create bounding box around the point
        # This is more reliable than radius-based queries
        offset = (radius_km / 111.0)  # Approximate km to degrees conversion

        params = {
            "startdatetime": (datetime.now() - timedelta(days=365)).isoformat(),
            "enddatetime": datetime.now().isoformat(),
            "geometry": f"POLYGON(({lon - offset} {lat - offset},"
                        f"{lon + offset} {lat - offset},"
                        f"{lon + offset} {lat + offset},"
                        f"{lon - offset} {lat + offset},"
                        f"{lon - offset} {lat - offset}))",
            "limit": limit,
            "format": "json"
        }

        logger.info(f"Querying OBIS API for Lat={lat}, Lon={lon}")

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        logger.info(
            f"OBIS API success: found {len(data.get('results', []))} "
            f"occurrences at ({lat},{lon})"
        )

        return data

    except Exception as e:
        logger.error(f"OBIS API error: {str(e)}")
        raise


def get_species_by_location(
    lat: float,
    lon: float,
    limit: int = 50,
    radius_km: float = 50.0
) -> Dict[str, Any]:
    """
    Get species occurrences by location with fallback to simulation.

    Attempts to fetch real data from OBIS API.
    If API fails, falls back to realistic simulated species data.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        limit: Maximum results to return (default 50)
        radius_km: Search radius in kilometers (default 50.0)

    Returns:
        dict: Species occurrences with metadata
        {
            "occurrences": [
                {
                    "scientific_name": str,
                    "latitude": float,
                    "longitude": float,
                    "date": str,
                    "kingdom": str,
                    "phylum": str,
                    "class": str,
                    "family": str,
                    "depth": float or None,
                    "basis_of_record": str
                },
                ...
            ],
            "total": int,
            "source": str,
            "coordinates": dict,
            "timestamp": str
        }
    """
    validate_coordinates(lat, lon)

    try:
        # Try real OBIS API
        api_data = get_species_occurrences(lat, lon, limit=limit, radius_km=radius_km)

        # Parse results
        occurrences = [
            _parse_occurrence_data(occ)
            for occ in api_data.get("results", [])
        ]

        logger.info(f"OBIS integration success: {len(occurrences)} species found")

        return {
            "occurrences": occurrences,
            "total": api_data.get("total", len(occurrences)),
            "source": "OBIS API (Real Data)",
            "coordinates": {"latitude": lat, "longitude": lon},
            "timestamp": datetime.now().isoformat(),
            "note": f"Data from {len(occurrences)} observations at ({lat},{lon})"
        }

    except Exception as e:
        logger.warning(
            f"OBIS API unavailable ({type(e).__name__}: {str(e)}). "
            "Using simulated species data."
        )
        # Fall back to simulated data
        return _simulate_species_occurrences(lat, lon, limit)


def _parse_occurrence_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize OBIS occurrence data.

    Maps OBIS API fields to standard format.

    Args:
        raw_data: Raw OBIS API response object

    Returns:
        dict: Normalized occurrence data
    """
    # Extract date
    date_str = raw_data.get("eventDate")
    if not date_str:
        date_str = datetime.fromtimestamp(
            raw_data.get("date_mid", 0) / 1000
        ).isoformat()
    else:
        date_str = date_str.split("T")[0]  # Get just the date part

    return {
        "scientific_name": raw_data.get("scientificName", "Unknown"),
        "latitude": raw_data.get("decimalLatitude", 0.0),
        "longitude": raw_data.get("decimalLongitude", 0.0),
        "date": date_str,
        "kingdom": raw_data.get("kingdom", ""),
        "phylum": raw_data.get("phylum", ""),
        "class": raw_data.get("class", ""),
        "family": raw_data.get("family", ""),
        "depth": raw_data.get("depth"),
        "basis_of_record": raw_data.get("basisOfRecord", "Unknown"),
        "vernacular_name": raw_data.get("vernacularName"),
        "source_dataset": raw_data.get("datasetName", "")
    }


def _simulate_species_occurrences(
    lat: float,
    lon: float,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Generate realistic simulated species occurrence data as fallback.

    Uses location-based species distributions to create plausible observations.

    Args:
        lat: Latitude
        lon: Longitude
        limit: Number of species to simulate

    Returns:
        dict: Simulated species occurrence data
    """
    validate_coordinates(lat, lon)

    logger.info(
        f"Simulating OBIS species occurrences for Lat={lat}, Lon={lon}"
    )

    abs_lat = abs(lat)

    # Define species pools by region
    tropical_species = {
        "Acropora palmata": {"phylum": "Cnidaria", "class": "Anthozoa"},
        "Montastraea annularis": {"phylum": "Cnidaria", "class": "Anthozoa"},
        "Orbicella faveolata": {"phylum": "Cnidaria", "class": "Anthozoa"},
        "Plectropomus leopardus": {
            "phylum": "Chordata",
            "class": "Teleostei",
            "family": "Epinephelidae"
        },
        "Chaetodon striatus": {
            "phylum": "Chordata",
            "class": "Teleostei",
            "family": "Chaetodontidae"
        },
        "Tridacna gigas": {"phylum": "Mollusca", "class": "Bivalvia"},
        "Holothuroidea sp.": {"phylum": "Echinodermata", "class": "Holothuroidea"},
    }

    temperate_species = {
        "Asterias rubens": {
            "phylum": "Echinodermata",
            "class": "Asteroidea",
            "family": "Asteriidae"
        },
        "Mytilus edulis": {
            "phylum": "Mollusca",
            "class": "Bivalvia",
            "family": "Mytilidae"
        },
        "Pomatoschistus microps": {
            "phylum": "Chordata",
            "class": "Teleostei",
            "family": "Gobiidae"
        },
        "Saccharina latissima": {"phylum": "Ochrophyta", "class": "Phaeophyceae"},
        "Homarus americanus": {
            "phylum": "Arthropoda",
            "class": "Malacostraca",
            "family": "Nephropidae"
        },
    }

    polar_species = {
        "Euphausia superba": {
            "phylum": "Arthropoda",
            "class": "Malacostraca",
            "family": "Euphausiidae"
        },
        "Pagothenia borchgrevinki": {
            "phylum": "Chordata",
            "class": "Teleostei",
            "family": "Nototheniidae"
        },
        "Strongylocentrotus": {
            "phylum": "Echinodermata",
            "class": "Echinoidea"
        },
    }

    # Select species pool based on latitude
    if abs_lat < 30:
        species_pool = tropical_species
    elif abs_lat < 55:
        species_pool = temperate_species
    else:
        species_pool = polar_species

    # Generate occurrences
    occurrences = []
    for i, (species_name, taxonomy) in enumerate(list(species_pool.items())[:limit]):
        occurrence = {
            "scientific_name": species_name,
            "latitude": lat + (random.random() - 0.5) * 2.0,  # ±1° variation
            "longitude": lon + (random.random() - 0.5) * 2.0,
            "date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat().split("T")[0],
            "kingdom": "Animalia" if taxonomy["phylum"] != "Ochrophyta" else "Chromista",
            "phylum": taxonomy["phylum"],
            "class": taxonomy.get("class", ""),
            "family": taxonomy.get("family", ""),
            "depth": round(random.uniform(0, 100), 1) if abs_lat < 70 else None,
            "basis_of_record": random.choice([
                "HumanObservation",
                "MachineObservation",
                "MATERIAL_SAMPLE"
            ]),
            "vernacular_name": None,
            "source_dataset": "Simulated OBIS Dataset"
        }
        occurrences.append(occurrence)

    return {
        "occurrences": occurrences,
        "total": len(occurrences),
        "source": "Simulated OBIS Data (API unavailable)",
        "coordinates": {"latitude": lat, "longitude": lon},
        "timestamp": datetime.now().isoformat(),
        "note": f"Using simulated species data. {len(occurrences)} species simulated for ({lat},{lon})"
    }
