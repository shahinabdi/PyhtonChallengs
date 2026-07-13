"""Challenge 24 — Transparent caching proxy with a bounded TTL cache."""

import time
from collections import OrderedDict
from typing import Any

_MISSING = object()  # sentinel: None could be a legitimate cached value


class TTLCache:
    """Bounded mapping with per-entry time-to-live.

    * Expiry via time.monotonic() — immune to wall-clock adjustments.
    * Bounded: when full, evicts least-recently-used (OrderedDict order).
    """

    def __init__(self, ttl: float, maxsize: int = 1024) -> None:
        self._ttl = ttl
        self._maxsize = maxsize
        self._data: OrderedDict[Any, tuple[float, Any]] = OrderedDict()

    def get(self, key: Any) -> Any:
        """Return the cached value or the _MISSING sentinel."""
        entry = self._data.get(key)
        if entry is None:
            return _MISSING
        stored_at, value = entry
        if time.monotonic() - stored_at > self._ttl:
            del self._data[key]  # lazily expire on access
            return _MISSING
        self._data.move_to_end(key)  # mark as recently used
        return value

    def set(self, key: Any, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (time.monotonic(), value)
        while len(self._data) > self._maxsize:
            self._data.popitem(last=False)  # evict LRU

    def invalidate(self, key: Any) -> None:
        self._data.pop(key, None)


class CachedUserService:
    """Drop-in proxy: same public interface as UserService, so callers —
    and code that constructs a 'UserService-like' object — are untouched.
    Swap it in at the composition root:  service = CachedUserService(UserService(db))
    """

    def __init__(self, inner: Any, ttl: float = 30.0, maxsize: int = 1024) -> None:
        self._inner = inner
        self._cache = TTLCache(ttl=ttl, maxsize=maxsize)

    def get_user(self, user_id: int) -> Any:
        cached = self._cache.get(user_id)
        if cached is not _MISSING:
            return cached
        user = self._inner.get_user(user_id)
        self._cache.set(user_id, user)
        return user

    def update_user(self, user_id: int, **fields: Any) -> None:
        # Write-through: the write always goes to the real service;
        # the stale cache entry is invalidated so the next read refetches.
        self._inner.update_user(user_id, **fields)
        self._cache.invalidate(user_id)


# ---- demo with a fake slow DB -------------------------------------------
class FakeDb:
    def __init__(self) -> None:
        self.rows = {1: {"id": 1, "name": "ada"}, 2: {"id": 2, "name": "bob"}}
        self.fetches = 0

    def fetch(self, table: str, user_id: int) -> dict[str, Any]:
        self.fetches += 1
        return dict(self.rows[user_id])

    def update(self, table: str, user_id: int, fields: dict[str, Any]) -> None:
        self.rows[user_id].update(fields)


class UserService:
    def __init__(self, db: FakeDb) -> None:
        self._db = db

    def get_user(self, user_id: int) -> dict[str, Any]:
        return self._db.fetch("users", user_id)

    def update_user(self, user_id: int, **fields: Any) -> None:
        self._db.update("users", user_id, fields)


if __name__ == "__main__":
    db = FakeDb()
    service = CachedUserService(UserService(db), ttl=30.0, maxsize=2)

    # Caller code is identical to before — that's the whole point.
    assert service.get_user(1)["name"] == "ada"
    assert service.get_user(1)["name"] == "ada"
    assert db.fetches == 1                      # second read was a cache hit

    service.update_user(1, name="grace")        # write-through + invalidate
    assert service.get_user(1)["name"] == "grace"
    assert db.fetches == 2                      # refetched after invalidation

    # Bounded size: cap is 2; touching a third key evicts the LRU entry.
    service.get_user(2)
    db.rows[3] = {"id": 3, "name": "eve"}
    service.get_user(3)
    fetches_before = db.fetches
    service.get_user(1)                         # was evicted -> refetch
    assert db.fetches == fetches_before + 1
    print("ok")
