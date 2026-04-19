from typing import Optional
import subprocess


class Accessibility:
    @staticmethod
    def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        btn = ""
        if button == "right":
            btn = "using right button"
        elif button == "middle":
            btn = "using middle button"
        else:
            btn = "using left button"

        script = f'''
            tell application "System Events"
                set mousePos to {{{x}, {y}}}
                click at mousePos
            end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True, "coordinates": {"x": x, "y": y}}

    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> dict:
        import pyperclip
        original = pyperclip.paste()
        pyperclip.copy(text)
        script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        import time
        time.sleep(interval)
        pyperclip.copy(original)
        return {"success": True, "characters_typed": len(text)}

    @staticmethod
    def press_key(key: str) -> dict:
        mapping = {
            "enter": "return",
            "escape": "escape",
            "cmd": "command",
            "command": "command",
            "ctrl": "control",
            "control": "control",
            "alt": "option",
            "option": "option",
            "shift": "shift",
            "tab": "tab",
            "space": " ",
            "up": "up arrow",
            "down": "down arrow",
            "left": "left arrow",
            "right": "right arrow",
        }
        key_lower = key.lower()
        parts = key_lower.split("+")
        modifiers = []
        main_key = None

        for part in parts:
            part = part.strip()
            if part in mapping:
                mod = mapping[part]
                if mod not in ["return", "escape", " ", "up arrow", "down arrow", "left arrow", "right arrow", "tab"]:
                    modifiers.append(mod + " down")
                else:
                    main_key = mod
            else:
                main_key = part

        if modifiers and main_key:
            script = f'''
                tell application "System Events"
                    keystroke "{main_key}" using {", ".join(modifiers)}
                end tell
            '''
        elif main_key:
            script = f'''
                tell application "System Events"
                    keystroke "{main_key}"
                end tell
            '''
        else:
            return {"success": False}

        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True}

    @staticmethod
    def scroll(direction: str, amount: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        delta = amount if direction in ["down", "right"] else -amount
        axis = "y" if direction in ["up", "down"] else "x"

        script = f'''
            tell application "System Events"
                scroll {axis} {delta}
            end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True}

    @staticmethod
    def drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> dict:
        script = f'''
            tell application "System Events"
                set mousePos to {{{from_x}, {from_y}}}
                click at mousePos
                delay {duration}
                set dragPos to {{{to_x}, {to_y}}}
                click at dragPos
            end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        return {"success": True}
