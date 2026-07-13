### 22 — lru_cache Pitfalls
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def route_cost(graph: dict, start: str, end: str) -> float:
    ...
```
This raises `TypeError: unhashable type: 'dict'`.
**Complete:** Fix caching three ways and compare trade-offs in comments: (1) restructure so the graph is bound in a closure/class and only `(start, end)` is cached; (2) convert the graph to a hashable frozen form; (3) implement a small custom memoization decorator keyed on `id(graph)` + args — and state why (3) is dangerous.
