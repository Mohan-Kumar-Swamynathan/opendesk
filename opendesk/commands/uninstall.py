"""Uninstall opendesk from clients."""
import json
import shutil
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def run_uninstall():
    console.print("[bold]Removing opendesk from MCP clients...[/bold]\n")

    home = Path.home()
    removed = []

    if sys.platform == "darwin":
        claude_config = home / "Library" / "Application Support" / "Claude" / "settings.json"
        if _remove_from_config(claude_config):
            removed.append("Claude Desktop")

        cursor_config = home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
        if _remove_from_config(cursor_config):
            removed.append("Cursor")

    elif sys.platform == "win32":
        appdata = Path.home() / "AppData" / "Roaming"
        cursor_path = appdata / "Code" / "User" / "settings.json"
        if _remove_from_config(cursor_path):
            removed.append("Cursor")

    else:
        config_dir = home / ".config" / "Code" / "User"
        cursor_path = config_dir / "settings.json"
        if _remove_from_config(cursor_path):
            removed.append("Cursor")

    if removed:
        console.print(f"[green]✓ Removed from: {', '.join(removed)}[/green]")
    else:
        console.print("[yellow]No opendesk configurations found[/yellow]")


def _remove_from_config(config_path: Path) -> bool:
    if not config_path.exists():
        return False

    try:
        config = json.loads(config_path.read_text())
        if "mcpServers" in config and "opendesk" in config["mcpServers"]:
            del config["mcpServers"]["opendesk"]
            if not config["mcpServers"]:
                del config["mcpServers"]
            config_path.write_text(json.dumps(config, indent=2))
            return True
    except Exception:
        pass
    return False