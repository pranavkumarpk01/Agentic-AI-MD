from graph import graph

state = {
    "destination": "Goa",
    "budget": 50000,

    "hotels": [],
    "flights": [],

    "selected_hotel": "",
    "selected_flight": "",

    "itinerary": "",

    "validated": False
}

result = graph.invoke(state)

print("\nFINAL RESULT\n")

print(result["itinerary"])