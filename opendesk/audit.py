"""Audit logging — thread-safe, with sensitive data redaction."""
import fcntl
import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

SENSITIVE_KEYS = frozenset([
    "password", "token", "api_key", "secret", "auth", "bearer",
    "credential", "private_key", "access_token", "refresh_token",
])

_audit_lock = threading.Lock() if sys.platform == "win32" else None


def get_audit_log_path() -> Path:
    log_dir = Path.home() / ".opendesk"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "audit.log"


def _redact_sensitive(args: dict) -> dict:
    """Redact sensitive keys from arguments."""
    redacted = {}
    for key, value in args.items():
        lower_key = key.lower()
        if any(s in lower_key for s in SENSITIVE_KEYS):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def _rotate_if_needed(log_path: Path):
    """Rotate log file if it exceeds max size."""
    try:
        if log_path.exists() and log_path.stat().st_size > MAX_LOG_SIZE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated = log_path.with_suffix(f".log.{timestamp}")
            log_path.rename(rotated)
    except Exception:
        pass


def log_tool_call(
    tool_name: str,
    args: dict,
    success: bool,
    result_summary: str = "",
    error: str = None,
):
    """Log a tool call to audit log (thread-safe)."""
    log_path = get_audit_log_path()
    _rotate_if_needed(log_path)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "args": _redact_sensitive(args),
        "success": success,
        "result_summary": result_summary[:200] if result_summary else "",
        "error": error,
    }

    entry_json = json.dumps(entry)

    try:
        if sys.platform == "win32":
            with _audit_lock:
                with open(log_path, "a") as f:
                    f.write(entry_json + "\n")
        else:
            with open(log_path, "a") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(entry_json + "\n")
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass


def read_audit_log(limit: int = 50) -> list[dict]:
    """Read recent audit log entries."""
    log_path = get_audit_log_path()
    if not log_path.exists():
        return []

    try:
        lines = log_path.read_text().strip().split("\n")
        entries = []
        for line in lines[-limit:]:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return entries
    except Exception:
        return []


def clear_audit_log():
    """Clear the audit log."""
    log_path = get_audit_log_path()
    if log_path.exists():
        log_path.unlink()