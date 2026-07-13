# Explanation — Challenge 14

## Concepts required
- How instances store attributes: `__dict__` (a real dict per instance) vs `__slots__` (fixed C-level struct offsets).
- Inheritance rules for slots: every class in the MRO must define `__slots__` (possibly empty) or instances regain a `__dict__`; child classes declare **only their new** attributes.
- Measuring memory: `sys.getsizeof` (shallow, per-object) vs `tracemalloc` (all allocations, the honest number).

## Why this approach is correct
- `Point.__slots__ = ("x", "y")` and `Point3D.__slots__ = ("z",)`: the child inherits the parent's slot descriptors, so listing `"x", "y"` again would create *duplicate* storage (wasting exactly the memory you tried to save) and shadow the parent's descriptors. One slot name, one class, once.
- **No accidental `__dict__`:** a `__dict__` sneaks back in if any base class lacks `__slots__` (here both define it), or if `"__dict__"` is listed in slots. The demo asserts `not hasattr(p, "__dict__")`.
- **Measurement:** `sys.getsizeof(instance)` on a dict-based instance undercounts badly — the attribute dict is a *separate object*, so we add `getsizeof(instance.__dict__)`. `tracemalloc` snapshots capture everything (instances + dicts + list overhead) and show the real aggregate: typically ~1.5–2× less memory for slotted instances (roughly 48–56 B vs 100+ B per small object, varying by Python version/platform), plus faster attribute access as a bonus.

## What you lose with slots
1. **Dynamic attributes** — `p.color = "red"` raises `AttributeError` (demonstrated). This is also a feature: it catches typos like `p.xx = 5`.
2. `weakref.ref(p)` fails unless `"__weakref__"` is added to `__slots__`.
3. `functools.cached_property` and this repo's challenge-13 `lazy_property` can't cache (no `__dict__` to plant values in).
4. Multiple inheritance from two slotted classes with non-empty layouts raises `TypeError`.

## Alternatives and trade-offs
- `@dataclass(slots=True)` (3.10+) generates all of this declaratively — the modern default for record types.
- If you need 1M+ homogeneous points, `array`/NumPy beats *any* object-per-point design by an order of magnitude.

## Python features used
- **`__slots__`** with inheritance, **`sys.getsizeof`**, **`tracemalloc`** snapshots and `compare_to`.
