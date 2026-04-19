"""Natural language query using local Ollama.

Usage:
    opendesk ask "why is my Mac slow?"
    opendesk ask "what time is it?" --model qwen2.5:14b
"""
import inspect
import json
import logging
import shutil
import sys
import time
from typing import Optional

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(stderr=True)  # Never pollute stdout


# ---------------------------------------------------------------------------
# Tool registry — single source of truth
# ---------------------------------------------------------------------------

def _build_registry() -> dict:
    """
    Import every tool from opendesk.tools and return {name: callable}.

    Lazy-imported so the module can be loaded without side-effects.
    Platform-specific tools that fail to import are silently skipped.
    """
    import datetime
    registry = {}

    # Collect all tool functions from opendesk.tools
    # Wrapping in try/except per-tool so a single broken platform import
    # doesn't take out the whole registry
    _TOOL_IMPORTS = {
        # screen
        "take_screenshot":       ("opendesk.tools", "take_screenshot"),
        "get_active_window":     ("opendesk.tools", "get_active_window"),
        "list_open_windows":     ("opendesk.tools", "list_open_windows"),
        "get_screen_text":       ("opendesk.tools", "get_screen_text"),
        # input
        "click":                 ("opendesk.tools", "click"),
        "type_text":             ("opendesk.tools", "type_text"),
        "press_key":             ("opendesk.tools", "press_key"),
        "scroll":                ("opendesk.tools", "scroll"),
        "drag":                  ("opendesk.tools", "drag"),
        # filesystem
        "read_file":             ("opendesk.tools", "read_file"),
        "write_file":            ("opendesk.tools", "write_file"),
        "list_directory":        ("opendesk.tools", "list_directory"),
        "search_files":          ("opendesk.tools", "search_files"),
        "get_recent_files":      ("opendesk.tools", "get_recent_files"),
        "move_file":             ("opendesk.tools", "move_file"),
        "delete_file":           ("opendesk.tools", "delete_file"),
        "get_disk_usage":        ("opendesk.tools", "get_disk_usage"),
        # system
        "list_processes":        ("opendesk.tools", "list_processes"),
        "kill_process":          ("opendesk.tools", "kill_process"),
        "get_system_info":       ("opendesk.tools", "get_system_info"),
        "get_network_info":      ("opendesk.tools", "get_network_info"),
        # applications
        "open_application":      ("opendesk.tools", "open_application"),
        "close_application":     ("opendesk.tools", "close_application"),
        "focus_application":     ("opendesk.tools", "focus_application"),
        "list_installed_apps":   ("opendesk.tools", "list_installed_apps"),
        # clipboard
        "get_clipboard":         ("opendesk.tools", "get_clipboard"),
        "set_clipboard":         ("opendesk.tools", "set_clipboard"),
        # terminal
        "run_command":           ("opendesk.tools", "run_command"),
        "get_command_history":   ("opendesk.tools", "get_command_history"),
        "get_environment_variable": ("opendesk.tools", "get_environment_variable"),
        # notifications
        "send_notification":     ("opendesk.tools", "send_notification"),
        # audio
        "get_volume":            ("opendesk.tools", "get_volume"),
        "set_volume":            ("opendesk.tools", "set_volume"),
        "mute":                  ("opendesk.tools", "mute"),
        "unmute":                ("opendesk.tools", "unmute"),
        # browser
        "get_open_tabs":         ("opendesk.tools", "get_open_tabs"),
        "open_url":              ("opendesk.tools", "open_url"),
    }

    for name, (module_path, func_name) in _TOOL_IMPORTS.items():
        try:
            mod = __import__(module_path, fromlist=[func_name])
            fn = getattr(mod, func_name, None)
            if fn and callable(fn):
                registry[name] = fn
        except (ImportError, AttributeError, OSError) as exc:
            logger.debug("Skipped tool %s: %s", name, exc)

    # Built-in helper that doesn't live in opendesk.tools
    def get_current_time() -> dict:
        """Get current date, time, and weekday."""
        now = datetime.datetime.now()
        return {
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%Y-%m-%d"),
            "weekday": now.strftime("%A"),
            "full": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

    registry["get_current_time"] = get_current_time
    return registry


# ---------------------------------------------------------------------------
# Ollama tool-spec builder — reads real function signatures
# ---------------------------------------------------------------------------

_PY_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def _build_tool_specs(registry: dict) -> list:
    """Convert the registry into Ollama-compatible tool schemas."""
    specs = []
    for name, func in registry.items():
        sig = inspect.signature(func)
        props = {}
        required = []

        for pname, param in sig.parameters.items():
            json_type = _PY_TO_JSON_TYPE.get(param.annotation, "string")
            props[pname] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(pname)

        description = (func.__doc__ or name.replace("_", " ").title()).strip().split("\n")[0]

        specs.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            },
        })
    return specs


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

_PREFERRED_MODELS = [
    "qwen2.5:14b", "qwen2.5:7b", "qwen3",
    "llama3.2:latest", "llama3.1:8b",
    "mistral:latest",
]


def _pick_model(available_models: list[str]) -> Optional[str]:
    """Pick the best available model for tool calling."""
    for preferred in _PREFERRED_MODELS:
        for avail in available_models:
            if preferred in avail:
                return avail
    return available_models[0] if available_models else None


