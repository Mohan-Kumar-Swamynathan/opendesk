"""Natural language query using Ollama."""
from rich.console import Console

console = Console()


def run_ask(query: str, model: str = None):
    try:
        import ollama
    except ImportError:
        console.print("[red]ollama package not installed[/red]")
        console.print("[cyan]pip install ollama[/cyan]")
        return

    from opendesk.ai_cli import parse_ask
    parse_ask(query)