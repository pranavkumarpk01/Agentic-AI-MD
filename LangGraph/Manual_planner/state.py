from typing import TypedDict, List

class TravelState(TypedDict):

    user_id: str

    destination: str

    budget: int

    hotels: List[str]

    flights: List[str]

    selected_hotel: str

    selected_flight: str

    itinerary: str

    validated: bool

    approved: bool

    user_preference: str