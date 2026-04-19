"""MCP server assembly using FastMCP."""
from opendesk._stdio_hygiene import enforce_stdout_discipline
enforce_stdout_discipline()

import logging

logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("opendesk")


def register_all_tools():
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

    tool_handlers = {
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

    for name, handler in tool_handlers.items():
        doc = handler.__doc__ or f"Tool: {name}"

        def make_wrapper(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        mcp.tool(name=name, description=doc)(tool_handlers[name])

    logger.info(f"opendesk ready with {len(tool_handlers)} tools")


def get_server() -> FastMCP:
    register_all_tools()
    return mcp


if __name__ == "__main__":
    get_server().run(transport="stdio")