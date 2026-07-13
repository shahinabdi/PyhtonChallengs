### 16 — Async Timeouts and Cancellation
```python
async def fetch_with_fallback(primary: str, fallback: str) -> str:
    # TODO:
    # 1. Try fetching `primary` with a 1.0s timeout (asyncio.timeout).
    # 2. On timeout, fetch `fallback` instead (no timeout).
    # 3. If the caller cancels this coroutine, the cancellation must
    #    propagate — do NOT swallow CancelledError.
    ...
```
**Complete:** Implement the body. Then explain in a comment why `except Exception` would be safe here but a bare `except` would break cancellation in versions before 3.8 — and what changed since.
