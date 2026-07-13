### 35 — Finite State Machine as a Class
```python
class Document:
    """States: draft -> review -> approved -> published
                       review -> draft (reject)
       Illegal transitions raise InvalidTransition."""
    ...  # TODO
```
**Complete:** Implement with an explicit transition table (`dict[tuple[State, Event], State]`), a `dispatch(event)` method, and per-transition hooks (`on_enter_review`, discovered via `getattr`). Use `StrEnum` for states and events. No if/elif chains.
