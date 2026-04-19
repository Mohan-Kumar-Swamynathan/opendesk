"""Screen capture and OCR tools."""
from typing import Optional

from opendesk.platform_utils import IS_MAC, IS_WINDOWS, IS_LINUX


def take_screenshot(save_path: Optional[str] = None, monitor: int = 0) -> dict:
    """Take a screenshot of the screen."""
    if IS_MAC:
        from opendesk.tools.mac.applescript import take_screenshot as mac_screenshot
        return mac_screenshot(save_path=save_path, monitor=monitor)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import take_screenshot as win_screenshot
        return win_screenshot(save_path=save_path, monitor=monitor)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import take_screenshot as linux_screenshot
        return linux_screenshot(save_path=save_path, monitor=monitor)
    return {"error": "Unsupported OS"}


def get_active_window() -> dict:
    """Get the currently active window."""
    if IS_MAC:
        from opendesk.tools.mac.applescript import get_active_window as mac_active
        return mac_active()
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import get_active_window as win_active
        return win_active()
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import get_active_window as linux_active
        return linux_active()
    return {"app_name": "", "window_title": "", "window_id": ""}


def list_open_windows(app_filter: Optional[str] = None) -> dict:
    """List all open windows."""
    if IS_MAC:
        from opendesk.tools.mac.applescript import list_windows as mac_windows
        return mac_windows(app_filter=app_filter)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import list_windows as win_windows
        return win_windows(app_filter=app_filter)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import list_windows as linux_windows
        return linux_windows(app_filter=app_filter)
    return {"windows": []}


def get_screen_text(languages: Optional[str] = None) -> dict:
    """Extract text from screen using OCR."""
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        screenshot_result = take_screenshot()
        if "error" in screenshot_result:
            return screenshot_result
            
        from opendesk.platform_utils import IS_MAC
        if IS_MAC:
            import subprocess
            result = subprocess.run(
                ["screencapture", "-x", "/tmp/opendesk_screen.png"],
                capture_output=True
            )
            img = Image.open("/tmp/opendesk_screen.png")
        else:
            img = Image.frombytes("RGB", screenshot_result["size"], screenshot_result["data"])
        
        text = pytesseract.image_to_string(img, lang=languages or "eng")
        
        return {"text": text.strip(), "confidence": 0.0}
        
    except ImportError:
        return {
            "text": "",
            "error": "OCR not installed. Run: pip install opendesk[ocr]",
            "suggestion": "Install OCR support: pip install -e '.[ocr]'"
        }
    except Exception as e:
        return {"text": "", "error": str(e)}