### 13 — Cached Property from Scratch
```python
class lazy_property:
    """Like functools.cached_property: compute once, then behave
    like a plain attribute (no recomputation, no __set__)."""
    def __init__(self, fn):
        ...
    # TODO
```
**Complete:** Implement using the non-data-descriptor trick (only `__get__`, plus `__set_name__`). Explain in a comment *why* the absence of `__set__` makes subsequent accesses skip the descriptor.
