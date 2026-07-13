# Explanation — Challenge 13

## Concepts required
- Non-data vs data descriptors and the attribute lookup algorithm.
- `__set_name__` for self-naming descriptors.
- How `functools.cached_property` actually works.

## Why this approach is correct
The lookup order for `obj.attr` is the key fact:

1. **Data descriptors** on the type (define `__set__` or `__delete__`) — always win.
2. **Instance `__dict__`.**
3. **Non-data descriptors** and plain class attributes.

`lazy_property` defines only `__get__`, so it sits at priority 3. First access: nothing in `obj.__dict__`, so the descriptor's `__get__` runs, computes the value via the wrapped function, and stores it in `obj.__dict__["mean"]`. Every later access finds `"mean"` at priority 2 and never consults the descriptor again — the "cache hit" is just a normal instance-attribute read, the fastest attribute path Python has.

Contrast with `property`: it defines `__set__` (even if only to raise), making it a *data* descriptor — priority 1 — so it intercepts **every** access forever. That's why a caching `property` must do its own "if cached, return cached" check on each call, while the non-data trick pays the descriptor cost exactly once.

Consequences to know:
- **Writes are allowed** (`d.mean = 99`) — no `__set__` means normal assignment; this matches the challenge spec and `functools.cached_property`.
- **Invalidation** = `del obj.__dict__["mean"]` (or `del d.mean`): removes the shadow, so the next read recomputes.
- **Requires `__dict__`**: classes using `__slots__` can't use this trick (nowhere to plant the cache) — same limitation as `functools.cached_property`.
- Thread-safety: two threads racing the first access may both compute. `functools.cached_property` originally locked (3.8) and removed the lock in 3.12 for exactly this "benign race" reason.

## Python features used
- **Descriptor protocol (`__get__` only)**, **`__set_name__`**, **instance `__dict__` shadowing**, copying `__doc__` for introspection.
