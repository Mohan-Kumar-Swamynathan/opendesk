"""Safety model for opendesk."""
import re
import sys
import time
from pathlib import Path
from threading import Lock
from typing import Optional

from opendesk.errors import PathSafetyError, PermissionDeniedError, RateLimitError

PROTECTED_READONLY_PATHS = [
    "~/.ssh",
    "~/.aws",
    "~/.gnupg",
    "~/.config/gh",
    "~/.netrc",
    "~/Library/Keychains",
    "~/.bash_history",
    "~/.zsh_history",
    "~/.history",
    "~/.config/opendesk",
    "~/.opendesk",
]

PROTECTED_NEVER_PATHS = [
    "/System",
    "/usr/bin",
    "/bin",
    "/sbin",
    "C:\\Windows",
    "C:\\Program Files",
]

if sys.platform == "win32":
    PROTECTED_READONLY_PATHS.extend([
        "~/AppData/Local/Microsoft/Credentials",
    ])


DANGEROUS_PATTERNS = [
    (re.compile(r"\brm\s+-[rfRF]+\s+/\s*$"), "Recursive delete of root"),
    (re.compile(r"\brm\s+-[rfRF]+\s+~"), "Recursive delete of home"),
    (re.compile(r"\bmkfs\b"), "Filesystem format"),
    (re.compile(r"\bdd\s+if=.+of=/dev/[sh]d"), "Raw disk write"),
    (re.compile(r":\(\)\s*\{.*\};"), "Fork bomb"),
    (re.compile(r"\b(shutdown|reboot|halt|poweroff)\b"), "System power"),
    (re.compile(r"\bchmod\s+-R\s+777\s+/"), "Permissions wipe"),
    (re.compile(r">\s*/dev/[sh]d"), "Raw disk write"),
    (re.compile(r"\b(curl|wget).+\|\s*(bash|sh|zsh)\b"), "Pipe-to-shell"),
    (re.compile(r"\bsudo\b"), "sudo (never allowed)"),
]

RATE_LIMITS = {
    "delete_file": (5, 60),
    "kill_process": (3, 60),
    "write_file": (30, 60),
    "run_command": (20, 60),
    "type_text": (10, 1),
    "click": (10, 1),
}


class RateLimiter:
    def __init__(self):
        self._buckets = {}
        self._lock = Lock()

    def check_and_consume(self, tool_name: str) -> tuple[bool, int]:
        if tool_name not in RATE_LIMITS:
            return True, 0

        max_per_window, window_seconds = RATE_LIMITS[tool_name]

        with self._lock:
            now = time.time()
            if tool_name not in self._buckets:
                self._buckets[tool_name] = {"tokens": max_per_window, "last_refill": now}

            bucket = self._buckets[tool_name]
            elapsed = now - bucket["last_refill"]
            refill = elapsed * (max_per_window / window_seconds)
            bucket["tokens"] = min(max_per_window, bucket["tokens"] + refill)
            bucket["last_refill"] = now

            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True, 0
            else:
                needed = 1 - bucket["tokens"]
                retry_after = int(needed * window_seconds / max_per_window) + 1
                return False, retry_after


rate_limiter = RateLimiter()


def validate_path(path_input: str, operation: str = "read") -> Path:
    """Safely resolve a user-provided path."""
    try:
        expanded = Path(path_input).expanduser()
        resolved = expanded.resolve(strict=False)
    except (ValueError, OSError) as e:
        raise PathSafetyError(f"Invalid path: {path_input}")

    if any(p == ".." for p in resolved.parts):
        raise PathSafetyError(
            f"Path traversal rejected: {path_input}",
            suggestion="Use an absolute path without '..'"
        )

    for protected_str in PROTECTED_READONLY_PATHS:
        protected = Path(protected_str).expanduser().resolve(strict=False)
        try:
            resolved.relative_to(protected)
            if operation in ("write", "delete", "move"):
                raise PathSafetyError(
                    f"Protected path: {path_input}",
                    suggestion=f"This location contains sensitive data and is read-only."
                )
        except ValueError:
            pass

    for never_str in PROTECTED_NEVER_PATHS:
        never = Path(never_str).resolve(strict=False)
        try:
            resolved.relative_to(never)
            raise PathSafetyError(
                f"System path: {path_input}",
                suggestion="opendesk cannot operate on system paths"
            )
        except ValueError:
            pass

    return resolved


def check_dangerous_command(command: str) -> Optional[str]:
    """Returns danger description or None."""
    for pattern, description in DANGEROUS_PATTERNS:
        if pattern.search(command):
            if description == "sudo (never allowed)":
                return description
            return description
    return None


def check_rate_limit(tool_name: str):
    """Check rate limit for a tool. Raises RateLimitError if exceeded."""
    allowed, retry_after = rate_limiter.check_and_consume(tool_name)
    if not allowed:
        raise RateLimitError(
            f"Rate limit exceeded for {tool_name}",
            suggestion=f"Try again in {retry_after} seconds"
        )