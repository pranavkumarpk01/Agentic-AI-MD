# ============================================================
# graph/nodes.py
#
# CONCEPT: LLM Integration + Tool Execution
#
# Two nodes in the graph:
#
# 1. llm_node (LLM Node)
#    - Initializes Ollama LLM with bind_tools()
#    - Injects system prompt + full message history
#    - Returns AIMessage (may contain tool_calls for ReAct)
#
# 2. tool_node (Tool Calling Node)
#    - Receives AIMessage with tool_calls from the LLM
#    - Dispatches to the correct tool function
#    - Returns ToolMessage with the result
#    - LangGraph's built-in ToolNode handles all of this automatically
#
# CONCEPT: ReAct Reasoning
#    The LLM node uses ReAct implicitly:
#    - It REASONS about what to do (Thought in the AIMessage text)
#    - It takes an ACTION (tool_call in AIMessage.tool_calls)
#    - After the tool runs, it gets an OBSERVATION (ToolMessage)
#    - It reasons again — loop continues until no tool_calls
# ============================================================

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    OLLAMA_NUM_PREDICT,
    SYSTEM_PROMPT,
    AGENT_VERBOSE,
    MAX_ITERATIONS,
)
from tools import ALL_TOOLS
from graph.state import AgentState
from utils.pretty_print import print_llm_thinking, print_tool_call, print_warning


# ── Initialize LLM (done once at module load) ────────────────
# ChatOllama connects to local Ollama server
# bind_tools() injects tool schemas into the LLM's context so it
# knows what tools are available and how to call them
_llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=OLLAMA_TEMPERATURE,
    num_predict=OLLAMA_NUM_PREDICT,
)

# bind_tools tells the LLM about all available tools:
# - Tool name (used in tool_calls)
# - Tool description (docstring — LLM reads this to decide when to use it)
# - Tool input schema (type hints — LLM fills these in)
llm_with_tools = _llm.bind_tools(ALL_TOOLS)


# ── Node 1: LLM Node ─────────────────────────────────────────
def llm_node(state: AgentState) -> dict:
    """
    The reasoning node — heart of the ReAct loop.

    Flow:
      1. Read current messages from state
      2. Prepend system prompt (if not already there)
      3. Call Ollama LLM with full history + tools bound
      4. Return AIMessage to be appended to state

    If the LLM decides to use a tool:
      → AIMessage.tool_calls will be non-empty
      → The edge router will send us to tool_node

    If the LLM has enough info to answer:
      → AIMessage.tool_calls will be empty
      → The edge router will send us to END
    """

    messages = state["messages"]
    iteration = state.get("iteration_count", 0)

    # ── Safety: check iteration limit ───────────────────────
    if iteration >= MAX_ITERATIONS:
        print_warning(f"Max iterations ({MAX_ITERATIONS}) reached. Forcing final answer.")
        # Force a final response by sending a hint
        forced_prompt = SystemMessage(
            content=(
                f"[SYSTEM: You have used {iteration} iterations. "
                "You MUST now provide a final answer based on the information "
                "you have gathered so far. Do NOT call any more tools.]"
            )
        )
        messages = messages + [forced_prompt]

    # ── Build full message list with system prompt ───────────
    # Only inject system prompt if it's the first iteration
    # (avoid duplicating it on every loop)
    if iteration == 0:
        system_msg = SystemMessage(content=SYSTEM_PROMPT)
        full_messages = [system_msg] + messages
    else:
        full_messages = messages

    if AGENT_VERBOSE:
        print_llm_thinking(iteration, len(messages))

    # ── Invoke LLM ───────────────────────────────────────────
    # This is the actual Ollama API call
    # The LLM receives: system prompt + all messages so far
    # It returns an AIMessage with optional tool_calls
    response = llm_with_tools.invoke(full_messages)

    if AGENT_VERBOSE and hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            print_tool_call(tc["name"], tc["args"])

    # ── Return state update ──────────────────────────────────
    # LangGraph merges this with existing state:
    # - messages: add_messages reducer APPENDS the new AIMessage
    # - iteration_count: incremented by 1
    return {
        "messages": [response],
        "iteration_count": iteration + 1,
    }


# ── Node 2: Tool Node ─────────────────────────────────────────
# LangGraph's built-in ToolNode handles everything:
#   1. Reads tool_calls from the last AIMessage in state
#   2. Finds the matching tool from ALL_TOOLS by name
#   3. Calls the tool with the LLM-provided arguments
#   4. Wraps result in a ToolMessage (with matching tool_call_id)
#   5. Returns ToolMessage to be appended to state
#
# The tool_call_id links the ToolMessage back to the specific
# tool_call in the AIMessage — important for multi-tool calls
tool_node = ToolNode(ALL_TOOLS)


# ── Tool node wrapper (for verbose logging) ───────────────────
def tool_node_with_logging(state: AgentState) -> dict:
    """
    Wraps ToolNode with verbose logging.
    Calls the tools and logs what happened.
    """
    if AGENT_VERBOSE:
        # Show which tools are about to be executed
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls"):
            for tc in last_message.tool_calls:
                print(f"\n  🔧 Executing: {tc['name']}({tc['args']})")

    # Execute tools via LangGraph's built-in ToolNode
    result = tool_node.invoke(state)

    if AGENT_VERBOSE:
        # Show tool results summary
        new_messages = result.get("messages", [])
        for msg in new_messages:
            if hasattr(msg, "content"):
                preview = str(msg.content)[:200]
                print(f"\n  📊 Tool Result: {preview}{'...' if len(str(msg.content)) > 200 else ''}")

    return result