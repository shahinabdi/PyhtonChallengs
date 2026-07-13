# Challenge 09 — Study Checklist

To solve this challenge, you should understand:
- Decorators and decorator factories (three nested functions)
- Closures — how the wrapper sees `times`/`delay`
- `functools.wraps` and why wrappers need it
- Catching a tuple of exception types; bare `raise` re-raising
- Exponential backoff
- `async def` / `await` fundamentals
- `inspect.iscoroutinefunction` for dispatch
- Why `time.sleep` must never appear inside a coroutine
