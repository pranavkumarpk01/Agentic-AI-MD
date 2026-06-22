from typing import TypedDict, List

class TravelState(TypedDict):
    destination: str
    budget: int

    hotels: List[str]
    flights: List[str]

    selected_hotel: str
    selected_flight: str

    itinerary: str

    validated: bool

