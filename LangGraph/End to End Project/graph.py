from langgraph.graph import StateGraph, START, END

from state import ResearchState
from checkpointer import checkpointer
from nodes import (
    load_memory_node,
    decide_search_node,
    search_web_node,
    summarize_node,
    extract_memory_node,
    human_approval_node,
    save_memory_node,
    save_to_db_node,
    search_router,
    approval_router,
)

# ---- Build the graph -------------------------------------------------------

builder = StateGraph(ResearchState)

# ---- Add nodes -------------------------------------------------------------

builder.add_node("load_memory",     load_memory_node)
builder.add_node("decide_search",   decide_search_node)
builder.add_node("search_web",      search_web_node)
builder.add_node("summarize",       summarize_node)
builder.add_node("extract_memory",  extract_memory_node)
builder.add_node("human_approval",  human_approval_node)
builder.add_node("save_memory",     save_memory_node)
builder.add_node("save_to_db",      save_to_db_node)   # <-- INTENTIONALLY BROKEN

# ---- Wire edges ------------------------------------------------------------

# Always start by loading what we know
builder.add_edge(START, "load_memory")
builder.add_edge("load_memory", "decide_search")

# LLM decides: search the web, or skip straight to summarize?
builder.add_conditional_edges(
    "decide_search",
    search_router,
    {
        "search":      "search_web",
        "skip_search": "summarize",
    },
)

builder.add_edge("search_web",     "summarize")
builder.add_edge("summarize",      "extract_memory")
builder.add_edge("extract_memory", "human_approval")

# Human can approve (save to memory) or reject (discard)
builder.add_conditional_edges(
    "human_approval",
    approval_router,
    {
        "approved": "save_memory",
        "rejected": END,
    },
)

builder.add_edge("save_memory", "save_to_db")
builder.add_edge("save_to_db",  END)

# ---- Compile ---------------------------------------------------------------
# interrupt_before=["human_approval"] pauses the graph before that node runs.
# The frontend can then POST /approve to inject human_approved=True/False
# and resume by calling graph.stream(None, config).

graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_approval"],
)
