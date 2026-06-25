# ============================================================
# tools/flight_tool.py
#
# CONCEPT: Tool Definition
#   - Uses SerpAPI's Google Flights engine
#   - Supports one-way and round-trip searches
#   - Returns flight options with prices, duration, stops, airlines
# ============================================================

import json
from langchain_core.tools import tool
from serpapi import GoogleSearch

from config.settings import SERPAPI_API_KEY, SERP_MAX_RESULTS


@tool
def flight_search(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    adults: int = 1,
    travel_class: str = "economy",
    max_stops: int = -1,
) -> str:
    """
    Search for available flights between two cities using Google Flights.

    Use this tool when the user asks about:
    - Flight options between cities
    - Cheapest flights on a date
    - Flight duration and stops
    - Business or economy class availability
    - Round trip vs one-way flights

    Args:
        origin: Departure city or IATA airport code (e.g., "Bangalore" or "BLR", "New York" or "JFK")
        destination: Arrival city or IATA airport code (e.g., "Paris" or "CDG", "Dubai" or "DXB")
        departure_date: Departure date in YYYY-MM-DD format (e.g., "2025-08-15")
        return_date: Return date in YYYY-MM-DD for round trips. Leave empty for one-way.
        adults: Number of adult passengers (default: 1)
        travel_class: Seat class — "economy", "premium_economy", "business", or "first"
        max_stops: Maximum number of stops (-1 = any, 0 = nonstop only, 1 = max 1 stop)

    Returns:
        JSON string with list of flights including airline, price, duration, stops, and booking info
    """

    if not origin or not destination:
        return json.dumps({"error": "Both origin and destination are required"})
    if not departure_date:
        return json.dumps({"error": "Departure date is required (YYYY-MM-DD format)"})

    # ── Map travel class to SerpAPI codes ────────────────────
    class_map = {
        "economy": "1",
        "premium_economy": "2",
        "business": "3",
        "first": "4",
    }
    travel_class_code = class_map.get(travel_class.lower(), "1")

    # ── Determine trip type ───────────────────────────────────
    trip_type = "1" if not return_date else "2"   # 1=one-way, 2=round-trip

    # ── Build SerpAPI params ─────────────────────────────────
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "type": trip_type,
        "travel_class": travel_class_code,
        "adults": str(adults),
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "gl": "us",
        "currency": "USD",
    }

    if return_date and trip_type == "2":
        params["return_date"] = return_date

    if max_stops == 0:
        params["stops"] = "0"   # nonstop only
    elif max_stops == 1:
        params["stops"] = "1"   # max 1 stop

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        flights_data = {
            "route": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date if return_date else "N/A (one-way)",
                "trip_type": "round-trip" if return_date else "one-way",
                "passengers": adults,
                "class": travel_class,
            },
            "best_flights": [],
            "other_flights": [],
        }

        # ── Parse best flights ───────────────────────────────
        best_flights = results.get("best_flights", [])
        for flight in best_flights[:3]:
            flights_data["best_flights"].append(_parse_flight(flight))

        # ── Parse other flights ──────────────────────────────
        other_flights = results.get("other_flights", [])
        for flight in other_flights[:SERP_MAX_RESULTS]:
            flights_data["other_flights"].append(_parse_flight(flight))

        # ── Price insights ───────────────────────────────────
        price_insights = results.get("price_insights", {})
        if price_insights:
            flights_data["price_insights"] = {
                "lowest_price": price_insights.get("lowest_price", "N/A"),
                "price_level": price_insights.get("price_level", "N/A"),
                "typical_range": price_insights.get("typical_range_formatted", "N/A"),
            }

        # ── Airport info ─────────────────────────────────────
        airports = results.get("airports", [])
        if airports:
            flights_data["airport_info"] = [
                {
                    "departure": leg.get("departure", [{}])[0].get("airport", {}).get("name", ""),
                    "arrival": leg.get("arrival", [{}])[0].get("airport", {}).get("name", ""),
                }
                for leg in airports[:2]
            ]

        if not best_flights and not other_flights:
            # Fallback to organic search
            return _flight_organic_fallback(origin, destination, departure_date, results)

        flights_data["total_options"] = len(best_flights) + len(other_flights)
        return json.dumps(flights_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Flight search failed: {str(e)}",
            "route": f"{origin} → {destination}",
            "date": departure_date,
            "tip": "Try using IATA codes (e.g., BLR, CDG) and ensure date is YYYY-MM-DD",
        })


def _parse_flight(flight: dict) -> dict:
    """Parse a single flight object from SerpAPI into clean format."""
    parsed = {
        "price": flight.get("price", "N/A"),
        "total_duration_minutes": flight.get("total_duration", 0),
        "total_duration_human": _minutes_to_duration(flight.get("total_duration", 0)),
        "carbon_emissions": flight.get("carbon_emissions", {}).get("this_flight", "N/A"),
        "legs": [],
    }

    # Parse each flight leg (could be multiple for connecting flights)
    for leg in flight.get("flights", []):
        parsed["legs"].append({
            "airline": leg.get("airline", "Unknown"),
            "flight_number": leg.get("flight_number", ""),
            "departure_airport": leg.get("departure_airport", {}).get("name", ""),
            "departure_time": leg.get("departure_airport", {}).get("time", ""),
            "arrival_airport": leg.get("arrival_airport", {}).get("name", ""),
            "arrival_time": leg.get("arrival_airport", {}).get("time", ""),
            "duration_minutes": leg.get("duration", 0),
            "airplane": leg.get("airplane", ""),
            "legroom": leg.get("legroom", ""),
            "extensions": leg.get("extensions", [])[:3],
        })

    # Layovers
    layovers = flight.get("layovers", [])
    if layovers:
        parsed["layovers"] = [
            {
                "airport": lv.get("name", ""),
                "duration_minutes": lv.get("duration", 0),
                "overnight": lv.get("overnight", False),
            }
            for lv in layovers
        ]

    return parsed


def _minutes_to_duration(minutes: int) -> str:
    """Convert minutes to human-readable duration."""
    if not minutes:
        return "N/A"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def _flight_organic_fallback(origin: str, destination: str, date: str, results: dict) -> str:
    """Fallback to organic search when flight engine returns no results."""
    organic = results.get("organic_results", [])
    return json.dumps({
        "route": f"{origin} → {destination}",
        "date": date,
        "source": "organic_fallback",
        "note": "Real-time flight data not available. Showing search results.",
        "results": [
            {
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
            }
            for r in organic[:4]
        ],
        "suggestion": "Try booking directly on Google Flights, Skyscanner, or MakeMyTrip",
    })