import json
from langchain_core.tools import tool
from serpapi import GoogleSearch
from config.settings import SERPAPI_API_KEY


def _readable(value) -> str:
    """SerpAPI returns distance/duration as either a string or {"text": ..., "value": ...}."""
    if isinstance(value, dict):
        return value.get("text", str(value))
    return str(value) if value else "N/A"


@tool
def maps_search(
    origin: str,
    destination: str,
    travel_mode: str = "driving",
) -> str:
    """
    Get directions and travel time between two places using Google Maps.

    Use this when the user asks about how to get somewhere, distances, or travel time.

    Args:
        origin: Starting point (e.g., "Eiffel Tower, Paris", "Times Square NYC")
        destination: Ending point (e.g., "Louvre Museum, Paris", "Central Park NYC")
        travel_mode: "driving", "transit", "walking", or "bicycling" (default: "driving")
    """
    mode_map = {"driving": "0", "bicycling": "1", "walking": "2", "transit": "3"}

    params = {
        "engine": "google_maps_directions",
        "start_addr": origin,
        "end_addr": destination,
        "travel_mode": mode_map.get(travel_mode, "0"),
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
    }

    results = GoogleSearch(params).get_dict()

    routes = []
    for route in results.get("directions", [])[:2]:
        routes.append({
            "distance": _readable(route.get("distance")),
            "duration": _readable(route.get("duration")),
            "steps": [
                {
                    "instruction": s.get("instruction"),
                    "distance": _readable(s.get("distance")),
                }
                for s in route.get("steps", [])[:8]
            ],
        })

    return json.dumps({
        "origin": origin,
        "destination": destination,
        "travel_mode": travel_mode,
        "routes": routes,
    }, indent=2)
