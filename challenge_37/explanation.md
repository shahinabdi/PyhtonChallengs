# Explanation — Challenge 37

## Concepts required
- `__init_subclass__`: a hook on the *base* class that runs every time a subclass is defined.
- Class-creation keyword arguments (`class X(Base, abstract=True):`).
- Fail-fast design: definition time vs first-use time.
- `ClassVar` annotation for class-level state.

## Why this approach is correct
- **Definition time is the earliest possible failure point.** `__init_subclass__` runs as part of executing the `class` statement — i.e., at *import time* of the module defining the subclass. A missing `dumps` or duplicate format therefore crashes the import with a precise `TypeError`, not a production request three weeks later. This is the challenge's core requirement and the pattern's main selling point over "check at first use".
- **`abstract=True` rides the class statement itself.** Extra keyword arguments in the bases list (`class TextSerializer(Serializer, abstract=True):`) are passed to `__init_subclass__` — no metaclass needed. Abstract intermediates skip both validation and registration, but their *concrete* children are still checked (and may inherit `format` from them, which is why validation uses `getattr` rather than `cls.__dict__`).
- **Validation details:** `dumps is Serializer.dumps` detects "inherited the base's placeholder" as missing — merely having *an* attribute named `dumps` isn't enough. The duplicate check names *both* classes in its message, turning an import error into an immediate fix.
- **`super().__init_subclass__(**kwargs)`** keeps the hook cooperative: unknown kwargs propagate up (ultimately erroring on `object` if truly unknown), and multiple bases with their own hooks compose.
- The demo uses `type(name, bases, ns)` to define bad classes inside `try` blocks — you can't write a failing `class` statement inline and catch it otherwise.

## Alternatives and trade-offs
- **A metaclass** could do the same but infects the entire hierarchy and conflicts with other metaclasses; `__init_subclass__` (PEP 487) was added precisely to make this common case metaclass-free. See challenge 38 for what *does* need a metaclass.
- **`abc.ABC`** enforces "implement this" only at *instantiation* time, and offers no registration — weaker on both counts here.
- Registry-on-the-base creates a global-ish singleton; for multi-tenant registries, key the registry per subclass tree instead.

## Python features used
- **`__init_subclass__`** (PEP 487), **class keyword arguments**, **`ClassVar`**, dynamic class creation via `type(...)` in tests, `raise ... from None`.
