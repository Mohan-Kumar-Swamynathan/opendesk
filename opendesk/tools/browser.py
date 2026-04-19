import subprocess
import json
from typing import Optional

from opendesk.platform_utils import IS_MAC


def get_open_tabs(browser: Optional[str] = None) -> dict:
    """Get open tabs from browsers."""
    tabs = []
    
    if not IS_MAC:
        return {"tabs": [], "total": 0, "error": "Browser tabs only supported on macOS"}

    browsers = ["Google Chrome", "Safari", "Firefox"]
    if browser:
        browsers = [browser]

    for b in browsers:
        try:
            if b == "Google Chrome":
                script = '''tell application "Google Chrome"
set tabData to {}
repeat with w in windows
    set windowTabs to tabs of w
    repeat with t in windowTabs
        set end of tabData to {title:(name of t) as text, url:(URL of t) as text}
    end repeat
end repeat
return tabData
end tell'''
            elif b == "Safari":
                script = '''tell application "Safari"
set tabData to {}
repeat with w in windows
    set windowTabs to tabs of w
    repeat with t in windowTabs
        set end of tabData to {title:(name of t) as text, url:(URL of t) as text}
    end repeat
end repeat
return tabData
end tell'''
            else:
                continue
                
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                tab_list = parse_applescript_output(result.stdout.strip())
                
                for tab in tab_list:
                    tabs.append({
                        "title": tab.get("title", "Untitled"),
                        "url": tab.get("url", ""),
                        "active": False,
                        "browser": b,
                    })
        except Exception as e:
            pass

    return {"tabs": tabs, "total": len(tabs)}


def parse_applescript_output(output: str) -> list:
    """Parse AppleScript output like: name:X, URL:Y, name:A, URL:B"""
    tabs = []
    current = {}
    
    parts = output.split(", ")
    for part in parts:
        if ":" in part and not part.startswith("URL:"):
            current["title"] = part.split(":", 1)[1]
            if "url" in current:
                tabs.append(current)
                current = {}
        elif part.startswith("URL:"):
            current["url"] = part.split(":", 1)[1]
            if "title" in current:
                tabs.append(current)
                current = {}
    
    if current and "title" in current:
        tabs.append(current)
    
    return tabs


def open_url(url: str, new_tab: bool = True) -> dict:
    """Open a URL in browser."""
    try:
        import webbrowser
        webbrowser.open(url, new=not new_tab)
        return {"success": True, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}