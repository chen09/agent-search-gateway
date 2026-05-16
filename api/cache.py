from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int, enabled: bool = True) -> None:
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled and ttl_seconds > 0
        self._items: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        if not self.enabled:
            return None
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at < time.monotonic():
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if not self.enabled:
            return
        self._items[key] = (time.monotonic() + self.ttl_seconds, value)

    def stats(self) -> dict[str, Any]:
        now = time.monotonic()
        expired = [key for key, (expires_at, _) in self._items.items() if expires_at < now]
        for key in expired:
            self._items.pop(key, None)
        return {
            "enabled": self.enabled,
            "ttl_seconds": self.ttl_seconds,
            "items": len(self._items),
        }


def cache_key(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"
