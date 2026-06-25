# ============================================================
# tools/maps_tool.py
#
# CONCEPT: Tool Definition
#   - Uses SerpAPI's Google Maps engine for directions
#   - Also searches for nearby places, attractions, transit info
#   - Returns routes with distance, duration, and steps
# ============================================================

import json
from langchain_core.tools import tool
from serpapi import GoogleSearch

from config.settings import SERPAPI_API_KEY, SERP_MAX_RESULTS


@tool
def maps_search(
    origin: str,
    destination: str,
    travel_mode: str = "driving",
    query: str = "",
) -> str:
    """
    Get directions, distances, and navigation between two places using Google Maps.
    Also search for nearby places, attractions, or transit options.

    Use this tool when the user asks about:
    - How to get from place A to place B
    - Distance between two locations
    - Travel time by car, transit, walking, or cycling
    - Directions or routes within a city
    - Nearby attractions or places at a destination

    Args:
        origin: Starting point (e.g., "Eiffel Tower, Paris", "Kempegowda Airport Bangalore", "Times Square NYC")
        destination: Ending point (e.g., "Louvre Museum, Paris", "MG Road Bangalore", "Central Park NYC")
        travel_mode: Mode of transport — "driving", "transit", "walking", or "bicycling" (default: "driving")
        query: Optional extra search query for nearby places (e.g., "restaurants near Eiffel Tower")
               Leave empty for just directions between origin and destination.

    Returns:
        JSON string with route options, distance, duration, and step-by-step directions
    """

    # ── If a nearby/search query is provided, use maps search ─
    if query and not (origin and destination):
        return _search_nearby(query)

    if not origin or not destination:
        return json.dumps({"error": "Both origin and destination are required for directions"})

    # ── Map travel mode to SerpAPI parameter ─────────────────
    mode_map = {
        "driving": "0",
        "transit": "3",
        "walking": "2",
        "bicycling": "1",
    }
    mode_code = mode_map.get(travel_mode.lower(), "0")

    # ── Build directions params ──────────────────────────────
    params = {
        "engine": "google_maps_directions",
        "start_addr": origin,
        "end_addr": destination,
        "travel_mode": mode_code,
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        maps_data = {
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode,
            "routes": [],
        }

        # ── Parse routes ────────────────────────────────────
        directions = results.get("directions", [])

        if not directions:
            # Fallback to regular Google Maps search
            return _maps_organic_fallback(origin, destination, travel_mode, results)

        for route in directions[:2]:   # Show top 2 route options
            route_info = {
                "distance": route.get("distance", "N/A"),
                "duration": route.get("duration", "N/A"),
                "steps": [],
            }

            # Parse turn-by-turn steps
            for step in route.get("steps", [])[:10]:
                step_info = {
                    "instruction": step.get("instruction", ""),
                    "distance": step.get("distance", ""),
                    "duration": step.get("duration", ""),
                    "travel_mode": step.get("travel_mode", travel_mode),
                }

                # Transit-specific info (bus number, train line, etc.)
                if "transit_details" in step:
                    transit = step["transit_details"]
                    step_info["transit"] = {
                        "vehicle_type": transit.get("vehicle", {}).get("type", ""),
                        "line_name": transit.get("line", {}).get("name", ""),
                        "departure_stop": transit.get("departure_stop", {}).get("name", ""),
                        "arrival_stop": transit.get("arrival_stop", {}).get("name", ""),
                        "num_stops": transit.get("num_stops", ""),
                    }

                route_info["steps"].append(step_info)

            maps_data["routes"].append(route_info)

        # ── Add local info ───────────────────────────────────
        if query:
            nearby = _search_nearby(query)
            maps_data["nearby_search"] = json.loads(nearby)

        return json.dumps(maps_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Maps search failed: {str(e)}",
            "origin": origin,
            "destination": destination,
            "fallback_tip": f"Try Google Maps directly: maps.google.com/?saddr={origin}&daddr={destination}",
        })


def _search_nearby(query: str) -> str:
    """Search for nearby places or attractions using Google Maps search."""
    params = {
        "engine": "google_maps",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "type": "search",
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        nearby_data = {
            "query": query,
            "places": [],
        }

        local_results = results.get("local_results", [])
        for place in local_results[:SERP_MAX_RESULTS]:
            nearby_data["places"].append({
                "name": place.get("title", ""),
                "type": place.get("type", ""),
                "address": place.get("address", ""),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("reviews", "N/A"),
                "hours": place.get("hours", ""),
                "phone": place.get("phone", ""),
                "website": place.get("website", ""),
                "thumbnail": place.get("thumbnail", ""),
                "gps_coordinates": place.get("gps_coordinates", {}),
            })

        return json.dumps(nearby_data, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Nearby search failed: {str(e)}", "query": query})


def _maps_organic_fallback(origin: str, destination: str, mode: str, results: dict) -> str:
    """Fallback when directions engine returns nothing."""
    organic = results.get("organic_results", [])
    google_maps_url = (
        f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}"
        f"/{destination.replace(' ', '+')}"
    )

    return json.dumps({
        "origin": origin,
        "destination": destination,
        "travel_mode": mode,
        "source": "organic_fallback",
        "google_maps_link": google_maps_url,
        "note": "Structured directions not available. Use the Google Maps link above.",
        "search_results": [
            {
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
            }
            for r in organic[:3]
        ],
    }, indent=2)