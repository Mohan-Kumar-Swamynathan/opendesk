"""List available tools."""
from rich.console import Console
from rich.table import Table


def run_list():
    console = Console()
    table = Table(title="Available Tools (31 tools)", show_header=True)
    table.add_column("Tool", style="cyan", width=30)
    table.add_column("Description", style="white")

    tools = [
        ("take_screenshot", "Capture screen as image"),
        ("get_active_window", "Get focused app/window"),
        ("list_open_windows", "List all visible windows"),
        ("get_screen_text", "OCR text from screen"),
        ("click", "Click at coordinates"),
        ("type_text", "Type text via keyboard"),
        ("press_key", "Press keyboard shortcut"),
        ("scroll", "Scroll mouse wheel"),
        ("drag", "Click and drag"),
        ("read_file", "Read file content"),
        ("write_file", "Create/update file"),
        ("list_directory", "Browse folder contents"),
        ("search_files", "Find files by name/content"),
        ("get_recent_files", "Recently modified files"),
        ("move_file", "Move or rename file"),
        ("delete_file", "Move file to trash"),
        ("get_disk_usage", "Free space on disks"),
        ("list_processes", "Running processes"),
        ("kill_process", "Terminate process"),
        ("get_system_info", "CPU, RAM, battery, uptime"),
        ("get_network_info", "Network interfaces"),
        ("open_application", "Launch an app"),
        ("close_application", "Quit an app"),
        ("focus_application", "Switch to app"),
        ("list_installed_apps", "All installed apps"),
        ("get_clipboard", "Read clipboard"),
        ("set_clipboard", "Write to clipboard"),
        ("run_command", "Execute shell command"),
        ("get_command_history", "Recent terminal commands"),
        ("get_environment_variable", "Read env variable"),
        ("send_notification", "Show system notification"),
    ]

    for name, desc in tools:
        table.add_row(name, desc)

    console.print(table)
    
    console.print("\n[dim]For more tools see: opendesk --help[/dim]")
