# Challenge 14 — Study Checklist

To solve this challenge, you should understand:
- How instance `__dict__` storage works and what `__slots__` replaces it with
- Slots inheritance rules: declare only new names; any slot-less base reintroduces `__dict__`
- Why `sys.getsizeof` is shallow and what `tracemalloc` measures
- Slot descriptors (slots are implemented as data descriptors)
- Features lost with slots: dynamic attributes, weakrefs, `cached_property`
- `@dataclass(slots=True)` as the modern shortcut
