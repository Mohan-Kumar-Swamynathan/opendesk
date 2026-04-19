import platform
import sys
from typing import Literal

OSType = Literal["mac", "windows", "linux"]


def get_os() -> OSType:
    system = platform.system()
    if system == "Darwin":
        return "mac"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


OS: OSType = get_os()
IS_MAC = OS == "mac"
IS_WINDOWS = OS == "windows"
IS_LINUX = OS == "linux"


def import_platform_modules():
    modules = {}
    if IS_MAC:
        from opendesk.tools.mac import applescript, accessibility

        modules["applescript"] = applescript
        modules["accessibility"] = accessibility
    elif IS_WINDOWS:
        from opendesk.tools.windows import win32_utils, uia

        modules["win32_utils"] = win32_utils
        modules["uia"] = uia
    elif IS_LINUX:
        from opendesk.tools.linux import x11_utils

        modules["x11_utils"] = x11_utils
    return modules
