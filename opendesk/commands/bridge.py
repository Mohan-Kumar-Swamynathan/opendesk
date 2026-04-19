"""Interactive Ollama bridge."""
import json
from rich.console import Console

console = Console()

TOOL_SCHEMAS = {
    "get_open_tabs": {"description": "Get list of open browser tabs", "parameters": {"browser": {"type": "string"}}},
    "take_screenshot": {"description": "Take a screenshot", "parameters": {"save_path": {"type": "string"}}},
    "get_system_info": {"description": "Get CPU, memory, battery info", "parameters": {}},
    "get_disk_usage": {"description": "Get disk usage", "parameters": {}},
    "list_processes": {"description": "List processes", "parameters": {"limit": {"type": "integer"}}},
    "list_directory": {"description": "List files", "parameters": {"path": {"type": "string"}}},
    "get_clipboard": {"description": "Get clipboard", "parameters": {}},
    "get_volume": {"description": "Get volume", "parameters": {}},
    "set_volume": {"description": "Set volume", "parameters": {"level": {"type": "number"}}},
    "open_application": {"description": "Open app", "parameters": {"app_name": {"type": "string"}}},
    "close_application": {"description": "Close app", "parameters": {"app_name": {"type": "string"}}},
    "send_notification": {"description": "Send notification", "parameters": {"title": {"type": "string"}, "message": {"type": "string"}}},
}


def run_bridge(model: str = None):
    if not model:
        model = "llama3.2:latest"
    import ollama
    from opendesk.tools import (
        get_open_tabs, take_screenshot, get_system_info, get_disk_usage,
        list_processes, list_directory, get_clipboard, get_volume,
        open_application, close_application, send_notification,
    )

    console.print(f"[green]Ollama bridge with {model}[/green]")
    console.print("[dim]Type naturally. 'quit' to exit.[/dim]\n")

    tool_schemas = []
    for name, schema in TOOL_SCHEMAS.items():
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": schema["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_name: {"type": param_info["type"]}
                        for param_name, param_info in schema.get("parameters", {}).items()
                    }
                }
            }
        })

    system_prompt = f"""You are an opendesk assistant. Convert requests to tool calls.
Available tools: {json.dumps(tool_schemas)}

Use EXACT parameter names: app_name (not application), path, level, save_path, title, message.

Respond ONLY with:
TOOL: <tool_name>
ARGS: <json>

Or if no tool needed:
TOOL: none
REASON: <why>"""

    tools = {
        "get_open_tabs": get_open_tabs,
        "take_screenshot": take_screenshot,
        "get_system_info": get_system_info,
        "get_disk_usage": get_disk_usage,
        "list_processes": list_processes,
        "list_directory": list_directory,
        "get_clipboard": get_clipboard,
        "get_volume": get_volume,
        "open_application": open_application,
        "close_application": close_application,
        "send_notification": send_notification,
    }

    call_tool = lambda name, args: tools.get(name, lambda: {"error": f"Unknown: {name}"})(**args) if name in tools else {"error": f"Unknown tool: {name}"}

    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            if not user_input:
                continue

            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )

            content = response.message.content.strip()

            if content.startswith("TOOL:"):
                lines = content.split("\n")
                tool_name = lines[0].replace("TOOL:", "").strip()
                args_line = "".join(lines[1:]).replace("ARGS:", "").strip()

                if tool_name == "none":
                    reason = args_line.replace("REASON:", "").strip()
                    console.print(f"[yellow]{reason}[/yellow]")
                    continue

                try:
                    args = json.loads(args_line) if args_line else {}
                except json.JSONDecodeError:
                    args = {}

                # Map args
                if tool_name == "open_application":
                    args["app_name"] = args.get("app_name") or args.get("application") or args.get("app") or args.get("name", "")

                result = call_tool(tool_name, args)
                console.print_json(json.dumps(result))
            else:
                console.print(content)

        except KeyboardInterrupt:
            console.print("\n[yellow]Bye![/yellow]")
            break
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")