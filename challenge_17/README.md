# Challenge 17 — Study Checklist

To solve this challenge, you should understand:
- `asyncio.Queue`: `put`, `get`, `maxsize` and backpressure
- `task_done()` / `join()` accounting and its deadlock pitfall
- The producer/consumer (worker pool) pattern
- Shutdown strategies: sentinel values vs `join()` + `cancel()`
- How `TaskGroup` treats cancelled child tasks
- `CancelledError` and where cancellation is delivered
- (Awareness) `Queue.shutdown()` in Python 3.13
