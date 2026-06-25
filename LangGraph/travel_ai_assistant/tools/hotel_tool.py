# ============================================================
# tools/hotel_tool.py
#
# CONCEPT: Tool Definition
#   - Searches Google Hotels via SerpAPI's dedicated hotel engine
#   - Supports filters: check-in/check-out dates, price range, rating
#   - Returns structured list of hotel options with amenities
# ============================================================

import json
from langchain_core.tools import tool
from serpapi import GoogleSearch

from config.settings import SERPAPI_API_KEY, SERP_MAX_RESULTS


@tool
def hotel_search(
    location: str,
    check_in_date: str = "",
    check_out_date: str = "",
    max_price: int = 0,
    min_rating: float = 0.0,
    adults: int = 2,
) -> str:
    """
    Search for hotels at a travel destination using Google Hotels.

    Use this tool when the user asks about:
    - Hotels at a destination
    - Accommodation options with price filters
    - Luxury or budget hotels
    - Hotels near specific landmarks
    - Available rooms for specific dates

    Args:
        location: City or area to search hotels (e.g., "Paris", "Goa Beach", "Manhattan NYC")
        check_in_date: Check-in date in YYYY-MM-DD format (e.g., "2025-08-15"). Leave empty if not specified.
        check_out_date: Check-out date in YYYY-MM-DD format (e.g., "2025-08-20"). Leave empty if not specified.
        max_price: Maximum price per night in USD (0 = no limit)
        min_rating: Minimum hotel star rating (0.0 to 5.0, e.g., 4.0 for 4-star+)
        adults: Number of adult guests (default: 2)

    Returns:
        JSON string with list of hotels including name, price, rating, amenities, and booking link
    """

    if not location or not location.strip():
        return json.dumps({"error": "Location cannot be empty"})

    # ── Build SerpAPI params for Google Hotels engine ────────
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {location}",
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "gl": "us",
        "currency": "USD",
        "adults": str(adults),
    }

    # Add optional date filters
    if check_in_date:
        params["check_in_date"] = check_in_date
    if check_out_date:
        params["check_out_date"] = check_out_date

    # Add price filter
    if max_price > 0:
        params["max_price"] = str(max_price)

    # Add rating filter (Google Hotels uses 3.5, 4.0, 4.5 thresholds)
    if min_rating >= 4.5:
        params["rating"] = "9"   # 4.5+
    elif min_rating >= 4.0:
        params["rating"] = "8"   # 4.0+
    elif min_rating >= 3.5:
        params["rating"] = "7"   # 3.5+

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        hotels_data = {
            "location": location,
            "search_params": {
                "check_in": check_in_date or "flexible",
                "check_out": check_out_date or "flexible",
                "adults": adults,
                "max_price": f"${max_price}/night" if max_price else "no limit",
                "min_rating": f"{min_rating}+" if min_rating else "any",
            },
            "hotels": [],
        }

        # ── Parse hotel properties from SerpAPI ──────────────
        properties = results.get("properties", [])

        if not properties:
            # Fallback: try organic results
            return _hotel_organic_fallback(location, results)

        for hotel in properties[:SERP_MAX_RESULTS]:
            hotel_info = {
                "name": hotel.get("name", "Unknown"),
                "type": hotel.get("type", "Hotel"),
                "description": hotel.get("description", ""),
                "link": hotel.get("link", ""),
                "gps_coordinates": hotel.get("gps_coordinates", {}),
            }

            # Price info
            rate_per_night = hotel.get("rate_per_night", {})
            if rate_per_night:
                hotel_info["price_per_night"] = rate_per_night.get("lowest", "N/A")
                hotel_info["price_before_taxes"] = rate_per_night.get("before_taxes_fees", "N/A")

            # Rating
            hotel_info["rating"] = hotel.get("overall_rating", "N/A")
            hotel_info["reviews"] = hotel.get("reviews", "N/A")
            hotel_info["stars"] = hotel.get("hotel_class", "N/A")

            # Location details
            hotel_info["nearby_places"] = [
                place.get("name", "") for place in hotel.get("nearby_places", [])[:3]
            ]

            # Amenities
            hotel_info["amenities"] = hotel.get("amenities", [])[:8]

            # Images
            images = hotel.get("images", [])
            hotel_info["thumbnail"] = images[0].get("thumbnail", "") if images else ""

            hotels_data["hotels"].append(hotel_info)

        hotels_data["total_found"] = len(properties)
        hotels_data["showing"] = len(hotels_data["hotels"])

        return json.dumps(hotels_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Hotel search failed: {str(e)}",
            "location": location,
            "tip": "Check SERPAPI_API_KEY and try a broader location name",
        })


def _hotel_organic_fallback(location: str, results: dict) -> str:
    """Fallback to organic search results if hotel engine returns no properties."""
    organic = results.get("organic_results", [])
    fallback_data = {
        "location": location,
        "source": "organic_fallback",
        "note": "Structured hotel data not available, showing search snippets",
        "results": [],
    }
    for r in organic[:4]:
        fallback_data["results"].append({
            "title": r.get("title", ""),
            "snippet": r.get("snippet", ""),
            "link": r.get("link", ""),
        })
    return json.dumps(fallback_data, indent=2)