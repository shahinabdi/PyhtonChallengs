# Explanation — Challenge 15

## Concepts required
- `async def` / `await`, the event loop, and why `asyncio.sleep` (not `time.sleep`) stands in for network I/O.
- `asyncio.TaskGroup` (3.11+): structured concurrency.
- `asyncio.Semaphore` for concurrency capping.
- `asyncio.run` as the entry point.

## Why this approach is correct
- **Concurrency:** the sync dict comprehension runs fetches one after another — 12 × 0.2s = 2.4s. Each `tg.create_task(...)` schedules a task immediately; all of them interleave on the event loop while awaiting their sleeps.
- **TaskGroup vs bare `gather`:** `TaskGroup` guarantees the `async with` block doesn't exit until every child task finished, and if one task fails the rest are *cancelled* and the failure propagates as an `ExceptionGroup` — no orphaned tasks, no silently-swallowed errors. That's "structured concurrency": task lifetimes are bounded by a lexical scope.
- **Semaphore cap:** `asyncio.Semaphore(5)` starts with 5 permits. `async with semaphore:` acquires one before fetching and releases it afterwards — including when `fetch` raises, because `async with` is exception-safe. Net effect: at most 5 fetches are ever concurrently "in flight"; the other tasks exist but are parked waiting on the semaphore. With 12 urls the run takes ⌈12/5⌉ = 3 waves ≈ 0.6s (asserted in the demo).
- **Mapping preserved:** each task writes `results[url]` — dict writes are safe here because asyncio is single-threaded; there's no data race, only cooperative interleaving at `await` points.

## Alternatives and trade-offs
- `asyncio.gather(*coros)` + `zip(urls, bodies)` also preserves ordering and is fine pre-3.11, but has messier failure semantics (default: first exception propagates while other tasks keep running).
- Fixed worker pool + `asyncio.Queue`: better when the url stream is unbounded; a semaphore is simpler for a known finite batch.

## Python features used
- **`asyncio.TaskGroup`**, **`asyncio.Semaphore`**, **`async with`**, **`asyncio.run`**, closure task functions.
