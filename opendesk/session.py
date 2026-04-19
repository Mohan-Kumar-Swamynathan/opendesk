"""Session state with bounded memory and TTL."""
import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Optional

MAX_SESSION_SIZE = 10 * 1024 * 1024  # 10MB total
SESSION_TTL = 3600  # 1 hour


class SessionState:
    """Bounded session state with TTL."""

    def __init__(self, max_size: int = MAX_SESSION_SIZE, ttl: int = SESSION_TTL):
        self._data: OrderedDict[str, tuple[bytes, float]] = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._lock = Lock()
        self._current_size = 0

    def set(self, key: str, value: Any):
        """Store a value in session."""
        import json

        value_bytes = json.dumps(value).encode()
        value_size = len(value_bytes)

        if value_size > self._max_size // 10:
            return  # Too large

        with self._lock:
            self._evict_expired()
            self._evict_if_needed(value_size)

            if key in self._data:
                old_size = len(self._data[key][0])
                self._current_size -= old_size
            else:
                self._current_size += value_size

            self._data[key] = (value_bytes, time.time())

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from session."""
        import json

        with self._lock:
            if key not in self._data:
                return default

            value_bytes, timestamp = self._data[key]

            if time.time() - timestamp > self._ttl:
                del self._data[key]
                return default

            try:
                return json.loads(value_bytes.decode())
            except json.JSONDecodeError:
                return default

    def delete(self, key: str):
        """Delete a key."""
        with self._lock:
            if key in self._data:
                value_bytes, _ = self._data.pop(key)
                self._current_size -= len(value_bytes)

    def clear(self):
        """Clear all session data."""
        with self._lock:
            self._data.clear()
            self._current_size = 0

    def _evict_expired(self):
        """Remove expired entries."""
        now = time.time()
        expired = []
        for key, (_, timestamp) in self._data.items():
            if now - timestamp > self._ttl:
                expired.append(key)

        for key in expired:
            value_bytes, _ = self._data.pop(key)
            self._current_size -= len(value_bytes)

    def _evict_if_needed(self, needed: int):
        """Evict oldest entries if we need space."""
        while self._current_size + needed > self._max_size and self._data:
            _, value_bytes = self._data.popitem(last=False)
            self._current_size -= len(value_bytes)

    def keys(self):
        """Return all keys."""
        with self._lock:
            return list(self._data.keys())


session = SessionState()