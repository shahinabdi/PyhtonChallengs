# Explanation — Challenge 17

## Concepts required
- `asyncio.Queue`: `put`/`get`, `maxsize` backpressure, `task_done()`/`join()` accounting.
- Worker-pool pattern: N identical consumers looping on one queue.
- Shutdown design: sentinels vs join-then-cancel.
- `asyncio.TaskGroup` semantics for cancelled children.

## How it works
- **Producer** just `put`s real items. `maxsize=8` provides backpressure: a fast producer parks at `await q.put(...)` until consumers catch up, bounding memory.
- **Consumers** loop forever: `get` an item, process, `task_done()`. The `finally` placement of `task_done()` matters — if processing raises, `join()` would otherwise wait forever for an acknowledgment that never comes.
- **main** wires it with a `TaskGroup`: start consumers, run the producer to completion, `await q.join()` (returns when the count of `task_done()` calls equals the count of items put), then cancel the idle consumers. The TaskGroup's `async with` exits once all children are finished; a child ending in cancellation is treated as normal completion, so nothing hangs and no exception escapes.

## The shutdown trade-off (the heart of the exercise)
| | Sentinels | `join()` + `cancel()` |
|---|---|---|
| Queue item type | polluted (`str \| None`) | clean (`str`) |
| Per-consumer bookkeeping | need exactly N sentinels | none |
| Risk of interrupting mid-item | none | none in practice — consumers are idle after `join()` (guaranteed: every item acknowledged) |
| Graceful per-consumer cleanup | natural (`break`, then cleanup) | must handle `CancelledError` |
| Works without `task_done` discipline | yes | no — one missed `task_done` deadlocks `join()` |

Chosen: **join + cancel** for a clean data plane and no sentinel-type contortions. Sentinels win when consumers hold resources needing orderly release, or in codebases where `task_done` discipline can't be trusted.

## Alternatives
- Python 3.13 adds `Queue.shutdown()`, which resolves this debate natively (`get()` raises `QueueShutDown`).
- For CPU-heavy processing, this pattern moves to `concurrent.futures` instead.

## Python features used
- **`asyncio.Queue[str]`** (generic since 3.9), **`task_done`/`join`**, **`TaskGroup`**, **`task.cancel()`**, `try/finally` discipline.
