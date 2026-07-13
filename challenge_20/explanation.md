# Explanation — Challenge 20

## Concepts required
- The GIL: only one thread executes Python bytecode at a time; it is *released* during blocking IO and inside many C routines.
- `concurrent.futures`: `ProcessPoolExecutor`, `ThreadPoolExecutor`, `Future.result()`.
- Matching workload to model — the decision table below.

## The decision table (the actual lesson)
| Workload | Right tool | Why |
|---|---|---|
| Pure-Python CPU (`cpu_task`) | **Processes** | Bytecode holds the GIL; threads serialize to ~1×. Each process has its own interpreter+GIL → ~`min(jobs, cores)`× speedup, minus pickle/spawn cost. |
| Blocking disk IO (`io_task`) | **Threads** | The GIL is released while blocked in `read()`; 50 reads overlap. Processes would add pickling of every returned buffer for nothing. |
| Blocking *network* IO at large scale | asyncio | Sockets have non-blocking modes; thousands of coroutines beat thousands of threads. Not applicable to files: regular file IO has no non-blocking mode (even `aiofiles` delegates to threads). |

## Why this implementation is correct
- Both pools are opened in one `with` statement; **all submissions happen before any `.result()` call**, so the CPU half and IO half overlap each other as well as internally. `submit` never blocks.
- Collecting `f.result()` in submission order preserves input→output correspondence and re-raises any worker exception in the parent — errors aren't silently lost.
- `ThreadPoolExecutor(max_workers=16)`: enough to keep an SSD's queue full; hundreds of threads would add scheduling overhead without more disk throughput.
- **The `if __name__ == "__main__":` guard is not optional.** `ProcessPoolExecutor` on Windows (and macOS since 3.8) uses *spawn*: child processes import the module afresh; without the guard, each child would recursively start its own pool.

## Expected speedups (as stated in the code comment)
- CPU: ~number-of-cores× (e.g. 8 jobs on 8 cores ≈ 8×).
- IO: bounded by the storage device, typically 5–16× on an SSD with 16 workers; the model overlaps *latency*, it cannot create bandwidth.

## Python features used
- **`ProcessPoolExecutor` / `ThreadPoolExecutor`**, **futures**, **parenthesized multi-context `with`** (3.10+), the **spawn** start method and `__main__` guard.
