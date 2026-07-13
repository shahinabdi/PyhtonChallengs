# Explanation — Challenge 19

## Concepts required
- Async context manager protocol: `__aenter__` / `__aexit__` (both coroutines).
- Async iterator protocol: `__aiter__` (plain method, returns the iterator) + `__anext__` (coroutine, raises `StopAsyncIteration` when done).
- Async generators (`async def` + `yield`) as the high-level alternative.

## Why this approach is correct
- **`async with`** calls `await p.__aenter__()` on entry and `await p.__aexit__(...)` on exit — both are natural places for genuinely asynchronous setup/teardown (opening/closing an HTTP session). Returning `False` from `__aexit__` propagates exceptions, as a session wrapper should.
- **`async for`** calls `p.__aiter__()` once (note: *not* awaited — a common confusion; it must be a regular method), then `await p.__anext__()` repeatedly until it raises **`StopAsyncIteration`** — the async twin of `StopIteration` and the "correct exception" the challenge asks for. Raising anything else (or returning `None`) would either crash the loop or never end it.
- The guard on `_session_open` ties the two protocols together: pages can only be fetched inside the session's lifetime.

## Manual protocol vs async generator (the comparison)
The `pages()` method does the same job in a third of the code:
- **State**: the generator's suspended frame *is* the cursor — no `self._page` bookkeeping, no risk of a half-consumed iterator being reused accidentally (each `pages()` call returns a fresh generator; the manual version is one-shot per instance).
- **Termination**: falling off the end of the generator raises `StopAsyncIteration` automatically.
- **When manual still wins**: when the iterator must expose extra methods (e.g., `p.current_page`), participate in other protocols, or be driven step-by-step by external code (`await it.__anext__()` interleaved with other calls).

## Alternatives and trade-offs
- `contextlib.asynccontextmanager` could likewise replace `__aenter__`/`__aexit__` with one generator function — same trade-off, one level up.
- Real paginators usually take `page_size`/cursors and prefetch the next page concurrently; the structure stays identical.

## Python features used
- **`__aenter__`/`__aexit__`**, **`__aiter__`/`__anext__`**, **`StopAsyncIteration`**, **async generators**, **async comprehensions** (`[x async for x in ...]`).
