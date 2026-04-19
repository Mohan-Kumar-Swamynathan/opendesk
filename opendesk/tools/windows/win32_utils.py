import subprocess
import ctypes
from typing import Optional
import base64
import io


def get_active_window() -> dict:
    try:
        import win32gui
        import win32process

        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = win32gui.GetWindowText(hwnd)

        try:
            proc = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
            )
            app_name = proc.stdout.split('"')[1] if proc.stdout else "Unknown"
        except Exception:
            app_name = "Unknown"

        return {"app_name": app_name, "window_title": title, "window_id": str(hwnd)}
    except Exception:
        return {"app_name": "", "window_title": "", "window_id": ""}


def list_windows(app_filter: Optional[str] = None) -> list[dict]:
    windows = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    import win32process
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                        capture_output=True,
                        text=True,
                    )
                    app_name = proc.stdout.split('"')[1] if proc.stdout else "Unknown"
                    windows.append({
                        "app_name": app_name,
                        "title": title,
                        "window_id": str(hwnd),
                        "is_minimized": False,
                    })
                except Exception:
                    pass
        return True

    try:
        import win32gui
        win32gui.EnumWindows(callback, None)
    except Exception:
        pass

    if app_filter:
        windows = [w for w in windows if app_filter.lower() in w["app_name"].lower()]

    return windows


def send_notification(title: str, message: str, urgency: str = "normal") -> dict:
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=3)
        return {"success": True}
    except Exception:
        subprocess.run(["msg", "*", f"{title}: {message}"], check=False)
        return {"success": True}


def open_application(app_name: str, args: Optional[list] = None) -> dict:
    try:
        import os

        if args:
            cmd = [app_name] + args
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen([app_name])
        return {"success": True, "pid": proc.pid}
    except Exception:
        return {"success": False, "pid": 0}


def close_application(app_name: str, force: bool = False) -> dict:
    try:
        if force:
            subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"], check=False)
        else:
            subprocess.run(["taskkill", "/IM", f"{app_name}.exe"], check=False)
        return {"success": True}
    except Exception:
        return {"success": False}


def focus_application(app_name: str) -> dict:
    try:
        import win32gui

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if app_name.lower() in title.lower():
                    win32gui.SetForegroundWindow(hwnd)
                    return False
            return True

        import win32gui
        win32gui.EnumWindows(callback, None)
        return {"success": True}
    except Exception:
        return {"success": False}


def take_screenshot(save_path: Optional[str] = None, monitor: int = 0) -> dict:
    try:
        from PIL import ImageGrab

        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()

        if save_path:
            img.save(save_path)

        return {
            "image_base64": base64.b64encode(data).decode(),
            "saved_to": save_path,
            "width": img.width,
            "height": img.height,
        }
    except Exception as e:
        return {"image_base64": "", "saved_to": None, "width": 0, "height": 0, "error": str(e)}


def get_volume() -> dict:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(interface=ISpeakerVolume._iid_, clsctx=1, server=None)
        volume = interface.QueryInterface(ISpeakerVolume)
        return {"volume": int(volume.GetMasterVolumeLevelScalar() * 100), "is_muted": volume.GetMute()}
    except Exception:
        return {"volume": 50, "is_muted": False}


def set_volume(level: int) -> dict:
    try:
        from pycaw.pycaw import AudioUtilities
        from comtypes import CLSCTX_ALL

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(interface=ISpeakerVolume._iid_, clsctx=1, server=None)
        volume = interface.QueryInterface(ISpeakerVolume)
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return {"success": True, "new_level": level}
    except Exception:
        return {"success": False, "new_level": level}


def mute() -> dict:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(interface=ISpeakerVolume._iid_, clsctx=1, server=None)
        volume = interface.QueryInterface(ISpeakerVolume)
        volume.SetMute(True, None)
        return {"success": True}
    except Exception:
        return {"success": False}


def unmute() -> dict:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(interface=ISpeakerVolume._iid_, clsctx=1, server=None)
        volume = interface.QueryInterface(ISpeakerVolume)
        volume.SetMute(False, None)
        return {"success": True}
    except Exception:
        return {"success": False}


class ISpeakerVolume(ctypes.ComInterface):
    _iid_ = "{c27020c2-7f00-11d9-b115-000a27052861}"

    @abstractmethod
    def SetMasterVolumeLevel(self, level: float, event_context: ctypes.c_void_p) -> ctypes.HRESULT:
        ...

    @abstractmethod
    def GetMasterVolumeLevel(self) -> float:
        ...

    @abstractmethod
    def SetMute(self, muted: bool, event_context: ctypes.c_void_p) -> ctypes.HRESULT:
        ...

    @abstractmethod
    def GetMute(self) -> bool:
        ...

    @abstractmethod
    def GetMasterVolumeLevelScalar(self) -> float:
        ...

    @abstractmethod
    def SetMasterVolumeLevelScalar(self, level: float, event_context: ctypes.c_void_p) -> ctypes.HRESULT:
        ...


from ctypes import ComInterface, abstractmethod
