# ============================================================
# graph/state.py
#
# CONCEPT: Tool Messages / State
#   - AgentState is the shared data container for the entire graph
#   - Every node READS from state and RETURNS updates to state
#   - `messages` uses Annotated[list, add_messages] which is a
#     LangGraph reducer — it APPENDS new messages instead of replacing
#
# Message flow through state:
#   HumanMessage → [AIMessage with tool_calls] → ToolMessage(s) → AIMessage (final)
#
# Message types used:
#   HumanMessage  — user input
#   AIMessage     — LLM response (may contain tool_calls)
#   ToolMessage   — result from a tool execution (has tool_call_id)
#   SystemMessage — system prompt (injected in llm_node)
# ============================================================

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The state object that flows through every node in the LangGraph.

    Fields:
        messages: Full conversation history including:
                  - HumanMessage (user inputs)
                  - AIMessage (LLM responses, possibly with tool_calls)
                  - ToolMessage (results from tool executions)
                  - SystemMessage (system prompt, injected once)

                  The `add_messages` reducer APPENDS new messages to the list.
                  This is the core mechanism for ReAct — we accumulate:
                  Thought (AIMessage) → Action (tool_call) →
                  Observation (ToolMessage) → Thought → ...

        iteration_count: Tracks how many ReAct loop iterations have run.
                         Used to enforce MAX_ITERATIONS safety limit.

        user_query: The original raw user query, preserved for reference.
    """

    # Annotated with add_messages reducer:
    # - New messages returned by nodes are APPENDED, not replaced
    # - This builds up the full ReAct conversation chain
    messages: Annotated[list[BaseMessage], add_messages]

    # Safety counter — prevents infinite loops
    iteration_count: int

    # The original user query (useful for logging/debugging)
    user_query: str