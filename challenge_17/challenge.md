### 17 — Producer/Consumer with asyncio.Queue
```python
import asyncio

async def producer(q: asyncio.Queue, items: list[str]) -> None:
    ...  # put items, then signal completion

async def consumer(q: asyncio.Queue, results: list[str]) -> None:
    ...  # consume until told to stop; append processed items

async def main(items: list[str], n_consumers: int = 3) -> list[str]:
    ...  # wire it together; must terminate cleanly with no hanging tasks
```
**Complete:** Implement all three. Choose and justify (in a comment) a shutdown strategy: sentinel values vs `q.join()` + `task.cancel()`.
