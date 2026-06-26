import os
import requests
from typing import List


def search_web(query: str) -> List[str]:
    """
    Search the web using SerpAPI.
    Falls back to mock results if SERPAPI_KEY is not set (demo mode).
    """
    api_key = os.getenv("SERPAPI_KEY", "")

    if not api_key:
        print("[Tool] SerpAPI key not set — using demo results")
        return [
            f"[Result 1] What is '{query}': A comprehensive overview of the topic covering its core principles, history, and modern applications in software engineering.",
            f"[Result 2] '{query}' explained: Key concepts include modular design, scalability considerations, and best practices adopted by leading technology companies.",
            f"[Result 3] Latest developments in '{query}': Recent research shows significant improvements in performance and usability, with several open-source frameworks gaining traction.",
            f"[Result 4] How to use '{query}' in production: Step-by-step guide with real-world examples from companies like Google, Meta, and OpenAI.",
            f"[Result 5] Common mistakes when working with '{query}': Expert advice on pitfalls to avoid and patterns that have proven effective at scale.",
        ]

    params = {
        "q": query,
        "api_key": api_key,
        "num": 5,
        "engine": "google",
    }

    try:
        response = requests.get(
            "https://serpapi.com/search", params=params, timeout=10
        )
        data = response.json()

        results = []
        for item in data.get("organic_results", [])[:5]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"**{title}**\n{snippet}\nSource: {link}")

        return results if results else ["No results found for this query"]

    except Exception as e:
        print(f"[Tool] SerpAPI error: {e}")
        return [f"Search failed: {str(e)}"]
