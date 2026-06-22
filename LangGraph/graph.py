from langgraph.graph import StateGraph
from langgraph.graph import START, END

from state import TravelState

from nodes import (
    start_node,
    search_hotels,
    search_flights,
    select_best_option,
    create_itinerary,
    validate_plan,
    validation_router
)

builder = StateGraph(TravelState)

builder.add_node("start_node", start_node)

builder.add_node("search_hotels", search_hotels)

builder.add_node("search_flights", search_flights)

builder.add_node("select_best_option", select_best_option)

builder.add_node("create_itinerary", create_itinerary)

builder.add_node("validate_plan", validate_plan)

# START

builder.add_edge(
    START,
    "start_node"
)

# PARALLEL

builder.add_edge(
    "start_node",
    "search_hotels"
)

builder.add_edge(
    "start_node",
    "search_flights"
)

# MERGE

builder.add_edge(
    "search_hotels",
    "select_best_option"
)

builder.add_edge(
    "search_flights",
    "select_best_option"
)

builder.add_edge(
    "select_best_option",
    "create_itinerary"
)

builder.add_edge(
    "create_itinerary",
    "validate_plan"
)

# CONDITIONAL

builder.add_conditional_edges(
    "validate_plan",
    validation_router,
    {
        "approved": END,
        "retry": "select_best_option"
    }
)

graph = builder.compile()