### 21 — Profile First, Then Optimize
```python
def common_prefix_groups(words: list[str]) -> dict[str, list[str]]:
    groups = {}
    for w in words:
        for other in words:
            if other.startswith(w[:3]):
                groups.setdefault(w[:3], [])
                if other not in groups[w[:3]]:
                    groups[w[:3]].append(other)
    return groups
```
**Complete:** (a) Profile with `cProfile` and `timeit` on 5,000 random words and record the hot spot. (b) Rewrite to O(n) with identical output (same keys, same membership — decide whether original ordering is part of "behavior" and document your call). Target ≥100× speedup.
