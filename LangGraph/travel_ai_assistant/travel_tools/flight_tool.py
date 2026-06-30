import json
from langchain_core.tools import tool
from serpapi import GoogleSearch
from config.settings import SERPAPI_API_KEY


@tool
def flight_search(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    adults: int = 1,
) -> str:
    """
    Search for available flights between two cities using Google Flights.

    Use this when the user asks about flights, prices, or travel between cities.

    Args:
        origin: Departure city or airport code (e.g., "Bangalore" or "BLR")
        destination: Arrival city or airport code (e.g., "Paris" or "CDG")
        departure_date: Date in YYYY-MM-DD format (e.g., "2025-08-15")
        return_date: Return date for round trips. Leave empty for one-way.
        adults: Number of passengers (default: 1)
    """
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "type": "2" if return_date else "1",  # 1=one-way, 2=round-trip
        "adults": str(adults),
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "gl": "us",
        "currency": "USD",
    }

    if return_date:
        params["return_date"] = return_date

    results = GoogleSearch(params).get_dict()

    # Try best_flights first, fall back to other_flights
    raw_flights = results.get("best_flights", []) or results.get("other_flights", [])

    flights = []
    for flight in raw_flights[:4]:
        legs = flight.get("flights", [])
        flights.append({
            "price": flight.get("price"),
            "duration_minutes": flight.get("total_duration"),
            "airline": legs[0].get("airline") if legs else "Unknown",
            "departure_time": legs[0].get("departure_airport", {}).get("time") if legs else "",
            "arrival_time": legs[-1].get("arrival_airport", {}).get("time") if legs else "",
            "stops": len(flight.get("layovers", [])),
        })

    return json.dumps({
        "route": f"{origin} → {destination}",
        "date": departure_date,
        "return_date": return_date or "one-way",
        "flights_found": len(flights),
        "flights": flights,
    }, indent=2)
