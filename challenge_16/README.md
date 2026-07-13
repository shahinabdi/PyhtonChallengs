# Challenge 16 — Study Checklist

To solve this challenge, you should understand:
- `asyncio.timeout()` context manager (3.11+) vs `asyncio.wait_for`
- How timeouts are implemented via cancellation + conversion to `TimeoutError`
- Task cancellation: `task.cancel()`, `CancelledError`, delivery at `await` points
- The 3.8 change: `CancelledError` now subclasses `BaseException`
- Why bare `except:` is dangerous in async code
- `Exception` vs `BaseException` hierarchy design
