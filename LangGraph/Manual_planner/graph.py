from langgraph.graph import StateGraph
from langgraph.graph import START, END

from state import TravelState

from checkpointer import checkpointer

from nodes import (
    start_node,
    search_hotels,
    search_flights,
    select_best_option,
    create_itinerary,
    validate_plan,
    validation_router,

    load_memory,
    save_memory,

    approval_node,
    approval_router
)

builder = StateGraph(TravelState)

# ------------------------------------------------
# Nodes
# ------------------------------------------------

builder.add_node(
    "load_memory",
    load_memory
)

builder.add_node(
    "start_node",
    start_node
)

builder.add_node(
    "search_hotels",
    search_hotels
)

builder.add_node(
    "search_flights",
    search_flights
)

builder.add_node(
    "select_best_option",
    select_best_option
)

builder.add_node(
    "create_itinerary",
    create_itinerary
)

builder.add_node(
    "validate_plan",
    validate_plan
)

builder.add_node(
    "approval_node",
    approval_node
)

builder.add_node(
    "save_memory",
    save_memory
)

# ------------------------------------------------
# Start Flow
# ------------------------------------------------

builder.add_edge(
    START,
    "load_memory"
)

builder.add_edge(
    "load_memory",
    "start_node"
)

# ------------------------------------------------
# Parallel Execution
# ------------------------------------------------

builder.add_edge(
    "start_node",
    "search_hotels"
)

builder.add_edge(
    "start_node",
    "search_flights"
)

# ------------------------------------------------
# Merge
# ------------------------------------------------

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

# ------------------------------------------------
# Validation Routing
# ------------------------------------------------

builder.add_conditional_edges(
    "validate_plan",
    validation_router,
    {
        "approved": "approval_node",
        "retry": "select_best_option"
    }
)

# ------------------------------------------------
# Human Approval Routing
# ------------------------------------------------

builder.add_conditional_edges(
    "approval_node",
    approval_router,
    {
        "approved": "save_memory",
        "rejected": END
    }
)

# ------------------------------------------------
# Save Memory -> END
# ------------------------------------------------

builder.add_edge(
    "save_memory",
    END
)

# ------------------------------------------------
# Compile
# ------------------------------------------------

graph = builder.compile(
    checkpointer=checkpointer
)