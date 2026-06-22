from state import TravelState

def start_node(state: TravelState):
    print("\n[Node] START NODE")
    return {} # Returning empty dict means no state change needed

def search_hotels(state: TravelState):
    print("\n[Node] SEARCH HOTELS NODE")
    # Return the key you want to update
    return {"hotels": ["Taj Goa", "Marriott Goa", "Novotel Goa"]}

def search_flights(state: TravelState):
    print("\n[Node] SEARCH FLIGHTS NODE")
    return {"flights": ["Indigo 6E123", "Air India AI245"]}

def select_best_option(state: TravelState):
    print("\n[Node] SELECT BEST OPTION NODE")
    return {
        "selected_hotel": state["hotels"][0],
        "selected_flight": state["flights"][0]
    }

def create_itinerary(state: TravelState):
    print("\n[Node] CREATE ITINERARY NODE")
    itinerary = f"Destination: {state['destination']}\nHotel: {state['selected_hotel']}\nFlight: {state['selected_flight']}"
    return {"itinerary": itinerary}

def validate_plan(state: TravelState):
    print("\n[Node] VALIDATE PLAN NODE")
    if state.get("selected_hotel") and state.get("selected_flight"):
        return {"validated": True}
    return {"validated": False}

# --- ADD THIS MISSING ROUTER ---
def validation_router(state: TravelState):
    print("\n[Router] Checking validation status...")
    if state["validated"]:
        return "approved"
    else:
        return "retry"