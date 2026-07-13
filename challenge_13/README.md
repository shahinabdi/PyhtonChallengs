# Challenge 13 — Study Checklist

To solve this challenge, you should understand:
- The full attribute lookup order (data descriptor → instance dict → non-data descriptor)
- What makes a descriptor "data" vs "non-data"
- `__set_name__` for capturing the attribute name
- How planting a value in `obj.__dict__` shadows a non-data descriptor
- `functools.cached_property` internals and its `__slots__` limitation
- Cache invalidation via `del`
