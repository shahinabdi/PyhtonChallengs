# Explanation — Challenge 07

## Concepts required
- Positional-only parameters (`/`, PEP 570) and keyword-only parameters (`*`, PEP 3102).
- API design: using the signature itself to make wrong calls impossible.
- Structured return values: frozen dataclass vs `TypedDict`.

## Why this approach is correct
The signature reads as three zones:

```python
def transfer(source, dest, /, amount, *, currency="USD", dry_run=False, audit=True):
```

- **`source, dest, /`** — positional-only. Two same-typed adjacent parameters are the classic swap hazard; making them positional-only means a caller must write them in order at the call site (where a reviewer can see `transfer(from_acct, to_acct, ...)`) and can never half-swap them with keywords. It also frees the implementation to rename them later.
- **`amount`** sits between `/` and `*`, so it may be passed positionally (`transfer(a, b, 10)`) or by keyword (`amount=10`) — as required.
- **`*, currency, dry_run, audit`** — keyword-only with defaults. Boolean flags passed positionally (`transfer(a, b, 10, True, False)`) are unreadable and reorder-fragile; keyword-only makes every call self-documenting and lets new options be added without breaking call sites.

## Return type: dataclass vs TypedDict
A frozen, slotted dataclass was chosen because the result is a *value produced by us*: it gets immutability (`frozen=True`), memory efficiency (`slots=True`), a good repr, and attribute access. A `TypedDict` would be preferable if the result had to be JSON-serialized directly or interoperate with dict-consuming code — it's just a `dict` at runtime with static-only guarantees.

## Python features used
- **PEP 570 `/`** and **PEP 3102 `*`** signature markers.
- **`@dataclass(frozen=True, slots=True)`** for an immutable result record.
- **`datetime.now(UTC)`** — timezone-aware timestamps (naive `utcnow()` is deprecated).
