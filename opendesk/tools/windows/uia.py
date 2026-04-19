from typing import Optional


class UIAutomation:
    @staticmethod
    def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        try:
            import win32api
            import win32con

            btn = win32con.MOUSEEVENTF_LEFTDOWN
            if button == "right":
                btn = win32con.MOUSEEVENTF_RIGHTDOWN
            elif button == "middle":
                btn = win32con.MOUSEEVENTF_MIDDLEDOWN

            win32api.SetCursorPos((x, y))
            win32api.mouse_event(btn, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

            if clicks == 2:
                win32api.mouse_event(btn, x, y, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

            return {"success": True, "coordinates": {"x": x, "y": y}}
        except Exception:
            return {"success": False, "coordinates": {"x": x, "y": y}}

    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> dict:
        try:
            import win32api
            import time

            for char in text:
                if char.isupper():
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                win32api.keybd_event(ord(char), 0, 0, 0)
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
                if char.isupper():
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(interval)

            return {"success": True, "characters_typed": len(text)}
        except Exception:
            return {"success": False, "characters_typed": 0}

    @staticmethod
    def press_key(key: str) -> dict:
        try:
            import win32api
            import win32con

            vk_codes = {
                "enter": win32con.VK_RETURN,
                "escape": win32con.VK_ESCAPE,
                "tab": win32con.VK_TAB,
                "space": win32con.VK_SPACE,
                "up": win32con.VK_UP,
                "down": win32con.VK_DOWN,
                "left": win32con.VK_LEFT,
                "right": win32con.VK_RIGHT,
                "ctrl": win32con.VK_CONTROL,
                "alt": win32con.VK_MENU,
                "shift": win32con.VK_SHIFT,
            }

            key_lower = key.lower()
            parts = key_lower.split("+")
            modifiers = []
            main_key = None

            for part in parts:
                part = part.strip()
                if part in vk_codes:
                    if part in ["ctrl", "alt", "shift"]:
                        modifiers.append(vk_codes[part])
                    else:
                        main_key = vk_codes[part]
                else:
                    main_key = ord(part.upper())

            for mod in modifiers:
                win32api.keybd_event(mod, 0, 0, 0)

            if main_key:
                win32api.keybd_event(main_key, 0, 0, 0)
                win32api.keybd_event(main_key, 0, win32con.KEYEVENTF_KEYUP, 0)

            for mod in reversed(modifiers):
                win32api.keybd_event(mod, 0, win32con.KEYEVENTF_KEYUP, 0)

            return {"success": True}
        except Exception:
            return {"success": False}

    @staticmethod
    def scroll(direction: str, amount: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        try:
            import win32api
            import win32con

            delta = amount * 120
            if direction in ["up", "down"]:
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, delta if direction == "up" else -delta, 0)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_HWHEEL, 0, 0, delta if direction == "right" else -delta, 0)

            return {"success": True}
        except Exception:
            return {"success": False}

    @staticmethod
    def drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> dict:
        try:
            import win32api
            import win32con
            import time

            win32api.SetCursorPos((from_x, from_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, from_x, from_y, 0, 0)

            steps = 10
            for i in range(steps):
                curr_x = from_x + (to_x - from_x) * i // steps
                curr_y = from_y + (to_y - from_y) * i // steps
                win32api.SetCursorPos((curr_x, curr_y))
                time.sleep(duration / steps)

            win32api.SetCursorPos((to_x, to_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, to_x, to_y, 0, 0)

            return {"success": True}
        except Exception:
            return {"success": False}
