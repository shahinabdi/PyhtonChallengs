### 18 — Bridging Sync and Async Worlds
```python
def blocking_hash(path: str) -> str:
    """CPU+IO heavy: reads a file and hashes it. Cannot be made async."""
    ...

async def hash_many(paths: list[str]) -> dict[str, str]:
    # TODO: run blocking_hash for all paths WITHOUT blocking the event loop.
    ...
```
**Complete:** Implement using `asyncio.to_thread` (or `loop.run_in_executor` with a `ProcessPoolExecutor` — pick one and justify the choice for CPU-bound vs IO-bound work in a comment).
