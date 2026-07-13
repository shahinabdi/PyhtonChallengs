"""Challenge 15 — Concurrent fan-out with TaskGroup + Semaphore."""

import asyncio
import time

MAX_CONCURRENCY = 5


async def fetch(url: str) -> str:
    await asyncio.sleep(0.2)  # pretend network I/O
    return f"body-of-{url}"


async def crawl(urls: list[str]) -> dict[str, str]:
    """Fetch all urls concurrently, at most MAX_CONCURRENCY in flight."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    results: dict[str, str] = {}

    async def bounded_fetch(url: str) -> None:
        async with semaphore:  # acquire/release even if fetch raises
            results[url] = await fetch(url)

    # TaskGroup: structured concurrency — the `async with` block does not
    # exit until every task is done; if any task raises, the others are
    # cancelled and the errors surface as an ExceptionGroup.
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(bounded_fetch(url))

    return results


if __name__ == "__main__":
    urls = [f"https://example.com/{i}" for i in range(12)]

    start = time.perf_counter()
    bodies = asyncio.run(crawl(urls))
    elapsed = time.perf_counter() - start

    assert bodies == {u: f"body-of-{u}" for u in urls}
    # 12 fetches of 0.2s with 5 in flight -> ceil(12/5)=3 waves ≈ 0.6s,
    # vs 2.4s sequential.
    assert 0.55 < elapsed < 1.2, elapsed
    print(f"12 urls, cap 5: {elapsed:.2f}s (sequential would be 2.4s)")
    print("ok")
