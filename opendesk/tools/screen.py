from typing import Optional
from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def take_screenshot(save_path: Optional[str] = None, monitor: int = 0) -> dict:
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
    if IS_MAC:
        from opendesk.tools.mac.applescript import list_windows as mac_windows

        windows = mac_windows(app_filter=app_filter)
        return {"windows": windows, "total": len(windows)}
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import list_windows as win_windows

        windows = win_windows(app_filter=app_filter)
        return {"windows": windows, "total": len(windows)}
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import list_windows as linux_windows

        windows = linux_windows(app_filter=app_filter)
        return {"windows": windows, "total": len(windows)}
    return {"windows": [], "total": 0}


def get_screen_text(region: Optional[dict] = None) -> dict:
    try:
        import pytesseract
        from PIL import Image

        screenshot_result = take_screenshot()
        if "image_base64" in screenshot_result:
            import base64
            import io

            img_data = base64.b64decode(screenshot_result["image_base64"])
            img = Image.open(io.BytesIO(img_data))

            if region:
                x = region.get("x", 0)
                y = region.get("y", 0)
                w = region.get("width", img.width)
                h = region.get("height", img.height)
                img = img.crop((x, y, x + w, y + h))

            text = pytesseract.image_to_string(img)
            return {"text": text, "confidence": 0.9}
    except ImportError:
        return {"text": "", "error": "pytesseract not installed", "confidence": 0.0}
    except Exception as e:
        return {"text": "", "error": str(e), "confidence": 0.0}

    return {"text": "", "error": "Failed to capture screen", "confidence": 0.0}