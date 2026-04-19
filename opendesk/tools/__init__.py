from opendesk.tools.screen import (
    take_screenshot,
    get_active_window,
    list_open_windows,
    get_screen_text,
)
from opendesk.tools.input import (
    click,
    type_text,
    press_key,
    scroll,
    drag,
)
from opendesk.tools.filesystem import (
    read_file,
    write_file,
    list_directory,
    search_files,
    get_recent_files,
    move_file,
    delete_file,
    get_disk_usage,
)
from opendesk.tools.system import (
    list_processes,
    kill_process,
    get_system_info,
    get_network_info,
)
from opendesk.tools.applications import (
    open_application,
    close_application,
    focus_application,
    list_installed_apps,
)
from opendesk.tools.clipboard import (
    get_clipboard,
    set_clipboard,
)
from opendesk.tools.terminal import (
    run_command,
    get_command_history,
    get_environment_variable,
)
from opendesk.tools.notifications import send_notification
from opendesk.tools.audio import (
    get_volume,
    set_volume,
    mute,
    unmute,
)
from opendesk.tools.browser import (
    get_open_tabs,
    open_url,
)

__all__ = [
    "take_screenshot",
    "get_active_window",
    "list_open_windows",
    "get_screen_text",
    "click",
    "type_text",
    "press_key",
    "scroll",
    "drag",
    "read_file",
    "write_file",
    "list_directory",
    "search_files",
    "get_recent_files",
    "move_file",
    "delete_file",
    "get_disk_usage",
    "list_processes",
    "kill_process",
    "get_system_info",
    "get_network_info",
    "open_application",
    "close_application",
    "focus_application",
    "list_installed_apps",
    "get_clipboard",
    "set_clipboard",
    "run_command",
    "get_command_history",
    "get_environment_variable",
    "send_notification",
    "get_volume",
    "set_volume",
    "mute",
    "unmute",
    "get_open_tabs",
    "open_url",
]