# ============================================================
# utils/pretty_print.py
# Rich-based colored terminal output for agent reasoning steps
# ============================================================

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

console = Console()


def print_header(title: str):
    """Print a styled header panel."""
    console.print(Panel(
        f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(0, 2),
    ))


def print_llm_thinking(iteration: int, message_count: int):
    """Print LLM reasoning step indicator."""
    console.print(
        f"\n[bold yellow]🧠 LLM Thinking[/bold yellow] "
        f"[dim](iteration {iteration + 1}, {message_count} messages in context)[/dim]"
    )


def print_tool_call(tool_name: str, args: dict):
    """Print tool call details."""
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    console.print(
        f"[bold green]🔧 Tool Call:[/bold green] "
        f"[cyan]{tool_name}[/cyan]([yellow]{args_str}[/yellow])"
    )


def print_tool_result(tool_name: str, result: str):
    """Print tool result (truncated for readability)."""
    preview = result[:300] + "..." if len(result) > 300 else result
    console.print(Panel(
        f"[dim]{preview}[/dim]",
        title=f"[green]📊 Result from {tool_name}[/green]",
        border_style="green",
        padding=(0, 1),
    ))


def print_final_answer(answer: str):
    """Print the final agent response."""
    console.print(Panel(
        answer,
        title="[bold magenta]✈️ Travel Assistant[/bold magenta]",
        border_style="magenta",
        padding=(1, 2),
    ))


def print_user_input(text: str):
    """Print user input styled."""
    console.print(f"\n[bold blue]👤 You:[/bold blue] {text}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold red]⚠️  Warning:[/bold red] [yellow]{message}[/yellow]")


def print_separator():
    """Print a visual separator."""
    console.print("[dim]" + "─" * 60 + "[/dim]")


def print_messages_debug(messages: list):
    """Debug: print all messages in the current state."""
    table = Table(title="Current Message State", box=box.ROUNDED)
    table.add_column("Index", style="dim", width=6)
    table.add_column("Type", style="cyan", width=15)
    table.add_column("Content Preview", style="white")

    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        content = str(getattr(msg, "content", ""))[:80]

        # Add tool_calls info for AIMessage
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            tools_str = ", ".join(tc["name"] for tc in msg.tool_calls)
            content = f"[tool_calls: {tools_str}] {content}"

        # Add tool_call_id for ToolMessage
        if isinstance(msg, ToolMessage):
            content = f"[id: {msg.tool_call_id[:8]}...] {content}"

        table.add_row(str(i), msg_type, content)

    console.print(table)


def print_graph_info(model: str, tools: list):
    """Print agent startup info."""
    tool_names = [t.name for t in tools]
    console.print(Panel(
        f"[bold]LLM:[/bold] Ollama / [cyan]{model}[/cyan]\n"
        f"[bold]Tools:[/bold] {', '.join(f'[green]{t}[/green]' for t in tool_names)}\n"
        f"[bold]Framework:[/bold] LangGraph 1.2.x (StateGraph + ReAct)\n"
        f"[bold]Search:[/bold] SerpAPI (Google Flights, Hotels, Maps, Weather)",
        title="[bold yellow]✈️ Travel AI Assistant[/bold yellow]",
        border_style="yellow",
    ))