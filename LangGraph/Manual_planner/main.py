from graph import graph

state = {

    "user_id": "pranav",

    "destination": "Goa",

    "budget": 50000,

    "hotels": [],

    "flights": [],

    "selected_hotel": "",

    "selected_flight": "",

    "itinerary": "",

    "validated": False,

    "approved": False,

    "user_preference": ""
}

config = {
    "configurable": {
        "thread_id": "trip_001"
    }
}

print("\nGRAPH STRUCTURE\n")

print(
    graph.get_graph().draw_ascii()
)

print("\nEXECUTING GRAPH\n")

result = graph.invoke(
    state,
    config=config
)

print("\nFINAL RESULT\n")

print(result["itinerary"])