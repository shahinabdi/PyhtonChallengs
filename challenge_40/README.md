# Challenge 40 — Study Checklist

To solve this challenge, you should understand:
- Decorators usable with and without arguments (the `fn=None` dispatch)
- Dependency graphs: topological order, DFS, three-color cycle detection
- `graphlib.TopologicalSorter` (the stdlib alternative)
- `asyncio.TaskGroup` and structured concurrency
- `asyncio.Future` as a one-shot completion signal
- Failure propagation policy: fail → skip dependents, spare unrelated branches
- `StrEnum` for status modeling
- PEP 695 `type` aliases for callables and contexts
- Why tasks need identity hashing (`dataclass(eq=False)`)
