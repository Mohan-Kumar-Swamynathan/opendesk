from typing import Optional
from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    """Click at screen coordinates."""
    try:
        if IS_MAC:
            from opendesk.tools.mac.accessibility import Accessibility
            return Accessibility.click(x, y, button=button, clicks=clicks)
        elif IS_WINDOWS:
            from opendesk.tools.windows.uia import UIAutomation
            return UIAutomation.click(x, y, button=button, clicks=clicks)
        elif IS_LINUX:
            from opendesk.tools.linux.x11_utils import X11Automation
            return X11Automation.click(x, y, button=button, clicks=clicks)
    except Exception as e:
        err_msg = str(e)
        if "not allowed" in err_msg.lower() and "access" in err_msg.lower():
            return {"success": False, "error": err_msg, "suggestion": "Grant Accessibility permission: System Settings → Privacy & Security → Accessibility"}
        return {"success": False, "error": err_msg}
    return {"success": False}


def type_text(text: str, interval: float = 0.05) -> dict:
    """Type text at current cursor position."""
    try:
        if IS_MAC:
            from opendesk.tools.mac.accessibility import Accessibility
            return Accessibility.type_text(text, interval=interval)
        elif IS_WINDOWS:
            from opendesk.tools.windows.uia import UIAutomation
            return UIAutomation.type_text(text, interval=interval)
        elif IS_LINUX:
            from opendesk.tools.linux.x11_utils import X11Automation
            return X11Automation.type_text(text, interval=interval)
    except Exception as e:
        if "not allowed" in str(e).lower() and "access" in str(e).lower():
            return {"error": str(e), "suggestion": "Grant Accessibility permission in System Settings → Privacy & Security → Accessibility"}
        raise
    return {"success": False}


def press_key(key: str) -> dict:
    """Press a keyboard shortcut."""
    try:
        if IS_MAC:
            from opendesk.tools.mac.accessibility import Accessibility
            return Accessibility.press_key(key)
        elif IS_WINDOWS:
            from opendesk.tools.windows.uia import UIAutomation
            return UIAutomation.press_key(key)
        elif IS_LINUX:
            from opendesk.tools.linux.x11_utils import X11Automation
            return X11Automation.press_key(key)
    except Exception as e:
        if "not allowed" in str(e).lower() and "access" in str(e).lower():
            return {"error": str(e), "suggestion": "Grant Accessibility permission in System Settings → Privacy & Security → Accessibility"}
        raise
    return {"success": False}


def scroll(direction: str, amount: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.accessibility import Accessibility

        return Accessibility.scroll(direction, amount, x, y)
    elif IS_WINDOWS:
        from opendesk.tools.windows.uia import UIAutomation

        return UIAutomation.scroll(direction, amount, x, y)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import X11Automation

        return X11Automation.scroll(direction, amount, x, y)
    return {"success": False}


def drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.accessibility import Accessibility

        return Accessibility.drag(from_x, from_y, to_x, to_y, duration)
    elif IS_WINDOWS:
        from opendesk.tools.windows.uia import UIAutomation

        return UIAutomation.drag(from_x, from_y, to_x, to_y, duration)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import X11Automation

        return X11Automation.drag(from_x, from_y, to_x, to_y, duration)
    return {"success": False}