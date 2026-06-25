# ============================================================
# main.py
# Entry point for the Travel AI Assistant
#
# Usage:
#   python main.py              — interactive chat mode
#   python main.py --debug      — show full message state each turn
#   python main.py --stream     — stream token-by-token output
# ============================================================

import sys
import uuid
import argparse
from langchain_core.messages import HumanMessage

from config.settings import OLLAMA_MODEL, AGENT_VERBOSE, MAX_ITERATIONS
from graph.builder import build_graph, get_graph_ascii
from tools import ALL_TOOLS
from utils.pretty_print import (
    console,
    print_header,
    print_final_answer,
    print_user_input,
    print_graph_info,
    print_separator,
    print_messages_debug,
)


def run_agent(
    query: str,
    graph,
    thread_id: str,
    debug: bool = False,
) -> str:
    """
    Run the agent on a single query.

    Args:
        query: User's travel question
        graph: Compiled LangGraph
        thread_id: Session ID for memory (used with MemorySaver)
        debug: If True, print full message state after each step

    Returns:
        Final answer string from the LLM
    """

    # ── Build initial state ──────────────────────────────────
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_query": query,
    }

    # ── Config for memory checkpointing ─────────────────────
    config = {"configurable": {"thread_id": thread_id}}

    final_answer = ""

    # ── Stream through graph events ──────────────────────────
    # stream_mode="values" gives us the full state after each node
    # stream_mode="updates" gives us just what changed (also useful)
    for event in graph.stream(
        initial_state,
        config=config,
        stream_mode="values",   # emit full state after each node
    ):
        messages = event.get("messages", [])

        if debug and messages:
            print_messages_debug(messages)

        # Extract the last message
        if messages:
            last_msg = messages[-1]

            # Capture final answer (AIMessage with no tool_calls)
            if hasattr(last_msg, "content") and hasattr(last_msg, "tool_calls"):
                tool_calls = getattr(last_msg, "tool_calls", [])
                if not tool_calls and last_msg.content:
                    final_answer = last_msg.content

    return final_answer


def run_streaming_agent(query: str, graph, thread_id: str) -> str:
    """
    Run agent with token-by-token streaming output.
    Shows the LLM's response as it's being generated.
    """
    from langchain_core.messages import AIMessageChunk

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "user_query": query,
    }
    config = {"configurable": {"thread_id": thread_id}}

    console.print("\n[bold magenta]✈️ Travel Assistant:[/bold magenta] ", end="")

    full_response = ""
    # astream_events gives fine-grained streaming control
    # For synchronous streaming, we use stream with messages mode
    for chunk in graph.stream(
        initial_state,
        config=config,
        stream_mode="messages",   # stream individual message tokens
    ):
        if isinstance(chunk, tuple) and len(chunk) == 2:
            msg, metadata = chunk
            if hasattr(msg, "content") and msg.content:
                # Only print AIMessage chunks (not tool results)
                if not hasattr(msg, "tool_call_id"):  # not a ToolMessage
                    print(msg.content, end="", flush=True)
                    full_response += msg.content

    print()  # newline after streaming
    return full_response


def interactive_mode(debug: bool = False, stream: bool = False):
    """
    Interactive chat loop — keeps conversation going until user exits.
    Uses MemorySaver for multi-turn memory.
    """

    # Print startup info
    print_graph_info(OLLAMA_MODEL, ALL_TOOLS)
    print(get_graph_ascii())

    console.print(
        "[dim]Tips: Ask about weather, hotels, flights, or directions. "
        "Type 'quit' or 'exit' to stop.[/dim]\n"
    )

    # Build graph WITH memory for multi-turn conversation
    graph = build_graph(use_memory=True)

    # Each session gets a unique thread_id
    session_id = str(uuid.uuid4())[:8]
    console.print(f"[dim]Session ID: {session_id}[/dim]\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"quit", "exit", "q", "bye"}:
                console.print("[bold cyan]Goodbye! Safe travels! ✈️[/bold cyan]")
                break

            # Special commands
            if user_input.lower() == "debug":
                debug = not debug
                console.print(f"[dim]Debug mode: {'ON' if debug else 'OFF'}[/dim]")
                continue

            if user_input.lower() == "new session":
                session_id = str(uuid.uuid4())[:8]
                console.print(f"[dim]New session started: {session_id}[/dim]")
                continue

            print_user_input(user_input)
            print_separator()

            # Run the agent
            if stream:
                answer = run_streaming_agent(user_input, graph, session_id)
            else:
                answer = run_agent(user_input, graph, session_id, debug=debug)
                if answer:
                    print_final_answer(answer)

            print_separator()

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Interrupted. Goodbye! ✈️[/bold cyan]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            if debug:
                import traceback
                traceback.print_exc()


def single_query_mode(query: str, debug: bool = False):
    """Run a single query and exit. Useful for scripting."""
    graph = build_graph(use_memory=False)
    thread_id = str(uuid.uuid4())[:8]

    console.print(f"\n[bold]Query:[/bold] {query}\n")
    print_separator()

    answer = run_agent(query, graph, thread_id, debug=debug)
    print_final_answer(answer)


# ── CLI Entrypoint ───────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Travel AI Assistant — LangGraph + Ollama + SerpAPI"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default="",
        help="Single query mode: run one question and exit",
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Show full message state table after each graph step",
    )
    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="Stream LLM output token-by-token",
    )

    args = parser.parse_args()

    print_header("✈️  Travel AI Assistant — LangGraph + Ollama + SerpAPI")

    if args.query:
        # Single query mode
        single_query_mode(args.query, debug=args.debug)
    else:
        # Interactive mode (default)
        interactive_mode(debug=args.debug, stream=args.stream)