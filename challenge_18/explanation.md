# Explanation — Challenge 18

## Concepts required
- Why calling a blocking function inside a coroutine freezes the *entire* event loop.
- `asyncio.to_thread` (3.9+) — offloading to the default thread pool.
- The GIL: when threads help (IO; C extensions that release it) and when they don't (pure-Python CPU).
- `asyncio.gather` for fan-out over awaitables.

## Why this approach is correct
- **The problem:** the event loop is single-threaded cooperative multitasking. `blocking_hash` called directly in `hash_many` would stall every other task for the full duration of each file. The demo proves the fix with a heartbeat task that keeps ticking during hashing.
- **`asyncio.to_thread(blocking_hash, p)`** wraps the call in the loop's default `ThreadPoolExecutor` and returns an awaitable; the loop stays free while worker threads block on disk reads.
- **Thread pool vs process pool (the required justification):** hashing a file is IO-dominated, and both halves of the work release the GIL — file reads by definition, and `hashlib`'s C code explicitly releases it for buffers larger than 2 KiB. So threads give real parallelism *without* pickling arguments/results or paying process startup (expensive on Windows, where processes are spawned, not forked). `ProcessPoolExecutor` is the right tool only when the bottleneck is pure-Python bytecode holding the GIL.
- `hashlib.file_digest(f, "sha256")` (3.11+) reads in chunks internally — no whole-file load.
- `gather` preserves input order, so `zip(paths, results, strict=True)` rebuilds the mapping safely.

## Alternatives and trade-offs
- `loop.run_in_executor(None, fn, arg)` is the older spelling of `to_thread` (that's literally what `to_thread` calls); use it when you need a *custom* executor — including a `ProcessPoolExecutor`.
- Unbounded fan-out is fine here (default pool caps threads at `min(32, cpu+4)`); for thousands of files add a semaphore.
- `aiofiles` makes the *read* async but not the hash — `to_thread` handles both uniformly.

## Python features used
- **`asyncio.to_thread`**, **`asyncio.gather`**, **`hashlib.file_digest`**, **`zip(..., strict=True)`**, GIL-release behavior of C extensions.
