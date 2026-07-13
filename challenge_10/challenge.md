### 10 — Context Manager Two Ways
```python
class Timer:
    """Measures elapsed wall time of a block and stores it in .elapsed"""
    # TODO
```
**Complete:** (a) Implement `Timer` as a class with `__enter__`/`__exit__`, ensuring `.elapsed` is set even if the block raises. (b) Implement the same as a generator with `@contextlib.contextmanager` — decide how to expose `.elapsed` given the generator form. (c) Make the class version *reentrant-safe or explicitly not* — document your choice in a docstring.
