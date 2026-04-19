import subprocess
import os
from typing import Optional
import base64


def run_x11_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def get_active_window() -> dict:
    try:
        script = """
            wmctrl -a :ACTIVE: -v 2>&1 | head -1
        """
        result = run_x11_cmd(["bash", "-c", script])
        parts = result.split()
        if len(parts) >= 2:
            return {"app_name": parts[0], "window_title": " ".join(parts[1:]), "window_id": ""}
    except Exception:
        pass
    return {"app_name": "", "window_title": "", "window_id": ""}


def list_windows(app_filter: Optional[str] = None) -> list[dict]:
    windows = []
    try:
        result = run_x11_cmd(["wmctrl", "-l"])
        for line in result.split("\n"):
            if line.strip():
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    windows.append({
                        "app_name": parts[2],
                        "title": parts[3],
                        "window_id": parts[0],
                        "is_minimized": False,
                    })
    except Exception:
        pass

    if app_filter:
        windows = [w for w in windows if app_filter.lower() in w["app_name"].lower()]

    return windows


def send_notification(title: str, message: str, urgency: str = "normal") -> dict:
    try:
        subprocess.run(
            ["notify-send", "-u", urgency, title, message],
            check=True,
        )
        return {"success": True}
    except Exception:
        return {"success": False}


def open_application(app_name: str, args: Optional[list] = None) -> dict:
    try:
        cmd = [app_name]
        if args:
            cmd.extend(args)
        proc = subprocess.Popen(cmd)
        return {"success": True, "pid": proc.pid}
    except Exception:
        return {"success": False, "pid": 0}


def close_application(app_name: str, force: bool = False) -> dict:
    try:
        if force:
            subprocess.run(["pkill", "-9", "-f", app_name], check=False)
        else:
            subprocess.run(["pkill", "-f", app_name], check=False)
        return {"success": True}
    except Exception:
        return {"success": False}


def focus_application(app_name: str) -> dict:
    try:
        run_x11_cmd(["wmctrl", "-a", app_name])
        return {"success": True}
    except Exception:
        return {"success": False}


def take_screenshot(save_path: Optional[str] = None, monitor: int = 0) -> dict:
    import tempfile
    import os

    tmp = save_path or tempfile.mktemp(suffix=".png")
    try:
        subprocess.run(["scrot", tmp], check=True, capture_output=True)
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
    except Exception as e:
        return {
            "image_base64": "",
            "saved_to": None,
            "width": 0,
            "height": 0,
            "error": str(e),
        }


def get_volume() -> dict:
    try:
        result = run_x11_cmd(["amixer", "sget", "Master"])
        for line in result.split("\n"):
            if "%" in line:
                import re
                match = re.search(r"(\d+)%", line)
                if match:
                    is_muted = "off" in line.lower()
                    return {"volume": int(match.group(1)), "is_muted": is_muted}
    except Exception:
        pass
    return {"volume": 50, "is_muted": False}


def set_volume(level: int) -> dict:
    try:
        subprocess.run(["amixer", "sset", "Master", f"{level}%"], check=True, capture_output=True)
        return {"success": True, "new_level": level}
    except Exception:
        return {"success": False, "new_level": level}


def mute() -> dict:
    try:
        subprocess.run(["amixer", "sset", "Master", "mute"], check=True, capture_output=True)
        return {"success": True}
    except Exception:
        return {"success": False}


def unmute() -> dict:
    try:
        subprocess.run(["amixer", "sset", "Master", "unmute"], check=True, capture_output=True)
        return {"success": True}
    except Exception:
        return {"success": False}


class X11Automation:
    @staticmethod
    def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        btn = "1"
        if button == "right":
            btn = "3"
        elif button == "middle":
            btn = "2"

        for _ in range(clicks):
            subprocess.run(["xdotool", "mousedown", btn], check=False)
            subprocess.run(["xdotool", "mouseup", btn], check=False)

        return {"success": True, "coordinates": {"x": x, "y": y}}

    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> dict:
        try:
            subprocess.run(["xdotool", "type", "--", text], check=True)
            return {"success": True, "characters_typed": len(text)}
        except Exception:
            return {"success": False, "characters_typed": 0}

    @staticmethod
    def press_key(key: str) -> dict:
        key = key.lower().replace("cmd", "super").replace("command", "super")
        key = key.replace("ctrl", "ctrl").replace("escape", "escape")
        parts = key.split("+")
        cmd = ["xdotool"]
        for p in parts:
            cmd.extend(["key", p.strip()])
        try:
            subprocess.run(cmd, check=True)
            return {"success": True}
        except Exception:
            return {"success": False}

    @staticmethod
    def scroll(direction: str, amount: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        btn = "4" if direction in ["up", "left"] else "5"
        if direction in ["left", "right"]:
            for _ in range(amount):
                subprocess.run(["xdotool", "click", "6" if direction == "left" else "7"], check=False)
        else:
            for _ in range(amount):
                subprocess.run(["xdotool", "click", btn], check=False)
        return {"success": True}

    @staticmethod
    def drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> dict:
        try:
            subprocess.run(["xdotool", "mousedown", "1"], check=True)
            subprocess.run(
                ["xdotool", "mousemove", str(to_x), str(to_y)],
                check=True,
            )
            subprocess.run(["xdotool", "mouseup", "1"], check=True)
            return {"success": True}
        except Exception:
            return {"success": False}
