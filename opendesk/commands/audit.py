"""Show audit log."""
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def run_audit(limit=50, today_only=False, errors_only=False, tool_filter=None, tail=False):
    audit_file = Path.home() / ".opendesk" / "audit.log"

    if not audit_file.exists():
        console.print("[yellow]No audit log found (no tools have been called yet)[/yellow]")
        return

    try:
        lines = audit_file.read_text().strip().split("\n")[-limit:]
    except Exception as e:
        console.print(f"[red]Error reading audit log: {e}[/red]")
        return

    table = Table(title="Recent Tool Calls")
    table.add_column("Time", style="dim")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    for line in lines[-limit:]:
        if not line.strip():
            continue
        try:
            import json
            entry = json.loads(line)
            tool = entry.get("tool", "?")
            status = "ok" if entry.get("success") else "error"

            if tool_filter and tool != tool_filter:
                continue
            if errors_only and status == "ok":
                continue

            table.add_row(
                entry.get("timestamp", "")[:19],
                tool,
                status,
                str(entry.get("args", {}))[:40]
            )
        except Exception:
            pass

    console.print(table)