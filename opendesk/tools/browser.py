import subprocess
import webbrowser
from typing import Optional
from opendesk.platform_utils import IS_MAC


def get_open_tabs(browser: Optional[str] = None) -> dict:
    tabs = []

    if IS_MAC:
        browsers = ["Safari", "Google Chrome", "Firefox"]
        if browser:
            browsers = [browser]

        for b in browsers:
            try:
                script = f'''
                    tell application "{b}"
                        set tabList to {{}}
                        if (count of windows) > 0 then
                            repeat with w in windows
                                repeat with t in tabs of w
                                    set end of tabList to {{title: name of t, url: URL of t, active: false}}
                                end repeat
                            end repeat
                        end if
                        return tabList
                    end tell
                '''
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split("\n"):
                        if "|||" in line:
                            parts = line.split("|||")
                            tabs.append({
                                "title": parts[0],
                                "url": parts[1] if len(parts) > 1 else "",
                                "active": False,
                                "browser": b,
                            })
            except Exception:
                pass
    else:
        return {"tabs": [], "total": 0, "error": "Browser tabs only supported on macOS"}

    return {"tabs": tabs, "total": len(tabs)}


def open_url(url: str, new_tab: bool = True) -> dict:
    try:
        if new_tab:
            webbrowser.open(url, new=2)
        else:
            webbrowser.open(url)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}