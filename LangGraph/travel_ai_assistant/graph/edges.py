# ============================================================
# graph/edges.py
#
# CONCEPT: ReAct Reasoning — The Routing Logic
#
# Edges control FLOW between nodes. Two types:
#
# 1. Regular edges: always go from A → B
#    Example: tool_node → llm_node (after tool executes, always go back to LLM)
#
# 2. Conditional edges: routing function decides which node to go to
#    Example: llm_node → (tool_node OR END)
#             decided by: does the AIMessage contain tool_calls?
#
# This IS the ReAct loop:
#   llm_node
#     ├─ has tool_calls → tool_node → llm_node (loop)
#     └─ no tool_calls  → END       (done)
# ============================================================

from typing import Literal
from langchain_core.messages import AIMessage

from graph.state import AgentState


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """
    Conditional edge router — implements the ReAct loop decision.

    Called after every llm_node execution. Examines the last message
    in state and decides:

    → "tools"    if LLM wants to call a tool (has tool_calls)
                 → routes to tool_node for execution

    → "__end__"  if LLM has finished reasoning (no tool_calls)
                 → terminates the graph, final answer is ready

    This function is the core of ReAct:
      The LLM ACTS by emitting tool_calls (Action)
      We route to tools which return results (Observation)
      We loop back to LLM which reasons again (Thought)
      Until LLM decides no more tools needed (Final Answer)

    Args:
        state: Current AgentState with full message history

    Returns:
        "tools"     → go to tool_node
        "__end__"   → terminate graph
    """

    messages = state["messages"]

    if not messages:
        # No messages — shouldn't happen, but terminate safely
        return "__end__"

    last_message = messages[-1]

    # Check if the last message is an AIMessage with tool_calls
    # tool_calls is a list of {"name": ..., "args": ..., "id": ...} dicts
    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", [])
        if tool_calls and len(tool_calls) > 0:
            # LLM wants to use tools — continue the ReAct loop
            return "tools"

    # No tool_calls — LLM has produced a final answer
    return "__end__"


def after_tools(state: AgentState) -> Literal["llm"]:
    """
    Edge after tool_node — always routes back to llm_node.

    After tools execute and return results (ToolMessages),
    we ALWAYS go back to the LLM so it can:
    1. Read the tool results
    2. Decide if more tools are needed, OR
    3. Formulate the final answer

    This is a simple always-go-to-llm edge, but defined as a
    function for clarity and potential future logic.
    """
    return "llm"