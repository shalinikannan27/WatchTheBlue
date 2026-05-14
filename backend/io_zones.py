"""
Indian Ocean sector definitions aligned with the frontend map (MapPage.jsx).
Used only for zone ids, bounds, and batch risk overlays — not drift physics.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Mirrors frontend/maps/src/components/MapPage.jsx ZONES
IO_ZONES: List[Dict[str, Any]] = [
    {
        "id": "arabian_sea",
        "name": "Arabian Sea",
        "center": (16.0, 72.0),
        "bounds": ((10.0, 68.0), (23.0, 77.0)),
    },
    {
        "id": "bay_of_bengal",
        "name": "Bay of Bengal",
        "center": (15.0, 85.0),
        "bounds": ((10.0, 80.0), (20.0, 90.0)),
    },
    {
        "id": "lakshadweep",
        "name": "Lakshadweep Sea",
        "center": (10.0, 73.0),
        "bounds": ((8.0, 72.0), (12.0, 74.0)),
    },
    {
        "id": "andaman_sea",
        "name": "Andaman Sea",
        "center": (12.0, 95.0),
        "bounds": ((10.0, 92.0), (14.0, 98.0)),
    },
]


def zone_for_point(lat: float, lon: float) -> Dict[str, Any]:
    """Return the zone dict containing the point, or nearest by center distance."""
    matched: Optional[Dict[str, Any]] = None
    for z in IO_ZONES:
        (south, west), (north, east) = z["bounds"]
        if south <= lat <= north and west <= lon <= east:
            matched = z
            break
    if matched:
        return matched

    def dist_sq(z: Dict[str, Any]) -> float:
        clat, clon = z["center"]
        return (lat - clat) ** 2 + (lon - clon) ** 2

    return min(IO_ZONES, key=dist_sq)


def get_zone_display_name(lat: float, lon: float) -> str:
    """Human-readable region label (legacy get_zone_name semantics)."""
    z = zone_for_point(lat, lon)
    if z["id"] == "andaman_sea":
        return "Andaman and Nicobar"
    return z["name"]


def zone_bounds_leaflet(zone_id: str) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Bounds as ((south, west), (north, east)) for Leaflet rectangles."""
    for z in IO_ZONES:
        if z["id"] == zone_id:
            return z["bounds"]
    return None