# ---------------------------------------------------------------------------
# Safe tool execution
# ---------------------------------------------------------------------------

def _clean_args(args: dict, valid_params: set) -> dict:
    """Clean arguments - handle llama3.2 quirks like {key: {'type': 'int'}}."""
    cleaned = {}
    for k, v in args.items():
        if k not in valid_params:
            continue
        # Handle llama3.2 returning {"key": {"type": "int"}} instead of {"key": <value>}
        if isinstance(v, dict):
            if "type" in v:
                continue  # Skip type annotations
            # If dict has other keys, just skip
            continue
        cleaned[k] = v
    return cleaned


def _execute_tool(name: str, args: dict, registry: dict) -> Optional[dict]:
    """
    Execute a tool with:
    - Registry lookup (not an if-else chain)
    - Audit logging
    - Timing
    - User-friendly error display
    """
    if name not in registry:
        console.print(f"  [red]Unknown tool: {name}[/red]")
        return None

    # Get expected parameters
    sig = inspect.signature(registry[name])
    valid_params = set(sig.parameters.keys())
    
    # Clean args (handle llama3.2 quirks)
    filtered_args = _clean_args(args, valid_params)
    
    console.print(f"  [yellow][{name}][/yellow] {json.dumps(filtered_args) if filtered_args else ''}")

    start = time.time()
    try:
        result = registry[name](**filtered_args)
        duration_ms = int((time.time() - start) * 1000)

        # Audit logging (best-effort)
        try:
            from opendesk.audit import log_tool_call
            log_tool_call(name, args, success=True, result_summary=str(result)[:200])
        except (ImportError, TypeError):
            pass

        return result

    except TypeError as exc:
        # Wrong arguments — show helpful message
        console.print(f"  [red]Bad arguments for {name}: {exc}[/red]")
        sig = inspect.signature(registry[name])
        console.print(f"  [dim]Expected: {sig}[/dim]")
        return {"error": str(exc)}

    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        console.print(f"  [red]Error: {exc}[/red]")

        try:
            from opendesk.audit import log_tool_call
            log_tool_call(name, args, success=False, error=str(exc))
        except (ImportError, TypeError):
            pass

        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_ask(query: str, model: str = None):
    """Run a natural language query using local Ollama."""

    # --- Step 1: Check ollama Python package ---
    try:
        import ollama
    except ImportError:
        console.print("[red]Ollama Python library not installed.[/red]")
        console.print("  Install: [cyan]pip install opendesk[ollama][/cyan]")
        return

    # --- Step 2: Check ollama binary exists ---
    if not shutil.which("ollama"):
        console.print("[red]Ollama not found on this machine.[/red]")
        console.print("  Install: [cyan]https://ollama.ai[/cyan]")
        return

    # --- Step 3: Check ollama daemon is running + list models ---
    try:
        model_list = ollama.list()
        available = [m.get("name", m.get("model", "")) for m in model_list.get("models", [])]
    except Exception:
        console.print("[red]Ollama is installed but not running.[/red]")
        console.print("  Start it: [cyan]ollama serve[/cyan]")
        return

    if not available:
        console.print("[yellow]No Ollama models installed.[/yellow]")
        console.print("  Pull one: [cyan]ollama pull qwen2.5:7b[/cyan]")
        return

    # --- Step 4: Pick model ---
    model = model or _pick_model(available)
    if not model:
        console.print("[yellow]Could not find a suitable model.[/yellow]")
        return

    # --- Step 5: Build tool specs from real registry ---
    registry = _build_registry()
    tool_specs = _build_tool_specs(registry)
    console.print(f"[dim]Model: {model} | Tools: {len(tool_specs)}[/dim]\n")

    # --- Step 6: Call Ollama with native tool calling ---
    system_prompt = """You are opendesk assistant, a desktop automation helper.

You can either:
1) Reply normally in natural language, or
2) Call available tools when user intent needs real system data or desktop actions.

Rules:
- Use tools for factual system/device state (cpu, memory, battery, files, apps, time, clipboard, volume, etc.).
- Use tools for actions (open/close/focus apps, screenshots, file ops, commands, notifications, audio, browser).
- If user asks for something ambiguous, ask a short clarification question.
- If a request is impossible or unsafe with available tools, explain briefly and suggest an alternative.
- Keep responses concise and practical."""

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            tools=tool_specs,
        )
    except Exception as exc:
        console.print(f"[red]Ollama error: {exc}[/red]")
        return

    # --- Step 7: Process response ---
    message = response.get("message", {})
    tool_calls = message.get("tool_calls", [])
    content = message.get("content", "")

    # If model didn't call a tool, just return its response
    if not tool_calls and content:
        console.print(content)
        return

    if tool_calls:
        for call in tool_calls:
            fn_name = call["function"]["name"]
            fn_args = call["function"].get("arguments", {})
            result = _execute_tool(fn_name, fn_args, registry)
            if result is not None:
                try:
                    console.print_json(json.dumps(result, default=str, indent=2))
                except Exception:
                    console.print(str(result))
            console.print()
    else:
        # Model chose to reply in natural language
        content = message.get("content", "")
        if content:
            console.print(content)
        else:
            console.print("[dim]No response from model.[/dim]")
