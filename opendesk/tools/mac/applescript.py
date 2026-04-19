import subprocess
import os
from typing import Optional


def run_applescript(script: str) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"AppleScript error: {proc.stderr}")
    return proc.stdout.strip()


def get_active_window() -> dict:
    script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            set appName to name of frontApp
            set win to first window of frontApp
            set winTitle to name of win
            return appName & "|||" & winTitle
        end tell
    '''
    result = run_applescript(script)
    parts = result.split("|||")
    return {"app_name": parts[0], "window_title": parts[1] if len(parts) > 1 else "", "window_id": ""}


def list_windows(app_filter: Optional[str] = None) -> list[dict]:
    script = '''
        tell application "System Events"
            set windowList to {}
            repeat with proc in application processes
                set procName to name of proc
                if procName is not equal to "Finder" then
                    try
                        repeat with win in windows of proc
                            set winName to name of win
                            set winPos to position of win
                            set end of windowList to procName & "|||" & winName
                        end repeat
                    end try
                end if
            end repeat
            return windowList as text
        end tell
    '''
    result = run_applescript(script)
    windows = []
    for line in result.split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            windows.append({
                "app_name": parts[0],
                "title": parts[1] if len(parts) > 1 else "",
                "window_id": "",
                "is_minimized": False,
            })
    if app_filter:
        windows = [w for w in windows if app_filter.lower() in w["app_name"].lower()]
    return windows


def send_notification(title: str, message: str, urgency: str = "normal") -> dict:
    script = f'''
        display notification "{message}" with title "{title}"
    '''
    run_applescript(script)
    return {"success": True}


def open_application(app_name: str, args: Optional[list] = None) -> dict:
    cmd = ["open", "-a", app_name]
    if args:
        cmd.extend(args)
    proc = subprocess.run(cmd, capture_output=True, check=False)
    return {"success": proc.returncode == 0, "pid": 0}


def close_application(app_name: str, force: bool = False) -> dict:
    script = f'''
        tell application "{app_name}"
            quit
        end tell
    '''
    try:
        run_applescript(script)
        return {"success": True}
    except Exception:
        return {"success": False}


def focus_application(app_name: str) -> dict:
    script = f'''
        tell application "{app_name}"
            activate
        end tell
    '''
    run_applescript(script)
    return {"success": True}


def take_screenshot(save_path: Optional[str] = None, monitor: int = 0) -> dict:
    import tempfile
    import base64

    tmp = save_path or tempfile.mktemp(suffix=".png")
    subprocess.run(["screencapture", "-x", tmp], check=True)
    with open(tmp, "rb") as f:
        data = f.read()
    if not save_path:
        os.unlink(tmp)
    return {
        "image_base64": base64.b64encode(data).decode(),
        "saved_to": save_path,
        "width": 0,
        "height": 0,
    }


def get_volume() -> dict:
    script = '''
        output volume of (get volume settings)
    '''
    volume = run_applescript(script)
    return {"volume": int(volume) if volume else 0, "is_muted": False}


def set_volume(level: int) -> dict:
    script = f'''
        set volume output volume {level}
    '''
    run_applescript(script)
    return {"success": True, "new_level": level}


def mute() -> dict:
    script = '''
        set volume output muted true
    '''
    run_applescript(script)
    return {"success": True}


def unmute() -> dict:
    script = '''
        set volume output muted false
    '''
    run_applescript(script)
    return {"success": True}


def get_clipboard() -> dict:
    import pyperclip
    content = pyperclip.paste()
    return {"content": content, "content_type": "text"}


def set_clipboard(content: str) -> dict:
    import pyperclip
    pyperclip.copy(content)
    return {"success": True}