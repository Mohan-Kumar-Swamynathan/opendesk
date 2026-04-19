"""Natural language query using Ollama."""
import json

from rich.console import Console

console = Console()

TOOL_DESCRIPTIONS = {
    "get_open_tabs": "Get list of open browser tabs",
    "take_screenshot": "Take a screenshot of the screen",
    "get_system_info": "Get CPU, memory, battery info",
    "get_disk_usage": "Get disk space usage",
    "list_processes": "List running processes",
    "list_directory": "List files in a directory",
    "get_clipboard": "Get clipboard content",
    "get_volume": "Get current volume level",
    "set_volume": "Set volume level",
    "open_application": "Open an application",
    "close_application": "Close an application",
    "send_notification": "Send a notification",
}


def run_ask(query: str, model: str = None):
    """Run natural language query using Ollama."""
    try:
        import ollama
    except ImportError:
        console.print("[red]ollama package not installed[/red]")
        console.print("[cyan]pip install ollama[/cyan]")
        return

    tool_schemas = []
    for name, desc in TOOL_DESCRIPTIONS.items():
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": {"type": "object", "properties": {}}
            }
        })

    system_prompt = f"""You are an opendesk assistant. Convert the user's request into a tool call.
Available tools:
{json.dumps(tool_schemas, indent=2)}

If a tool applies, respond with ONLY this format (no other text):
TOOL: <tool_name>
ARGS: <json arguments>

If no tool applies, respond with:
TOOL: none
REASON: <why not applicable>"""

    try:
        response = ollama.chat(
            model=model or "llama3.2:latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )

        content = response.message.content.strip()
        
        if content.startswith("TOOL:"):
            lines = content.split("\n")
            tool_line = lines[0].replace("TOOL:", "").strip()
            args_line = "".join(lines[1:]).replace("ARGS:", "").strip()
            
            if tool_line == "none":
                reason = "".join(lines[1:]).replace("REASON:", "").strip()
                console.print(f"[yellow]{reason}[/yellow]")
                return
            
            tool_name = tool_line
            try:
                args = json.loads(args_line) if args_line else {}
            except json.JSONDecodeError:
                args = {}
            
            result = call_tool(tool_name, args)
            console.print_json(json.dumps(result))
        else:
            console.print(content)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def call_tool(tool_name: str, args: dict):
    """Call a tool and return result."""
    from opendesk.tools import (
        get_open_tabs, take_screenshot, get_system_info, get_disk_usage,
        list_processes, list_directory, get_clipboard, get_volume,
        open_application, close_application, send_notification,
    )
    
    if tool_name == "open_application":
        app_name = args.get("app_name") or args.get("application") or args.get("app") or args.get("name", "")
        app_args = args.get("args")
        return open_application(app_name=app_name, args=app_args)
    elif tool_name == "close_application":
        app_name = args.get("app_name") or args.get("application") or args.get("app") or args.get("name", "")
        force = args.get("force", False)
        return close_application(app_name=app_name, force=force)
    elif tool_name == "get_open_tabs":
        browser = args.get("browser")
        return get_open_tabs(browser=browser)
    elif tool_name == "take_screenshot":
        save_path = args.get("save_path")
        monitor = args.get("monitor", 0)
        return take_screenshot(save_path=save_path, monitor=monitor)
    elif tool_name == "get_system_info":
        return get_system_info()
    elif tool_name == "get_disk_usage":
        return get_disk_usage()
    elif tool_name == "list_processes":
        sort_by = args.get("sort_by", "memory")
        limit = args.get("limit", 20)
        filter_name = args.get("filter_name")
        return list_processes(sort_by=sort_by, limit=limit, filter_name=filter_name)
    elif tool_name == "list_directory":
        path = args.get("path", ".")
        return list_directory(path=path)
    elif tool_name == "get_clipboard":
        return get_clipboard()
    elif tool_name == "get_volume":
        return get_volume()
    elif tool_name == "set_volume":
        level = args.get("level", 0.5)
        return set_volume(level=level)
    elif tool_name == "send_notification":
        title = args.get("title", "")
        message = args.get("message", "")
        return send_notification(title=title, message=message)
    else:
        return {"error": f"Unknown tool: {tool_name}"}
