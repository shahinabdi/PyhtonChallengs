# Explanation — Challenge 30

## Concepts required
- Weak references: `weakref.ref`, and the bound-method trap solved by `weakref.WeakMethod`.
- `ExceptionGroup` and `except*` (3.11, PEP 654).
- Iteration-during-mutation hazards and the snapshot idiom.

## The three requirements

**(a) Weak handlers.** An event bus holding strong references keeps subscribers alive forever — the classic observer memory leak. `weakref.ref` fixes it for plain functions. For bound methods there's a trap worth internalizing: `obj.method` creates a *new* bound-method object on every access, so `weakref.ref(obj.method)` is dead before `subscribe` returns. `weakref.WeakMethod` stores weak refs to the instance and the function separately and reconstitutes the bound method on call — it dies exactly when the instance dies. `publish` treats a ref that returns `None` as a dead subscriber and prunes it lazily. Flip side (deliberately demonstrated): a lambda or local closure passed as a handler has no other referent and dies immediately — weak-ref buses require subscribers to own their handlers.

**(b) Error isolation with `ExceptionGroup`.** Each handler runs in its own `try`; failures are collected and all remaining handlers still execute. Raising an `ExceptionGroup` at the end loses nothing: every traceback is preserved, and callers can handle selectively with `except* ValueError:` semantics. The old alternatives — log-and-swallow (silent failures) or fail-fast (handler order determines who starves) — are both worse.

**(c) Publish-during-publish.** A handler that subscribes/unsubscribes mutates the very list being iterated — Python lists don't detect concurrent modification; you'd silently skip or double-call handlers. `list(self._subscribers[event_type])` snapshots the audience first: this publish sees a frozen set of handlers, mutations take effect next publish. Note the pruning is careful to filter the *current* list, not overwrite it with the snapshot — otherwise mid-publish subscriptions would be lost.

## Alternatives and trade-offs
- `weakref.finalize` callbacks could prune eagerly instead of lazily — more machinery, same net effect.
- Making weak-vs-strong a `subscribe(..., weak=True)` flag is the pragmatic production API (solves the lambda problem).
- Async handlers would collect awaitables and use a `TaskGroup` — whose failure mode is *also* an `ExceptionGroup`, showing the design symmetry.

## Python features used
- **`weakref.ref` / `weakref.WeakMethod`**, **`ExceptionGroup` / `except*`**, **`inspect.ismethod`**, `defaultdict(list)`, snapshot iteration.
