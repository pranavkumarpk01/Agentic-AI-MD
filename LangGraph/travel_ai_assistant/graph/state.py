from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # add_messages reducer APPENDS new messages instead of replacing the list
    # Message flow: HumanMessage → AIMessage (with tool_calls) → ToolMessage → AIMessage (final)
    messages: Annotated[list[BaseMessage], add_messages]
