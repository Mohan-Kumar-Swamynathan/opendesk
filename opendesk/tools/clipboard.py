import pyperclip
from typing import Optional
from opendesk.platform_utils import IS_MAC


def get_clipboard() -> dict:
    try:
        content = pyperclip.paste()
        return {"content": content, "content_type": "text"}
    except Exception as e:
        return {"content": "", "content_type": "text", "error": str(e)}


def set_clipboard(content: str) -> dict:
    try:
        pyperclip.copy(content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}