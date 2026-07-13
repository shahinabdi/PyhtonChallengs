### 04 — Enum + Exhaustive Handling
```python
STATE_PENDING = 0
STATE_RUNNING = 1
STATE_DONE = 2
STATE_FAILED = 3

def describe(state):
    if state == 0:
        return "waiting"
    # ... incomplete
```
**Complete:** Define a proper `enum.Enum` (or `StrEnum`), rewrite `describe` with `match`, and make the code fail loudly (e.g., `assert_never`-style using `typing.Never`) if a new enum member is added but not handled.
