# ============================================================
# tools/weather_tool.py
#
# CONCEPT: Tool Definition
#   - @tool decorator turns a Python function into a LangChain tool
#   - The docstring becomes the tool description the LLM reads
#   - Type hints on arguments become the tool's input schema
#   - The LLM decides WHEN to call this and with WHAT arguments
#
# CONCEPT: Tool Execution
#   - SerpAPI hits Google's weather knowledge panel
#   - Returns structured weather data (temp, condition, humidity, etc.)
# ============================================================

import json
from langchain_core.tools import tool
from serpapi import GoogleSearch

from config.settings import SERPAPI_API_KEY, SERP_MAX_RESULTS


@tool
def weather_search(location: str, days: int = 3) -> str:
    """
    Search for current weather conditions and forecasts for a travel destination.

    Use this tool when the user asks about:
    - Current weather at a destination
    - Weather forecast for trip planning
    - Best time to visit a place
    - What to pack (hot/cold/rainy)

    Args:
        location: City or destination name (e.g., "Paris, France", "Goa, India", "Tokyo")
        days: Number of forecast days to retrieve (default: 3, max: 7)

    Returns:
        JSON string with current conditions and forecast data
    """

    # ── Validate inputs ──────────────────────────────────────
    if not location or not location.strip():
        return json.dumps({"error": "Location cannot be empty"})

    days = max(1, min(days, 7))  # clamp to 1-7

    # ── Build SerpAPI params ─────────────────────────────────
    # SerpAPI's weather engine hits Google's weather knowledge panel
    params = {
        "engine": "google",
        "q": f"weather in {location} {days} day forecast",
        "api_key": SERPAPI_API_KEY,
        "hl": "en",          # language: english
        "gl": "us",          # country: US (affects result format)
        "num": SERP_MAX_RESULTS,
    }

    try:
        # ── Execute search ───────────────────────────────────
        search = GoogleSearch(params)
        results = search.get_dict()

        # ── Extract weather panel (primary source) ───────────
        weather_data = {}

        # Google often returns a structured weather panel
        if "answer_box" in results:
            answer = results["answer_box"]
            weather_data["source"] = "google_weather_panel"
            weather_data["location"] = location
            weather_data["current"] = {
                "temperature": answer.get("temperature", "N/A"),
                "unit": answer.get("unit", "°F"),
                "weather": answer.get("weather", "N/A"),
                "humidity": answer.get("humidity", "N/A"),
                "wind": answer.get("wind", "N/A"),
            }

            # Extract forecast if available in the panel
            if "forecast" in answer:
                weather_data["forecast"] = answer["forecast"]

        # ── Fall back to organic results ─────────────────────
        elif "organic_results" in results:
            weather_data["source"] = "organic_search"
            weather_data["location"] = location
            weather_data["snippets"] = []

            for result in results["organic_results"][:3]:
                weather_data["snippets"].append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "source": result.get("source", ""),
                    "link": result.get("link", ""),
                })

        else:
            weather_data = {
                "error": "No weather data found",
                "location": location,
                "suggestion": "Try a more specific location name",
            }

        # ── Add metadata ─────────────────────────────────────
        weather_data["query"] = f"weather in {location}",
        weather_data["days_requested"] = days

        return json.dumps(weather_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Weather search failed: {str(e)}",
            "location": location,
            "tip": "Check your SERPAPI_API_KEY in .env",
        })