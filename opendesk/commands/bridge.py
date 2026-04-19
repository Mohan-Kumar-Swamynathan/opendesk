"""Interactive Ollama bridge — conversational desktop AI.

Usage:
    opendesk bridge
    opendesk bridge --model qwen2.5:14b
"""
import json
import logging
import shutil
import sys
import time
from typing import Optional

from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console(stderr=True)  # Never pollute stdout


def run_bridge(model: str = None):
    """Start an interactive conversation loop with local Ollama."""

    # --- Pre-flight checks ---
    try:
        import ollama
    except ImportError:
        console.print("[red]Ollama Python library not installed.[/red]")
        console.print("  Install: [cyan]pip install ollama[/cyan]")
        return

    if not shutil.which("ollama"):
        console.print("[red]Ollama not found on this machine.[/red]")
        console.print("  Install: [cyan]https://ollama.ai[/cyan]")
        return

    try:
        model_list = ollama.list()
        available = [m.get("name", m.get("model", "")) for m in model_list.get("models", [])]
    except Exception:
        console.print("[red]Ollama is installed but not running.[/red]")
        console.print("  Start it: [cyan]ollama serve[/cyan]")
        return

    if not available:
        console.print("[yellow]No Ollama models installed.[/yellow]")
        console.print("  Pull one: [cyan]ollama pull llama3.2:latest[/cyan]")
        return

    # --- Pick model ---
    from opendesk.commands.ask import _pick_model
    model = model or _pick_model(available)
    if not model:
        console.print("[yellow]No suitable model found.[/yellow]")
        return

    # --- Build tool registry + specs ---
    from opendesk.commands.ask import _build_registry, _build_tool_specs, _execute_tool
    registry = _build_registry()
    tool_specs = _build_tool_specs(registry)

    # --- Welcome banner ---
    console.print()
    console.print(Panel.fit(
        f"[bold green]opendesk bridge[/bold green]\n"
        f"  Model:   [cyan]{model}[/cyan]\n"
        f"  Tools:   [yellow]{len(tool_specs)}[/yellow] available\n"
        f"  Network: {'[red]OFFLINE[/red]' if not _check_internet() else '[green]online[/green]'}\n\n"
        f"  [dim]Type naturally. 'quit' to exit.[/dim]",
        title="[bold]opendesk[/bold]",
        border_style="cyan",
    ))
    console.print()

    # --- System prompt ---
    system_msg = """You are a friendly assistant. 

Response rules:
- For greetings, just say hi friendly
- For random questions (like "what is charge"), ask for clarification or say you don't understand
- Only use tools for clear commands like "open Safari", "check CPU", "take screenshot"

If unclear what user wants, ask for clarification or just chat!"""

    conversation: list[dict] = [{"role": "system", "content": system_msg}]

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]Bye![/cyan]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[cyan]Bye![/cyan]")
            break

        # Add user message to history
        conversation.append({"role": "user", "content": user_input})

        # Only use tools for action keywords
        action_keywords = ["open", "close", "launch", "check", "take", "screenshot", 
                         "list", "show", "get", "kill", "cpu", "memory", "battery",
                         "processes", "files", "disk", "time", "date", "volume"]
        use_tools = any(kw in user_input.lower() for kw in action_keywords)

        # --- Call Ollama ---
        try:
            response = ollama.chat(
                model=model,
                messages=conversation,
                tools=tool_specs if use_tools else None,
            )
        except Exception as exc:
            console.print(f"[red]Ollama error: {exc}[/red]")
            # Remove failed message from history so conversation stays clean
            conversation.pop()
            continue

        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])
        content = message.get("content", "")

        if tool_calls:
            # --- Execute tool calls ---
            tool_results = []
            content = message.get("content", "")
            
            for call in tool_calls:
                fn_name = call["function"]["name"]
                fn_args = call["function"].get("arguments", {})

                result = _execute_tool(fn_name, fn_args, registry)

                if result is not None:
                    # Show result to user
                    try:
                        console.print_json(json.dumps(result, default=str, indent=2))
                    except Exception:
                        console.print(str(result))

                    tool_results.append({
                        "tool": fn_name,
                        "result": json.dumps(result, default=str)[:2000],
                    })

            # --- Send tool results back to model for summarization ---
            # Add assistant message with tool calls to history
            conversation.append({
                "role": "assistant",
                "content": content or "",
                "tool_calls": tool_calls,
            })

            # Add tool results to history
            for tr in tool_results:
                conversation.append({
                    "role": "tool",
                    "content": tr["result"],
                })

            # Ask model to summarize
            try:
                summary_response = ollama.chat(
                    model=model,
                    messages=conversation,
                )
                summary = summary_response.get("message", {}).get("content", "")
                if summary:
                    console.print(f"\n{summary}\n")
                    conversation.append({"role": "assistant", "content": summary})
            except Exception:
                # If summarization fails, just continue
                pass

        elif content:
            # --- Natural language response (no tools needed) ---
            console.print(f"\n{content}\n")
            conversation.append({"role": "assistant", "content": content})

        else:
            console.print("[dim]No response.[/dim]")

        # --- Trim conversation to prevent context overflow ---
        # Keep system prompt + last 20 exchanges
        if len(conversation) > 40:
            conversation = conversation[-40:]


def _check_internet() -> bool:
    """Quick check if internet is available."""
    import socket
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=1)
        return True
    except OSError:
        return False
