# Explanation — Challenge 09

## Concepts required
- Decorator factories (a function returning a decorator returning a wrapper — three layers).
- `functools.wraps` to preserve `__name__`, `__doc__`, signature metadata.
- Exception handling: catching a *tuple* of exception types, bare `raise` to re-raise.
- Coroutine functions: `inspect.iscoroutinefunction`, why async needs its own wrapper.

## Why this approach is correct
- **Retry loop:** `for attempt in range(1, times + 1)` makes "up to `times` attempts" explicit. On success, `return` exits immediately. On failure, if it was the final attempt, bare `raise` re-raises the *current* exception with its original traceback — no need to save it in a variable. Otherwise sleep and double the delay (exponential backoff: `delay`, `2*delay`, `4*delay`, ...).
- **Async dispatch at decoration time:** `inspect.iscoroutinefunction(fn)` is checked once, when the decorator is applied — not per call. If the target is `async def`, the wrapper must itself be `async def` so that it can (a) `await fn(...)` — merely *calling* a coroutine function doesn't run it and never raises — and (b) use `await asyncio.sleep(...)`; `time.sleep` inside a coroutine would freeze the whole event loop for every other task.
- **`functools.wraps`** keeps `flaky.__name__ == "flaky"` and, importantly for async, copies `__wrapped__` markers so introspection tools still see through the wrapper.

## Alternatives and trade-offs
- Jitter (randomizing the backoff) prevents thundering herds in real systems — omitted here for determinism.
- A single wrapper that checks `inspect.isawaitable(result)` at call time can handle both, but it changes the sync function's behavior subtly and defers errors; explicit dispatch is clearer.
- Libraries like `tenacity` provide this in production; writing it once teaches you what they cost.

## Python features used
- **Closures** (the wrapper closes over `times`, `delay`, `exceptions`), **`functools.wraps`**, **`inspect.iscoroutinefunction`**, **bare `raise`**, **`asyncio.sleep` vs `time.sleep`**.
