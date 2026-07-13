# Explanation — Challenge 35

## Concepts required
- Finite state machines: states, events, transitions, and why explicit beats implicit.
- Table-driven design: encoding control flow as data.
- `enum.StrEnum` (3.11+): enum members that *are* strings.
- Dynamic dispatch with `getattr` — convention-based hooks.

## Why this approach is correct
- **The transition table is the machine.** `dict[(State, Event) -> State]` makes every legal move visible in one place — reviewable at a glance, diff-able, even exportable to a diagram. Adding `review -> archived` is one line of *data*. The if/elif version the challenge bans scatters the same information across branches where gaps hide.
- **`dispatch` is generic**: look up `(state, event)`; a `KeyError` *is* the definition of an illegal transition, converted to a domain exception carrying both offenders (`from None` hides the internal KeyError). No special cases — terminal states like `PUBLISHED` need no code; they're simply absent from the table's keys.
- **Hooks via `getattr(self, f"on_enter_{new_state}")`** — the same convention `unittest` (`test_*`) and many frameworks use. The FSM core doesn't know which hooks exist; defining `on_enter_review` is all it takes to attach behavior to a transition. Hooks receive `(old_state, event)` so they can distinguish *how* the state was entered. Trade-off acknowledged: name-based discovery means a typo (`on_enter_reviw`) silently never fires — mitigate with tests or a validation pass over `dir(self)`.
- **`StrEnum`** gives type-safe members that serialize as plain strings (`f"{State.REVIEW}"` → `"review"`) — handy for logs, JSON, and the history trail, without `.value` noise everywhere.

## Alternatives and trade-offs
- `match` on `(state, event)` tuples: works, but re-encodes the table as code — you lose the ability to introspect/enumerate transitions.
- Hooks-in-table (`dict[..., tuple[State, Callable]]`): more explicit than `getattr`, better for hooks needing arguments; heavier to declare.
- The State pattern (one class per state) earns its keep when each state carries distinct data/behavior; overkill for a flat document workflow.
- Guards (conditional transitions) extend the values to `(next_state, guard_fn)` — the table shape scales.

## Python features used
- **`StrEnum`**, **dict-as-transition-table**, **`getattr` dynamic lookup**, custom exception with structured fields, tuple keys, `raise ... from None`.
