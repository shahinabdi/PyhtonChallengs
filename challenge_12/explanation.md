# Explanation — Challenge 12

## Concepts required
- The descriptor protocol: `__get__`, `__set__`, `__set_name__`.
- Data vs non-data descriptors (having `__set__` makes this a *data* descriptor, which takes precedence over the instance `__dict__`).
- Attribute lookup order: type's data descriptors → instance `__dict__` → type's non-data descriptors.

## Why this approach is correct
- **`__set_name__(owner, name)`** is called once, automatically, when `Thermostat`'s class body finishes executing. The descriptor learns it was bound to `"celsius"` without the user repeating the name (`celsius = Bounded(-30, 60, name="celsius")` — the old, error-prone way). We derive a private storage key `_celsius` from it.
- **`__get__` with `obj is None`**: when accessed on the class itself (`Thermostat.celsius`), `obj` is `None`. Returning `self` is the convention (it's what `property` does) — it lets tools inspect the descriptor. Instance access reads from `obj.__dict__[self.private_name]`, raising a helpful `AttributeError` if never set.
- **`__set__` validates then stores per-instance.** The value lands in `obj.__dict__`, not on the descriptor — the descriptor instance is a *class-level* object shared by all `Thermostat` instances, so storing on `self` would leak values across instances. The `ValueError` message includes `self.public_name`, so `t.celsius = 100` produces "celsius must be in [-30, 60]".
- Storing under `_celsius` in the instance `__dict__` doesn't shadow the descriptor: `Bounded` is a **data descriptor** (it defines `__set__`), and data descriptors on the type always win over the instance `__dict__` for the name they're bound to (`celsius`); the private name never collides.

## Alternatives and trade-offs
- `property` per attribute: fine for one-offs, but N validated fields means N boilerplate properties. Descriptors are the reusable abstraction *behind* `property`.
- Pydantic/attrs solve this declaratively at scale; the raw descriptor teaches you their machinery.

## Python features used
- **Descriptor protocol** (`__set_name__`, `__get__`, `__set__`), **instance `__dict__` storage**, chained comparison `min <= v <= max`, `raise ... from None` to suppress context.
