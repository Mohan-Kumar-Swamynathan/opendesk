import sys
import json
import re
from typing import Optional
from rich.console import Console

console = Console()


def parse_ask(prompt: str):
    import re
    prompt_lower = prompt.lower()

    tool_map = {
        ("cpu", "processor", "computer"): ("get_system_info", {}),
        ("memory", "ram"): ("get_system_info", {}),
        ("battery", "charge"): ("get_system_info", {}),
        ("disk", "storage", "space"): ("get_disk_usage", {"path": "/"}),
        ("processes", "running processes"): ("list_processes", {"limit": 5}),
        ("files", "directory", "folder", "list files", "show files"): ("list_directory", {"path": "~", "max_items": 5}),
        ("notify", "notification", "send notification"): ("send_notification", {"title": "AI", "message": prompt}),
        ("clipboard", "copy paste"): ("get_clipboard", {}),
        ("network", "wifi", "internet"): ("get_network_info", {}),
        ("screenshot", "capture screen", "take picture"): ("take_screenshot", {}),
        ("volume", "audio", "sound"): ("get_volume", {}),
        ("mute", "silence"): ("mute", {}),
        ("unmute", "unmute"): ("unmute", {}),
    }

    app_open_patterns = [
        r"open\s+(.+)",
        r"launch\s+(.+)",
        r"start\s+(.+)",
        r"run\s+(.+)",
    ]
    
    app_close_patterns = [
        r"close\s+(.+)",
        r"quit\s+(.+)",
        r"kill\s+(.+)",
    ]

    app_focus_patterns = [
        r"focus\s+(.+)",
        r"switch\s+to\s+(.+)",
        r"activate\s+(.+)",
    ]

    from opendesk.tools import (
        get_system_info, get_disk_usage, list_processes, list_directory,
        get_clipboard, send_notification, get_network_info, take_screenshot, 
        get_volume, mute, unmute, open_application, close_application, focus_application,
    )

    tools = {
        "get_system_info": get_system_info,
        "get_disk_usage": get_disk_usage,
        "list_processes": list_processes,
        "list_directory": list_directory,
        "get_clipboard": get_clipboard,
        "send_notification": send_notification,
        "get_network_info": get_network_info,
        "take_screenshot": take_screenshot,
        "get_volume": get_volume,
        "mute": mute,
        "unmute": unmute,
        "open_application": open_application,
        "close_application": close_application,
        "focus_application": focus_application,
    }

    # Check for open app commands
    for pattern in app_open_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            app_name = match.group(1).strip()
            app_name = app_name.title() if len(app_name.split()) == 1 else app_name
            try:
                result = tools["open_application"](app_name=app_name)
                console.print(f"[green]Opening {app_name}...[/green]")
                console.print(f"[dim]PID: {result.get('pid', 'N/A')}[/dim]")
                return
            except Exception as e:
                console.print(f"[red]Error opening {app_name}: {e}[/red]")
                return

    # Check for close app commands
    for pattern in app_close_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            app_name = match.group(1).strip()
            app_name = app_name.title() if len(app_name.split()) == 1 else app_name
            try:
                result = tools["close_application"](app_name=app_name)
                console.print(f"[green]Closing {app_name}...[/green]")
                return
            except Exception as e:
                console.print(f"[red]Error closing {app_name}: {e}[/red]")
                return

    # Check for focus app commands
    for pattern in app_focus_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            app_name = match.group(1).strip()
            app_name = app_name.title() if len(app_name.split()) == 1 else app_name
            try:
                result = tools["focus_application"](app_name=app_name)
                console.print(f"[green]Switching to {app_name}...[/green]")
                return
            except Exception as e:
                console.print(f"[red]Error switching to {app_name}: {e}[/red]")
                return

    # Check for volume setting
    if "set volume" in prompt_lower or "volume" in prompt_lower:
        import re
        vol_match = re.search(r'(\d+)', prompt)
        if vol_match:
            level = int(vol_match.group(1))
            try:
                result = tools["set_volume"](level=level)
                console.print(f"[green]Volume set to {level}%[/green]")
                return
            except Exception as e:
                pass

    # Check for notifications
    if "notify" in prompt_lower or "alert" in prompt_lower:
        try:
            msg = prompt
            tools["send_notification"](title="AI Assistant", message=msg[:100])
            console.print("[green]Notification sent![/green]")
            return
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return

    # Check simple keywords
    for keywords, (tool_name, args) in tool_map.items():
        if any(kw in prompt_lower for kw in keywords):
            try:
                result = tools[tool_name](**args)
                if tool_name == "get_system_info":
                    if "battery" in prompt_lower:
                        console.print(f"[green]Battery: {result.get('battery_percent')}%[/green]")
                        console.print(f"[yellow]Charging: {result.get('battery_charging')}[/yellow]")
                    elif "memory" in prompt_lower or "ram" in prompt_lower:
                        console.print(f"[green]Memory: {result.get('memory_percent')}%[/green]")
                        console.print(f"[dim]{result.get('memory_used_gb')}GB / {result.get('memory_total_gb')}GB[/dim]")
                    elif "cpu" in prompt_lower or "processor" in prompt_lower:
                        console.print(f"[green]CPU: {result.get('cpu_percent')}%[/green]")
                        console.print(f"[dim]{result.get('cpu_cores')} cores[/dim]")
                    else:
                        console.print_json(json.dumps(result))
                elif tool_name == "get_disk_usage":
                    console.print(f"[green]Disk: {result.get('percent_used')}% used[/green]")
                    console.print(f"[dim]{result.get('free_gb')}GB free of {result.get('total_gb')}GB[/dim]")
                elif tool_name == "list_processes":
                    console.print("[green]Top processes:[/green]")
                    for p in result.get("processes", [])[:5]:
                        console.print(f"  {p.get('name')}: {p.get('memory_mb')}MB")
                elif tool_name == "list_directory":
                    console.print(f"[green]Files in ~:[/green]")
                    for item in result.get("items", [])[:5]:
                        console.print(f"  {item.get('name')} ({item.get('type')})")
                elif tool_name == "take_screenshot":
                    console.print(f"[green]Screenshot captured![/green]")
                    if result.get("saved_to"):
                        console.print(f"[cyan]Saved to: {result.get('saved_to')}[/cyan]")
                elif tool_name == "get_volume":
                    console.print(f"[green]Volume: {result.get('volume')}%[/green]")
                    if result.get("is_muted"):
                        console.print("[yellow]Muted[/yellow]")
                elif tool_name in ("mute", "unmute"):
                    console.print(f"[green]Done![/green]")
                else:
                    console.print_json(json.dumps(result))
                return
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return

    console.print("[yellow]I couldn't understand that command.[/yellow]")
    console.print("[dim]Try:[/dim]")
    console.print("[dim]  • open chrome[/dim]")
    console.print("[dim]  • close safari[/dim]")
    console.print("[dim]  • screenshot[/dim]")
    console.print("[dim]  • battery, cpu, memory[/dim]")
    console.print("[dim]  • set volume 50[/dim]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: opendesk <question>")
        print("Examples:")
        print("  opendesk cpu")
        print("  opendesk memory")
        print("  opendesk battery")
        print("  opendesk processes")
        print("  opendesk open chrome")
        print("  opendesk screenshot")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    parse_ask(prompt)
