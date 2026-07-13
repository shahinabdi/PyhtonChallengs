# Challenge 24 — Study Checklist

To solve this challenge, you should understand:
- The proxy / decorator design pattern (wrap, don't modify)
- Duck typing and interface compatibility without inheritance
- TTL cache mechanics and lazy expiry
- LRU eviction with `OrderedDict` (`move_to_end`, `popitem`)
- `time.monotonic()` vs `time.time()` for expiry
- Write-through vs write-back caching and cache invalidation
- Sentinel objects for "missing" when `None` is a valid value
- The composition root — the one place substitution happens
