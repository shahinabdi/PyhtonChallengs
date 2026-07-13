# Challenge 34 — Study Checklist

To solve this challenge, you should understand:
- The mechanics of Python module import and `sys.modules`
- Why circular imports fail with half-initialized modules
- `typing.TYPE_CHECKING` guards
- `from __future__ import annotations` / string annotations (PEP 563)
- Type-only vs runtime dependencies
- Module cohesion and when to merge/extract modules
- Deferred (function-local) imports and their costs
- Re-export shims for migration
