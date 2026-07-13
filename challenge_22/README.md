# Challenge 22 — Study Checklist

To solve this challenge, you should understand:
- How `functools.lru_cache` constructs cache keys (hashability requirement)
- Why dicts/lists are unhashable and frozenset/tuple are not
- Closures and factory functions for binding context out of the key
- Value equality vs object identity (`==` vs `id()`)
- Object id reuse after garbage collection
- Cache invalidation and mutation hazards
- `functools.cache` vs `lru_cache(maxsize=...)`
