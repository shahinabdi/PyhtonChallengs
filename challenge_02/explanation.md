# Explanation — Challenge 02

## Concepts required
- `@dataclass` code generation: `__init__`, `__repr__`, `__eq__`.
- The mutable default argument pitfall and `field(default_factory=...)`.
- Per-field options: `compare=False` to exclude a field from `__eq__` (and ordering).
- The rule that dataclass-generated dunders never overwrite ones you define in the class body.

## Why this approach is correct
- `tags: list[str] = field(default_factory=list)` gives each instance its own list. Writing `tags: list[str] = []` is rejected by dataclasses at class-definition time precisely because it would be shared state.
- Equality on `(host, port)` only: the generated `__eq__` compares a tuple of all fields *with* `compare=True`. Marking `tags` and `healthy` as `compare=False` shrinks that tuple to `(host, port)`.
- The custom `__repr__` in the class body is kept because dataclasses only add methods that are not already defined — so the original's compact repr survives.

## Subtle behavioral difference worth knowing
The generated `__eq__` first checks `other.__class__ is self.__class__` and returns `NotImplemented` otherwise. The original blindly accessed `other.host`, so comparing against a non-`Server` raised `AttributeError`. The dataclass version is strictly better behaved; document it if "exact" behavior matters.

## Alternatives and trade-offs
- `@dataclass(eq=False)` + hand-written `__eq__`: works, but you lose the declarative style and must also consider `__hash__`.
- If instances should be dict keys, add `frozen=True` (or `eq=True, frozen=True`) to get a consistent `__hash__` based on the compared fields.

## Python features used
- **`dataclasses.dataclass`** and **`dataclasses.field`** with `default_factory` and `compare`.
- **Class-level type annotations** — how dataclasses discover fields.
