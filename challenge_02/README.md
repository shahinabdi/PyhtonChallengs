# Challenge 02 — Study Checklist

To solve this challenge, you should understand:
- `@dataclass` basics: which dunders it generates and from what
- The mutable default argument pitfall in Python
- `field(default_factory=...)` for per-instance mutable defaults
- `field(compare=False)` to exclude fields from generated `__eq__`
- That dataclasses don't overwrite methods you define yourself (e.g. `__repr__`)
- The relationship between `__eq__` and `__hash__` (and `frozen=True`)
