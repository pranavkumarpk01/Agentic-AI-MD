import os
import requests

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

SERPER_API_KEY = os.getenv(
    "SERPER_API_KEY"
)


@tool
def destination_search(
    destination: str
) -> str:
    """
    Search attractions in a destination.
    """

    url = "https://google.serper.dev/search"

    payload = {
        "q": f"tourist attractions in {destination}"
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return response.text


@tool
def hotel_search(
    destination: str
) -> str:
    """
    Search hotels in a destination.
    """

    url = "https://google.serper.dev/search"

    payload = {
        "q": f"best hotels in {destination}"
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return response.text


@tool
def budget_calculator(
    costs: str
) -> str:
    """
    Example:
    3000,2000,1000
    """

    values = [
        int(x.strip())
        for x in costs.split(",")
    ]

    return f"Total Budget: ₹{sum(values)}"


tools = [
    destination_search,
    hotel_search,
    budget_calculator
]