# Explanation — Challenge 34

## Concepts required
- How circular imports actually fail: module A starts executing, hits `import B`; B's execution hits `import A` and receives the *half-initialized* A module → `ImportError`/`AttributeError`.
- `typing.TYPE_CHECKING` and `from __future__ import annotations` (PEP 563 deferred annotations).
- Module cohesion as the underlying design question.

## The three fixes

**Fix 1 — `TYPE_CHECKING` + deferred annotations.** The key observation: each module needs the other **only for type hints**. `if TYPE_CHECKING:` blocks are `False` at runtime — the import exists solely for the type checker — and `from __future__ import annotations` makes all annotations lazy strings, so `customer: Customer` never evaluates at runtime. The cycle disappears because at runtime there *is* no dependency. (Without the `__future__` import you'd quote the annotations manually: `"Customer"`.)

**Fix 2 — restructure.** A *runtime* mutual dependency signals that `Order` and `Customer` form one cohesive cluster; splitting them into two files was the actual mistake. Merging into `models.py` (or extracting a shared core both depend on) removes the cycle structurally. The thin re-export shims (`order.py` = `from models import Order`) show how to migrate without breaking existing import paths.

**Fix 3 — deferred import.** Moving `from order import Order` inside the method delays it to *call time*, when both modules are fully initialized. It works — and is also the weakest option: the dependency vanishes from the module header (where humans and tools look), failures surface at first call instead of at startup, and each deferred import quietly documents "there's a cycle here we didn't fix".

## The ranking (as required, stated in the module docstring)
1. **Fix 1** for type-only cycles — the common case in annotated codebases; idiomatic, zero structural churn.
2. **Fix 2** the moment the dependency is behavioral — it fixes the design, not the symptom; best long-term for a growing codebase (watch for `models.py` becoming a dumping ground — keep extracting cohesive clusters).
3. **Fix 3** as a stopgap only.

Note the solution *executes* all three fixes — each variant is written to disk, imported fresh, and round-tripped — because circular-import fixes are exactly the kind of thing that "looks right" and fails at import time.

## Python features used
- **`typing.TYPE_CHECKING`**, **`from __future__ import annotations`** (PEP 563), **`importlib.import_module`** + `sys.path`/`sys.modules` manipulation for isolated import tests, re-export shim modules.
