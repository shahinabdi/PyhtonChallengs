# Challenge 15 — Study Checklist

To solve this challenge, you should understand:
- `async def`, `await`, and the event loop model
- `asyncio.sleep` vs `time.sleep` (blocking the loop)
- `asyncio.TaskGroup` and structured concurrency (3.11+)
- `ExceptionGroup` semantics when a TaskGroup child fails
- `asyncio.Semaphore` and `async with` for capping concurrency
- `asyncio.run` as the program entry point
- Why single-threaded asyncio has no data races on the results dict
