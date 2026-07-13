### 06 — Walrus, Comprehensions, and Generator Hygiene
```python
def first_long_lines(path, limit):
    results = []
    f = open(path)
    lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 80:
            results.append(stripped)
            if len(results) == limit:
                break
    f.close()
    return results
```
**Complete:** Rewrite as a lazy generator function that never loads the whole file, uses a `with` block, and uses the walrus operator where it genuinely improves the code. Then write a one-line call site that materializes at most `limit` items using `itertools.islice`.
