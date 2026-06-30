from langchain_core.messages import AIMessage
from graph.state import AgentState


def should_continue(state: AgentState) -> str:
    """
    Decides what to do after the LLM node runs.
    - If the LLM called a tool  → go to "tools" node
    - If the LLM gave an answer → go to "__end__" (done)
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"
