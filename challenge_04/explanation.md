# Explanation — Challenge 04

## Concepts required
- `enum.Enum`: replacing magic integer constants with a real type.
- Value patterns in `match` (dotted names like `State.PENDING` are compared with `==`, not captured).
- Exhaustiveness checking: `typing.Never`, `typing.assert_never` (3.11+), and how type checkers narrow enum types across `case` arms.

## Why this approach is correct
- Module-level integer constants (`STATE_PENDING = 0`) have no type identity: any `int` "is" a state, typos create new constants silently, and reverse lookup (0 → name) requires a manual dict. `State(0)`, `State.PENDING.name`, and `isinstance(x, State)` come for free with `Enum`.
- In `match`, `State.PENDING` is a **value pattern** (because it's a dotted name) — it compares by equality rather than binding a name. A bare `case PENDING:` would be a *capture* pattern that matches anything; this is the classic `match` trap.
- `assert_never(state)` has parameter type `Never`. After the four `case` arms, a type checker has narrowed `state` to `Never` — so the call type-checks. Add `State.PAUSED` without a case for it, and the leftover type is `Literal[State.PAUSED]`, which is not assignable to `Never`: the type checker fails the build. At runtime, `assert_never` raises `AssertionError`, so unhandled values also fail loudly without static checking.

## Alternatives and trade-offs
- `StrEnum` (3.11+) is handy when values must serialize as strings (JSON, logs); here the legacy values were ints, so plain `Enum` (or `IntEnum` for wire compatibility) fits better.
- A `dict[State, str]` lookup table is shorter but has no static exhaustiveness guarantee — a missing key is only a runtime `KeyError`.
- Before 3.11, write your own `def assert_never(x: Never) -> Never: raise AssertionError(x)` — the checker treats it identically.

## Python features used
- **`enum.Enum`**, **value patterns in `match`**, **`typing.assert_never` / `typing.Never`**, type narrowing/exhaustiveness analysis.
