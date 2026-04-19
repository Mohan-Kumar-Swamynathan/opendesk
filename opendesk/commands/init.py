"""Initialize opendesk for MCP clients."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def find_opendesk_absolute() -> str:
    """Find opendesk executable with ABSOLUTE path."""
    path = shutil.which("opendesk")
    if path:
        return str(Path(path).resolve())

    python_dir = Path(sys.executable).parent
    candidate = python_dir / "opendesk"
    if candidate.exists():
        return str(candidate.resolve())

    return "opendesk"


def configure_json_client(name: str, config_path: Path, config_dir: Path) -> bool:
    """Add opendesk to a JSON-based MCP client config."""
    try:
        config_dir.mkdir(parents=True, exist_ok=True)

        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
            except json.JSONDecodeError:
                config = {}
        else:
            config = {}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"]["opendesk"] = {
            "command": find_opendesk_absolute(),
            "args": ["--serve"],
        }

        config_path.write_text(json.dumps(config, indent=2))
        return "opendesk" in config.get("mcpServers", {})
    except Exception as e:
        console.print(f"[red]Failed to configure {name}: {e}[/red]")
        return False


def run_init():
    console.print("[bold]Initializing opendesk for MCP clients...[/bold]\n")

    home = Path.home()

    claude_desktop_dir = home / "Library" / "Application Support" / "Claude"
    claude_config = claude_desktop_dir / "settings.json"

    cursor_dir = home / ".cursor-server" / "data" / "mcp"
    cursor_config = cursor_dir / "config.json"

    found_any = False

    if sys.platform == "darwin":
        if configure_json_client("Claude Desktop", claude_config, claude_desktop_dir):
            console.print(f"[green]✓ Configured Claude Desktop[/green]")
            found_any = True
        else:
            console.print(f"[yellow]○ Claude Desktop not found[/yellow]")

        cursor_path = home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
        if configure_json_client("Cursor", cursor_path, cursor_path.parent):
            console.print(f"[green]✓ Configured Cursor[/green]")
            found_any = True

    elif sys.platform == "win32":
        appdata = Path.home() / "AppData" / "Roaming"
        cursor_path = appdata / "Code" / "User" / "settings.json"
        if configure_json_client("Cursor", cursor_path, cursor_path.parent):
            console.print(f"[green]✓ Configured Cursor[/green]")
            found_any = True

    else:
        config_dir = home / ".config" / "Code" / "User"
        cursor_path = config_dir / "settings.json"
        if configure_json_client("Cursor", cursor_path, config_dir):
            console.print(f"[green]✓ Configured Cursor[/green]")
            found_any = True

    if found_any:
        console.print("\n[green]opendesk is ready![/green]")
    else:
        console.print("\n[yellow]No MCP clients found. Run 'opendesk --serve' manually.[/yellow]")