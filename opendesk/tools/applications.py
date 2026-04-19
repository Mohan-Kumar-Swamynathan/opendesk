import subprocess
from typing import Optional
from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def open_application(app_name: str, args: Optional[list[str]] = None) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import open_application as mac_open

        return mac_open(app_name, args)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import open_application as win_open

        return win_open(app_name, args)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import open_application as linux_open

        return linux_open(app_name, args)
    return {"success": False, "pid": 0}


def close_application(app_name: str, force: bool = False) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import close_application as mac_close

        return mac_close(app_name, force)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import close_application as win_close

        return win_close(app_name, force)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import close_application as linux_close

        return linux_close(app_name, force)
    return {"success": False}


def focus_application(app_name: str) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import focus_application as mac_focus

        return mac_focus(app_name)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import focus_application as win_focus

        return win_focus(app_name)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import focus_application as linux_focus

        return linux_focus(app_name)
    return {"success": False}


def list_installed_apps(filter: Optional[str] = None) -> dict:
    apps = []

    if IS_MAC:
        try:
            result = subprocess.run(
                ["mdfind", "kMDItemKind == 'Application'"],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.split("\n"):
                if line.strip():
                    name = line.split("/")[-1].replace(".app", "")
                    if filter and filter.lower() not in name.lower():
                        continue
                    apps.append({"name": name, "path": line, "version": ""})
        except Exception:
            pass
    elif IS_WINDOWS:
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
            )
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(key, i)
                    if filter and filter.lower() not in name.lower():
                        continue
                    apps.append({"name": name, "path": name, "version": ""})
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    elif IS_LINUX:
        try:
            result = subprocess.run(
                ["ls", "/usr/share/applications"],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.split("\n"):
                if line.strip() and line.endswith(".desktop"):
                    name = line.replace(".desktop", "")
                    if filter and filter.lower() not in name.lower():
                        continue
                    apps.append({"name": name, "path": f"/usr/share/applications/{line}", "version": ""})
        except Exception:
            pass

    return {"apps": apps, "total": len(apps)}