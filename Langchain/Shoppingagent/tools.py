from langchain.tools import tool

from serpapi import GoogleSearch

from duckduckgo_search import DDGS

from dotenv import load_dotenv

import os

load_dotenv()


@tool
def google_price_search(product: str):
    """
    Search Google Shopping and web for latest prices.
    """

    params = {
        "engine": "google_shopping",
        "q": product,
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    shopping_results = results.get(
        "shopping_results",
        []
    )

    output = []

    for item in shopping_results[:5]:

        title = item.get("title", "")
        price = item.get("price", "")
        source = item.get("source", "")

        output.append(
            f"{title} | {price} | {source}"
        )

    if not output:
        return "No shopping results found"

    return "\n".join(output)


@tool
def web_search(query: str):
    """
    Search Google.
    """

    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    organic = results.get(
        "organic_results",
        []
    )

    output = []

    for item in organic[:5]:

        title = item.get("title", "")
        link = item.get("link", "")

        output.append(
            f"{title} - {link}"
        )

    return "\n".join(output)


@tool
def compare_prices(price_text: str):
    """
    Compare prices and determine the cheapest option.
    """

    import re

    prices = re.findall(
        r"\d[\d,]*",
        price_text
    )

    if not prices:
        return "No prices found."

    numbers = [
        int(
            p.replace(",", "")
        )
        for p in prices
    ]

    cheapest = min(numbers)

    return (
        f"Cheapest detected price: ₹{cheapest}"
    )


TOOLS = [
    google_price_search,
    web_search,
    compare_prices
]