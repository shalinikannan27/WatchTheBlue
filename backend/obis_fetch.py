import os
import logging
import requests
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obis_fetch")

OBIS_API_BASE = os.getenv("OBIS_API_BASE_URL", "https://api.obis.org/v2")

def fetch_obis_occurrences(
    scientific_name: Optional[str] = None,
    taxon_id: Optional[int] = None,
    geometry: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch occurrence records from the OBIS (Ocean Biodiversity Information System) API.
    
    Args:
        scientific_name (str, optional): The scientific name of the species.
        taxon_id (int, optional): The OBIS/AphiaID taxon identifier.
        geometry (str, optional): WKT (Well-Known Text) string representing spatial boundary.
        start_date (str, optional): Start date for occurrences (YYYY-MM-DD).
        end_date (str, optional): End date for occurrences (YYYY-MM-DD).
        size (int, optional): Number of results to return (default 100).
        
    Returns:
        dict: The response JSON with occurrence records, or error details.
    """
    url = f"{OBIS_API_BASE}/occurrence"
    params = {}
    
    if scientific_name:
        params["scientificname"] = scientific_name
    if taxon_id:
        params["taxonid"] = taxon_id
    if geometry:
        params["geometry"] = geometry
    if start_date:
        params["startdate"] = start_date
    if end_date:
        params["enddate"] = end_date
    
    params["size"] = size
    
    try:
        logger.info(f"Fetching OBIS occurrences with params: {params}")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OBIS occurrences: {e}")
        return {"error": str(e), "results": []}

def fetch_taxon_info(taxon_id: int) -> Dict[str, Any]:
    """
    Fetch detailed taxon metadata from OBIS by AphiaID/taxonid.
    """
    url = f"{OBIS_API_BASE}/taxon/{taxon_id}"
    try:
        logger.info(f"Fetching OBIS taxon info for ID: {taxon_id}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OBIS taxon info: {e}")
        return {"error": str(e)}

def search_taxon(query: str) -> Dict[str, Any]:
    """
    Search for a taxon by scientific name query.
    """
    url = f"{OBIS_API_BASE}/taxon"
    params = {"q": query}
    try:
        logger.info(f"Searching OBIS taxon with query: {query}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching OBIS taxon: {e}")
        return {"error": str(e), "results": []}
