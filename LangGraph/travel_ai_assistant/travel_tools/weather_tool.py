import json
from langchain_core.tools import tool
from serpapi import GoogleSearch
from config.settings import SERPAPI_API_KEY


@tool
def weather_search(location: str, days: int = 3) -> str:
    """
    Search for current weather conditions and forecasts for a travel destination.

    Use this when the user asks about weather, what to pack, or best time to visit.

    Args:
        location: City or destination (e.g., "Paris", "Goa, India", "Tokyo")
        days: Number of forecast days (default: 3)
    """
    params = {
        "engine": "google",
        "q": f"weather in {location} {days} day forecast",
        "api_key": SERPAPI_API_KEY,
        "hl": "en",
        "gl": "us",
    }

    results = GoogleSearch(params).get_dict()

    # Google often returns a structured weather panel
    if "answer_box" in results:
        answer = results["answer_box"]
        return json.dumps({
            "location": location,
            "temperature": answer.get("temperature"),
            "unit": answer.get("unit"),
            "condition": answer.get("weather"),
            "humidity": answer.get("humidity"),
            "wind": answer.get("wind"),
            "forecast": answer.get("forecast", []),
        }, indent=2)

    # Fall back to organic search snippets
    snippets = [
        {"title": r.get("title"), "snippet": r.get("snippet")}
        for r in results.get("organic_results", [])[:3]
    ]
    return json.dumps({"location": location, "results": snippets}, indent=2)
