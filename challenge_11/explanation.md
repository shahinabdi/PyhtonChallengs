# Explanation — Challenge 11

## Concepts required
- `contextlib.ExitStack`: a container of pending cleanup callbacks.
- `enter_context()` — enter a context manager and register its exit.
- `pop_all()` — transfer ownership of all pending cleanups to a new stack.
- Exception-safety patterns for acquiring N resources where N is dynamic.

## Why this approach is correct
The hand-rolled version needs a `try/except` around the loop, an inner loop to close already-open handles, careful handling of an exception *during that cleanup*, and a re-raise. `ExitStack` encodes exactly this:

1. Each `stack.enter_context(open(p))` opens a file **and** registers its closing on the stack.
2. If any later `open` raises, the `with ExitStack()` block unwinds: every registered file is closed in **LIFO order**, and even if a close itself raises, ExitStack chains/propagates correctly (same semantics as nested `with` blocks). The original exception then reaches the caller.
3. If *all* opens succeed, `stack.pop_all()` moves the registered callbacks onto a **new** ExitStack and leaves the original empty — so when the `with` block exits normally, nothing is closed. The returned handles now belong to the caller. (Discarding the returned stack is deliberate; a variant could return it so the caller can do `with returned_stack:`.)

This is the canonical `pop_all` idiom straight from the `contextlib` documentation, and it scales to any "acquire N, commit or roll back" scenario: sockets, locks, DB cursors.

## Alternatives and trade-offs
- Manual `try/except` with a cleanup loop: works, but easy to get subtly wrong (e.g., an exception while closing handle 2 leaks handles 0–1).
- Returning the `ExitStack` itself (or making `open_all` a context manager) is often the *better API* — the caller writes `with open_all(paths) as files:` and can't forget to close. The challenge's contract (return a plain list) forces explicit ownership transfer.

## Python features used
- **`contextlib.ExitStack`** (`enter_context`, `pop_all`), **list comprehension with side effects deliberately bounded by the stack**, **`typing.IO[str]`** for file-object annotations.
