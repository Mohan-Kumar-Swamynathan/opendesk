import psutil
import platform
import time
from typing import Optional


def list_processes(sort_by: str = "cpu", limit: int = 20, filter_name: Optional[str] = None) -> dict:
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
        try:
            info = proc.info
            if filter_name and filter_name.lower() not in info["name"].lower():
                continue
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"] or 0.0,
                "memory_mb": round(info["memory_info"].rss / (1024 * 1024), 1) if info["memory_info"] else 0.0,
                "status": info["status"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if sort_by == "cpu":
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x["memory_mb"], reverse=True)
    elif sort_by == "name":
        processes.sort(key=lambda x: x["name"])
    elif sort_by == "pid":
        processes.sort(key=lambda x: x["pid"], reverse=True)

    return {"processes": processes[:limit], "total_processes": len(processes)}


def kill_process(identifier: str | int, force: bool = False) -> dict:
    killed_pids = []

    try:
        if isinstance(identifier, int):
            pids = [identifier]
        else:
            pids = [p.pid for p in psutil.process_iter() if p.name().lower() == identifier.lower()]

        for pid in pids:
            try:
                proc = psutil.Process(pid)
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                killed_pids.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        gone, alive = psutil.wait_procs(killed_pids, timeout=3)
        for p in alive:
            try:
                psutil.Process(p.pid).kill()
            except:
                pass

        return {"success": len(killed_pids) > 0, "killed_pids": killed_pids}
    except Exception as e:
        return {"success": False, "error": str(e), "killed_pids": killed_pids}


def get_system_info() -> dict:
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        battery = None
        battery_percent = None
        battery_charging = None

        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = battery.percent
                battery_charging = battery.power_plugged

        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time

        return {
            "cpu_percent": cpu_percent,
            "cpu_cores": psutil.cpu_count(),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": round(memory.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "battery_percent": battery_percent,
            "battery_charging": battery_charging,
            "uptime_hours": round(uptime_seconds / 3600, 1),
            "os": platform.system(),
            "hostname": platform.node(),
        }
    except Exception as e:
        return {"error": str(e)}


def get_network_info() -> dict:
    try:
        interfaces = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for name, addr_list in addrs.items():
            is_up = stats[name].isup if name in stats else False
            for addr in addr_list:
                if addr.family == psutil.AF_INET:
                    interfaces.append({
                        "name": name,
                        "ip": addr.address,
                        "mac": "",
                        "is_up": is_up,
                    })

        wifi_network = None
        is_connected = False

        try:
            wifi = psutil.net_if_stats()
            for name, stat in wifi.items():
                if stat.isup and "wi-fi" in name.lower() or "wifi" in name.lower():
                    is_connected = True
                    break
        except Exception:
            pass

        return {
            "interfaces": interfaces,
            "wifi_network": wifi_network,
            "is_connected": is_connected,
        }
    except Exception as e:
        return {"interfaces": [], "wifi_network": None, "is_connected": False, "error": str(e)}