# Explanation — Challenge 24

## Concepts required
- The proxy/decorator (wrapper) design pattern: same interface, added behavior, callers untouched.
- Cache design: TTL expiry, LRU bounding, write-through invalidation.
- `time.monotonic()` for durations; sentinel objects for "not found" when `None` is a valid value.
- Duck typing: the proxy needs no inheritance to be a drop-in.

## Why this approach is correct
- **No caller changes:** `CachedUserService` exposes exactly `get_user(user_id)` and `update_user(user_id, **fields)`. Python's duck typing means anything that *has* those methods satisfies the callers; substitution happens at the single place the service is constructed (the composition root). This is the Open/Closed principle in practice — behavior extended, no class edited.
- **TTL with `monotonic`:** wall-clock (`time.time`) can jump backwards (NTP, DST), corrupting expiry math; `monotonic` only moves forward. Entries expire *lazily* on access — no background thread needed.
- **Bounded size (LRU):** an `OrderedDict` where `move_to_end` marks recency and `popitem(last=False)` evicts the oldest gives O(1) LRU — the same structure `functools.lru_cache` uses conceptually. An unbounded cache is a slow-motion memory leak.
- **Write-through invalidation:** `update_user` forwards the write, then drops the cached entry, so the next read refetches fresh data. Invalidation (vs updating the cache in place) is chosen because the DB may transform fields (defaults, triggers, normalization) — refetching is the only honest source of truth.
- **Sentinel `_MISSING`:** `cache.get() -> None` would be ambiguous if `None` were ever a legitimate cached value; a module-private `object()` is the standard fix.

## Alternatives and trade-offs
- Subclassing `UserService` and overriding both methods also works but couples the cache to one concrete class; the proxy wraps *anything* with the right shape.
- `functools.lru_cache` on `get_user` has no TTL and no targeted invalidation — wrong tool for mutable data.
- Known limitation: other writers to the same DB bypass this in-process cache — TTL is the safety net; shared caching needs Redis/memcached.

## Python features used
- **`collections.OrderedDict`** (`move_to_end`, `popitem(last=False)`), **`time.monotonic`**, **sentinel object pattern**, duck-typed proxy composition.
