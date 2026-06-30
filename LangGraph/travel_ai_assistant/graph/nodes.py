from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT
from travel_tools import ALL_TOOLS
from graph.state import AgentState


# Initialize the LLM and bind tools to it
# bind_tools() tells the LLM what tools are available and their schemas
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, temperature=0)
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# ToolNode automatically handles: reading tool_calls from AIMessage,
# calling the right tool, and returning a ToolMessage with the result
tool_node = ToolNode(ALL_TOOLS)


def llm_node(state: AgentState) -> dict:
    """
    The reasoning node. Calls the LLM with the full message history.
    If the LLM wants to call a tool, AIMessage.tool_calls will be non-empty.
    If the LLM has enough info, AIMessage.tool_calls will be empty (final answer).
    """
    print("\n[LLM thinking...]")

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"[Tool call] {tc['name']}({tc['args']})")
    else:
        print("[LLM has final answer]")

    return {"messages": [response]}
