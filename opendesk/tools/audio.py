from opendesk.platform_utils import OS, IS_MAC, IS_WINDOWS, IS_LINUX


def get_volume() -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import get_volume as mac_volume

        return mac_volume()
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import get_volume as win_volume

        return win_volume()
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import get_volume as linux_volume

        return linux_volume()
    return {"volume": 50, "is_muted": False}


def set_volume(level: int) -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import set_volume as mac_set_volume

        return mac_set_volume(level)
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import set_volume as win_set_volume

        return win_set_volume(level)
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import set_volume as linux_set_volume

        return linux_set_volume(level)
    return {"success": False, "new_level": level}


def mute() -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import mute as mac_mute

        return mac_mute()
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import mute as win_mute

        return win_mute()
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import mute as linux_mute

        return linux_mute()
    return {"success": False}


def unmute() -> dict:
    if IS_MAC:
        from opendesk.tools.mac.applescript import unmute as mac_unmute

        return mac_unmute()
    elif IS_WINDOWS:
        from opendesk.tools.windows.win32_utils import unmute as win_unmute

        return win_unmute()
    elif IS_LINUX:
        from opendesk.tools.linux.x11_utils import unmute as linux_unmute

        return linux_unmute()
    return {"success": False}