"""List available tools."""
from rich.console import Console
from rich.table import Table


def run_list():
    console = Console()
    table = Table(title="Available Tools")
    table.add_column("Category", style="cyan")
    table.add_column("Tools", style="white")

    tools_by_cat = {
        "Screen & Vision": "take_screenshot, get_active_window, list_open_windows, get_screen_text",
        "Input": "click, type_text, press_key, scroll, drag",
        "File System": "read_file, write_file, list_directory, search_files, get_recent_files, move_file, delete_file, get_disk_usage",
        "System": "list_processes, kill_process, get_system_info, get_network_info",
        "Applications": "open_application, close_application, focus_application, list_installed_apps",
        "Clipboard": "get_clipboard, set_clipboard",
        "Terminal": "run_command, get_command_history, get_environment_variable",
        "Notifications": "send_notification",
        "Audio": "get_volume, set_volume, mute, unmute",
        "Browser": "get_open_tabs, open_url",
    }

    for cat, tools in tools_by_cat.items():
        table.add_row(cat, tools)

    console.print(table)