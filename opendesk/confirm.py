"""Native confirmation dialogs."""
import os
import shutil
import subprocess
import sys
import time
from typing import Optional

TEST_MODE = os.environ.get("OPENDESK_TEST_MODE", "0") == "1"


def confirm(title: str, message: str, timeout: int = 60) -> bool:
    """Show native OS dialog. Returns True if user approves."""
    if TEST_MODE:
        import logging
        logging.warning("OPENDESK_TEST_MODE=1: auto-approving confirmation")
        return True

    try:
        if sys.platform == "darwin":
            return _confirm_mac(title, message, timeout)
        elif sys.platform == "win32":
            return _confirm_windows(title, message, timeout)
        elif sys.platform == "linux":
            return _confirm_linux(title, message, timeout)
    except Exception:
        pass
    return False


def _confirm_mac(title: str, message: str, timeout: int) -> bool:
    """macOS confirmation using osascript."""
    safe_msg = message.replace('"', '\\"').replace("\n", "\\n")
    safe_title = title.replace('"', '\\"')

    script = f'''
    display dialog "{safe_msg}" ¬
        with title "{safe_title}" ¬
        buttons {{"Deny", "Allow"}} ¬
        default button "Deny" ¬
        cancel button "Deny" ¬
        with icon caution ¬
        giving up after {timeout}
    '''

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=timeout + 5
    )
    return "Allow" in result.stdout and "gave up:true" not in result.stdout


def _confirm_windows(title: str, message: str, timeout: int) -> bool:
    """Windows confirmation using MessageBoxTimeout."""
    import ctypes
    from ctypes import wintypes

    MB_OKCANCEL = 0x1
    MB_ICONWARNING = 0x30
    MB_TOPMOST = 0x40000
    MB_SYSTEMMODAL = 0x1000
    MB_DEFBUTTON2 = 0x100

    user32 = ctypes.windll.user32

    try:
        MessageBoxTimeout = user32.MessageBoxTimeoutW
        MessageBoxTimeout.argtypes = [
            wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR,
            wintypes.UINT, wintypes.UINT16, wintypes.UINT32
        ]

        result = MessageBoxTimeout(
            None, message, title,
            MB_OKCANCEL | MB_ICONWARNING | MB_TOPMOST | MB_SYSTEMMODAL | MB_DEFBUTTON2,
            0, timeout * 1000
        )
        return result == 1
    except Exception:
        return False


def _confirm_linux(title: str, message: str, timeout: int) -> bool:
    """Linux confirmation using zenity or kdialog."""
    if shutil.which("zenity"):
        result = subprocess.run([
            "zenity", "--question",
            "--title", title,
            "--text", message,
            "--ok-label=Allow",
            "--cancel-label=Deny",
            f"--timeout={timeout}",
        ], timeout=timeout + 5)
        return result.returncode == 0

    if shutil.which("kdialog"):
        result = subprocess.run([
            "kdialog", "--title", title,
            "--warningyesno", message,
        ], timeout=timeout + 5)
        return result.returncode == 0

    return False