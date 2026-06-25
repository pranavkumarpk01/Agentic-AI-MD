# ============================================================
# graph/builder.py
#
# Builds and compiles the LangGraph StateGraph.
#
# Final graph topology:
#
#   START
#     │
#     ▼
#   llm_node  ◄──────────────────────────┐
#     │                                  │
#     │── should_continue() ────────────►│
#     │     ├── "tools"  → tool_node ────┘
#     │     └── "__end__" → END
#     │
#   END
#
# This is a ReAct agent graph:
# - llm_node reasons and optionally emits tool_calls
# - tool_node executes the tools
# - Loop continues until LLM says it's done
# ============================================================

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import AgentState
from graph.nodes import llm_node, tool_node_with_logging
from graph.edges import should_continue


def build_graph(use_memory: bool = False):
    """
    Build and compile the Travel AI Agent StateGraph.

    Args:
        use_memory: If True, attach MemorySaver for multi-turn conversation
                    memory. Each conversation needs a unique thread_id in
                    config = {"configurable": {"thread_id": "session_123"}}

    Returns:
        Compiled LangGraph (CompiledGraph) ready to invoke/stream
    """

    # ── 1. Create StateGraph with our state schema ────────────
    # StateGraph takes the TypedDict that defines what's in state
    graph_builder = StateGraph(AgentState)


    # ── 2. Add Nodes ──────────────────────────────────────────
    # add_node(name, function)
    # The function signature must be: (state: AgentState) → dict
    # The dict returned is merged into state via reducers

    graph_builder.add_node("llm", llm_node)
    graph_builder.add_node("tools", tool_node_with_logging)


    # ── 3. Add Edges ──────────────────────────────────────────

    # Entry point: START → llm_node
    # Every invocation begins at the LLM
    graph_builder.add_edge(START, "llm")

    # Conditional edge from llm_node:
    # should_continue() inspects the last AIMessage and decides:
    #   "tools"   → go to tools node (continue ReAct loop)
    #   "__end__" → terminate graph (final answer ready)
    graph_builder.add_conditional_edges(
        source="llm",            # from this node
        path=should_continue,    # call this function to decide
        path_map={               # map return values to node names
            "tools": "tools",    # "tools" → go to tools node
            "__end__": END,      # "__end__" → terminate
        },
    )

    # After tools execute, ALWAYS return to LLM
    # This closes the ReAct loop: tool result → LLM reasoning
    graph_builder.add_edge("tools", "llm")


    # ── 4. Compile ────────────────────────────────────────────
    # compile() validates the graph structure and returns
    # a runnable object with .invoke(), .stream(), .astream()

    if use_memory:
        # MemorySaver persists state between invocations
        # Enables multi-turn conversation with context retention
        checkpointer = MemorySaver()
        compiled_graph = graph_builder.compile(checkpointer=checkpointer)
    else:
        compiled_graph = graph_builder.compile()

    return compiled_graph


def get_graph_ascii() -> str:
    """Return ASCII visualization of the graph topology."""
    return """
    ╔════════════════════════════════════════╗
    ║       Travel AI Agent — Graph          ║
    ╠════════════════════════════════════════╣
    ║                                        ║
    ║   START                                ║
    ║     │                                  ║
    ║     ▼                                  ║
    ║  ┌──────────┐                          ║
    ║  │ llm_node │ ◄──────────────┐         ║
    ║  └─────┬────┘                │         ║
    ║        │                     │         ║
    ║   should_continue()          │         ║
    ║        ├── "tools"           │         ║
    ║        │     ▼               │         ║
    ║        │  ┌──────────┐       │         ║
    ║        │  │tool_node │ ──────┘         ║
    ║        │  │ weather  │                 ║
    ║        │  │ hotels   │                 ║
    ║        │  │ flights  │                 ║
    ║        │  │ maps     │                 ║
    ║        │  └──────────┘                 ║
    ║        │                               ║
    ║        └── "__end__"                   ║
    ║               ▼                        ║
    ║             END                        ║
    ╚════════════════════════════════════════╝
    """