"""Quick check commands."""
from rich.console import Console

console = Console()

QUICK_CHECKS = {
    "cpu": ("get_system_info", "cpu_percent", "CPU: {value}%"),
    "battery": ("get_system_info", "battery_percent", "Battery: {value}%"),
    "memory": ("get_system_info", "memory_percent", "Memory: {value}%"),
    "disk": ("get_disk_usage", "percent_used", "Disk: {value}%"),
    "processes": ("list_processes", "processes", "processes"),
    "clipboard": ("get_clipboard", "text", "clipboard"),
    "volume": ("get_volume", "volume", "Volume: {value}%"),
    "network": ("get_network_info", "status", "network"),
}


def run_check(check_name: str):
    from opendesk.ai_cli import parse_ask
    parse_ask(check_name)