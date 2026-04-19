from opendesk.platform_utils import IS_MAC, IS_WINDOWS, IS_LINUX


def send_notification(title: str, message: str, urgency: str = "normal") -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import send_notification as mac_notify

        return mac_notify(title, message, urgency)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import send_notification as win_notify

        return win_notify(title, message, urgency)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import send_notification as linux_notify

        return linux_notify(title, message, urgency)
    return {"success": False}