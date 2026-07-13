# Challenge 10 — Study Checklist

To solve this challenge, you should understand:
- The context manager protocol (`__enter__`, `__exit__`)
- `__exit__` arguments and the meaning of its return value (swallow vs propagate)
- `@contextlib.contextmanager` and single-`yield` generators
- `try/finally` semantics inside a generator-based context manager
- `time.perf_counter()` vs `time.time()` for interval measurement
- Reentrant vs reusable context managers (contextlib docs taxonomy)
