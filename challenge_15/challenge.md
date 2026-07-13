### 15 — Sync → Async: HTTP-ish Fan-out
```python
import time

def fetch(url: str) -> str:
    time.sleep(0.2)          # pretend network I/O
    return f"body-of-{url}"

def crawl(urls: list[str]) -> dict[str, str]:
    return {u: fetch(u) for u in urls}
```
**Complete:** Convert to `async` using `asyncio` (`asyncio.sleep` as the stand-in). `crawl` must run all fetches concurrently with `asyncio.TaskGroup` (3.11+), preserve the url→body mapping, and cap concurrency at 5 simultaneous fetches with an `asyncio.Semaphore`.
