# Challenge 19 — Study Checklist

To solve this challenge, you should understand:
- Async context managers: `__aenter__`, `__aexit__`, `async with`
- Async iterators: `__aiter__` (plain method) + `__anext__` (coroutine)
- `StopAsyncIteration` vs `StopIteration`
- Async generators (`async def` with `yield`)
- Async comprehensions (`async for` inside a list comprehension)
- One-shot iterators vs fresh-generator-per-call semantics
- `contextlib.asynccontextmanager` (related tool)
