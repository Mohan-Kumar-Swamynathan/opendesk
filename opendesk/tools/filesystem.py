import os
import shutil
import glob
import time
from pathlib import Path
from datetime import datetime
from typing import Optional


def read_file(path: str, encoding: str = "utf-8", max_bytes: int = 1048576) -> dict:
    file_path = Path(path).expanduser().absolute()

    if not file_path.exists():
        return {"error": "File not found", "path": str(file_path)}

    if file_path.stat().st_size > max_bytes:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read(max_bytes)
        return {"content": content, "size_bytes": file_path.stat().st_size, "encoding": encoding, "truncated": True}

    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        return {"content": content, "size_bytes": file_path.stat().st_size, "encoding": encoding, "truncated": False}
    except Exception as e:
        return {"error": str(e), "path": str(file_path)}


def write_file(path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> dict:
    file_path = Path(path).expanduser().absolute()

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return {"success": True, "path": str(file_path), "bytes_written": len(content.encode(encoding))}
    except Exception as e:
        return {"success": False, "path": str(file_path), "error": str(e)}


def list_directory(path: str = "~", show_hidden: bool = False, sort_by: str = "name", max_items: int = 100) -> dict:
    dir_path = Path(path).expanduser().absolute()

    if not dir_path.exists():
        return {"error": "Directory not found", "path": str(dir_path)}

    if not dir_path.is_dir():
        return {"error": "Path is not a directory", "path": str(dir_path)}

    items = []
    try:
        for item in dir_path.iterdir():
            if not show_hidden and item.name.startswith("."):
                continue

            stat_info = item.stat()
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "path": str(item),
            })
    except PermissionError:
        return {"error": "Permission denied", "path": str(dir_path)}

    if sort_by == "size":
        items.sort(key=lambda x: x["size"], reverse=True)
    elif sort_by == "modified":
        items.sort(key=lambda x: x["modified"], reverse=True)
    else:
        items.sort(key=lambda x: x["name"])

    return {"items": items[:max_items], "total_items": len(items), "path": str(dir_path)}


def search_files(query: str, directory: str = "~", search_content: bool = False, file_type: Optional[str] = None, max_results: int = 50) -> dict:
    search_dir = Path(directory).expanduser().absolute()

    if not search_dir.exists():
        return {"error": "Directory not found", "total_found": 0}

    results = []
    query_lower = query.lower()

    try:
        if search_content:
            for path in search_dir.rglob(f"*{query_lower}*"):
                if path.is_file():
                    if file_type and not path.suffix.endswith(file_type):
                        continue
                    results.append({
                        "path": str(path),
                        "name": path.name,
                        "size": path.stat().st_size,
                        "match_type": "content",
                    })
    except Exception as e:
        return {"error": str(e), "total_found": 0}

    if file_type:
        pattern = f"*.{file_type}" if not file_type.startswith(".") else f"*{file_type}"
    else:
        pattern = "*"

    try:
        for path in search_dir.rglob(pattern):
            if path.is_file() and query_lower in path.name.lower():
                results.append({
                    "path": str(path),
                    "name": path.name,
                    "size": path.stat().st_size,
                    "match_type": "name",
                })
    except Exception:
        pass

    results = results[:max_results]
    return {"files": results, "total_found": len(results)}


def get_recent_files(days: int = 7, directory: str = "~", file_type: Optional[str] = None, max_results: int = 20) -> dict:
    search_dir = Path(directory).expanduser().absolute()
    cutoff = time.time() - (days * 86400)

    results = []
    try:
        for path in search_dir.rglob("*"):
            if path.is_file():
                if file_type:
                    if not path.suffix.endswith(file_type):
                        continue
                if path.stat().st_mtime >= cutoff:
                    results.append({
                        "path": str(path),
                        "name": path.name,
                        "size": path.stat().st_size,
                        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    })
    except Exception as e:
        return {"error": str(e), "files": []}

    results.sort(key=lambda x: x["modified"], reverse=True)
    return {"files": results[:max_results], "total_found": len(results)}


def move_file(source: str, destination: str, overwrite: bool = False) -> dict:
    src = Path(source).expanduser().absolute()
    dst = Path(destination).expanduser().absolute()

    if not src.exists():
        return {"success": False, "error": "Source not found"}

    if dst.exists() and not overwrite:
        return {"success": False, "error": "Destination exists"}

    try:
        shutil.move(str(src), str(dst))
        return {"success": True, "new_path": str(dst)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file(path: str, permanent: bool = False) -> dict:
    file_path = Path(path).expanduser().absolute()

    if not file_path.exists():
        return {"success": False, "error": "Path not found"}

    try:
        if permanent:
            file_path.unlink() if file_path.is_file() else shutil.rmtree(file_path)
        else:
            trash_dir = Path("~/.local/share/Trash/files").expanduser()
            trash_dir.mkdir(parents=True, exist_ok=True)
            dest = trash_dir / file_path.name
            shutil.move(str(file_path), str(dest))

        return {"success": True, "path": str(file_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_disk_usage(path: str = "/") -> dict:
    try:
        import psutil

        usage = psutil.disk_usage(path)
        return {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent_used": round(usage.percent, 1),
        }
    except Exception as e:
        return {"error": str(e)}