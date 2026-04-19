from typing import Optional
from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.accessibility import Accessibility

        return Accessibility.click(x, y, button=button, clicks=clicks)
    elif IS_WINDOWS:
        from opendesk.tools.windows.uia import UIAutomation

        return UIAutomation.click(x, y, button=button, clicks=clicks)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import X11Automation

        return X11Automation.click(x, y, button=button, clicks=clicks)
    return {"success": False}


def type_text(text: str, interval: float = 0.05) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.accessibility import Accessibility

        return Accessibility.type_text(text, interval=interval)
    elif IS_WINDOWS:
        from opendesk.tools.windows.uia import UIAutomation

        return UIAutomation.type_text(text, interval=interval)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import X11Automation

        return X11Automation.type_text(text, interval=interval)
    return {"success": False}


def press_key(key: str) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.accessibility import Accessibility

        return Accessibility.press_key(key)
    elif IS_WINDOWS:
        from opendesk.tools.windows.uia import UIAutomation

        return UIAutomation.press_key(key)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import X11Automation

        return X11Automation.press_key(key)
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