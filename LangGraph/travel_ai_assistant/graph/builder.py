from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from graph.nodes import llm_node, tool_node
from graph.edges import should_continue


def build_graph():
    """
    Graph topology:

        START → llm_node → (should_continue) → tools → llm_node → ...
                                             ↘ END
    """
    graph = StateGraph(AgentState)

    graph.add_node("llm",   llm_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "llm")

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {"tools": "tools", "__end__": END},
    )

    graph.add_edge("tools", "llm")

    return graph.compile()
