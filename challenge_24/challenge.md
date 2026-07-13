### 24 — Slot In a Cache Layer Without Changing Callers
```python
class UserService:
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id: int) -> "User":
        return self._db.fetch("users", user_id)   # slow

    def update_user(self, user_id: int, **fields) -> None:
        self._db.update("users", user_id, fields)
```
**Complete:** Add an in-memory TTL cache (write-through invalidation on `update_user`) *without changing the public API or the callers*. Implement it as a wrapper/proxy class implementing the same interface, plus a small `TTLCache` (dict + monotonic timestamps). Bound the cache size.
