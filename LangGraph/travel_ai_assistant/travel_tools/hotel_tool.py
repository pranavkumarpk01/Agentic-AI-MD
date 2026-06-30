import json
from langchain_core.tools import tool
from serpapi import GoogleSearch
from config.settings import SERPAPI_API_KEY


@tool
def hotel_search(
    location: str,
    check_in_date: str = "",
    check_out_date: str = "",
    max_price: int = 0,
    adults: int = 2,
) -> str:
    """
    Search for hotels at a travel destination using Google Hotels.

    Use this when the user asks about hotels, accommodation, or places to stay.

    Args:
        location: City or area (e.g., "Paris", "Goa Beach", "Manhattan NYC")
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        max_price: Maximum price per night in USD (0 = no limit)
        adults: Number of guests (default: 2)
    """
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {location}",
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "gl": "us",
        "currency": "USD",
        "adults": str(adults),
    }

    if check_in_date:
        params["check_in_date"] = check_in_date
    if check_out_date:
        params["check_out_date"] = check_out_date
    if max_price > 0:
        params["max_price"] = str(max_price)

    results = GoogleSearch(params).get_dict()

    hotels = []
    for hotel in results.get("properties", [])[:5]:
        rate = hotel.get("rate_per_night", {})
        hotels.append({
            "name": hotel.get("name"),
            "rating": hotel.get("overall_rating"),
            "reviews": hotel.get("reviews"),
            "price_per_night": rate.get("lowest"),
            "amenities": hotel.get("amenities", [])[:5],
            "link": hotel.get("link"),
        })

    return json.dumps({
        "location": location,
        "check_in": check_in_date or "flexible",
        "check_out": check_out_date or "flexible",
        "hotels": hotels,
    }, indent=2)
