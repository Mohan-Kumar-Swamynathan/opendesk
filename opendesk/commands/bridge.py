"""Interactive Ollama bridge."""
from rich.console import Console

console = Console()


def run_bridge(model: str = "qwen2.5:7b"):
    from opendesk.ai_cli import parse_ask

    console.print(f"[green]Interactive mode with {model}[/green]")
    console.print("[dim]Type your requests naturally. Type 'quit' to exit.[/dim]\n")

    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break
            if not user_input:
                continue
            parse_ask(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except EOFError:
            break