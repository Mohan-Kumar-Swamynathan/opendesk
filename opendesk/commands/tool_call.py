"""Run a tool directly."""
from rich.console import Console

console = Console()

TOOLS = {
    "take_screenshot": ("Take a screenshot", {}),
    "get_active_window": ("Get the active window", {}),
    "list_open_windows": ("List open windows", {}),
    "get_screen_text": ("Extract text from screen (OCR)", {}),
    "click": ("Click at coordinates", {"x": int, "y": int}),
    "type_text": ("Type text", {"text": str}),
    "press_key": ("Press a key", {"key": str}),
    "scroll": ("Scroll", {"x": int, "y": int, "delta": int}),
    "drag": ("Drag from point to point", {"x1": int, "y1": int, "x2": int, "y2": int}),
    "read_file": ("Read a file", {"path": str}),
    "write_file": ("Write to a file", {"path": str, "content": str}),
    "list_directory": ("List directory contents", {"path": str}),
    "search_files": ("Search for files", {"pattern": str, "path": str}),
    "get_recent_files": ("Get recent files", {"limit": int}),
    "move_file": ("Move a file", {"source": str, "destination": str}),
    "delete_file": ("Delete a file", {"path": str}),
    "get_disk_usage": ("Get disk usage", {"path": str}),
    "list_processes": ("List processes", {"limit": int}),
    "kill_process": ("Kill a process", {"pid": int}),
    "get_system_info": ("Get system info", {}),
    "get_network_info": ("Get network info", {}),
    "open_application": ("Open an application", {"app_name": str}),
    "close_application": ("Close an application", {"app_name": str}),
    "focus_application": ("Focus an application", {"app_name": str}),
    "list_installed_apps": ("List installed apps", {}),
    "get_clipboard": ("Get clipboard", {}),
    "set_clipboard": ("Set clipboard", {"text": str}),
    "run_command": ("Run a command", {"command": str}),
    "get_command_history": ("Get command history", {}),
    "get_environment_variable": ("Get environment variable", {"name": str}),
    "send_notification": ("Send notification", {"title": str, "message": str}),
    "get_volume": ("Get volume level", {}),
    "set_volume": ("Set volume level", {"level": int}),
    "mute": ("Mute audio", {}),
    "unmute": ("Unmute audio", {}),
    "get_open_tabs": ("Get open browser tabs", {}),
    "open_url": ("Open a URL", {"url": str}),
}


def run_tool(args, dry_run=False):
    if not args:
        console.print("[red]No tool specified[/red]")
        return

    tool_name = args[0]
    if tool_name not in TOOLS:
        console.print(f"[red]Unknown tool: {tool_name}[/red]")
        console.print("[dim]Available tools:[/dim]")
        for name, (desc, _) in TOOLS.items():
            console.print(f"  [cyan]{name}[/cyan] - {desc}")
        return

    from opendesk.tools import (
        take_screenshot, get_active_window, list_open_windows, get_screen_text,
        click, type_text, press_key, scroll, drag,
        read_file, write_file, list_directory, search_files, get_recent_files,
        move_file, delete_file, get_disk_usage,
        list_processes, kill_process, get_system_info, get_network_info,
        open_application, close_application, focus_application, list_installed_apps,
        get_clipboard, set_clipboard,
        run_command, get_command_history, get_environment_variable,
        send_notification,
        get_volume, set_volume, mute, unmute,
        get_open_tabs, open_url,
    )

    tools = {
        "take_screenshot": take_screenshot,
        "get_active_window": get_active_window,
        "list_open_windows": list_open_windows,
        "get_screen_text": get_screen_text,
        "click": click,
        "type_text": type_text,
        "press_key": press_key,
        "scroll": scroll,
        "drag": drag,
        "read_file": read_file,
        "write_file": write_file,
        "list_directory": list_directory,
        "search_files": search_files,
        "get_recent_files": get_recent_files,
        "move_file": move_file,
        "delete_file": delete_file,
        "get_disk_usage": get_disk_usage,
        "list_processes": list_processes,
        "kill_process": kill_process,
        "get_system_info": get_system_info,
        "get_network_info": get_network_info,
        "open_application": open_application,
        "close_application": close_application,
        "focus_application": focus_application,
        "list_installed_apps": list_installed_apps,
        "get_clipboard": get_clipboard,
        "set_clipboard": set_clipboard,
        "run_command": run_command,
        "get_command_history": get_command_history,
        "get_environment_variable": get_environment_variable,
        "send_notification": send_notification,
        "get_volume": get_volume,
        "set_volume": set_volume,
        "mute": mute,
        "unmute": unmute,
        "get_open_tabs": get_open_tabs,
        "open_url": open_url,
    }

    kwargs = {}
    for param in args[1:]:
        if "=" in param:
            key, value = param.split("=", 1)
            try:
                kwargs[key] = int(value)
            except ValueError:
                try:
                    kwargs[key] = float(value)
                except ValueError:
                    kwargs[key] = value

    if dry_run:
        console.print(f"[cyan]{tool_name}[/cyan]({kwargs})")
        return

    try:
        result = tools[tool_name](**kwargs)
        console.print_json(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")