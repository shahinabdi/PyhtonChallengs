# Challenge 20 — Study Checklist

To solve this challenge, you should understand:
- What the GIL actually locks, and when it is released
- CPU-bound vs IO-bound workload classification
- `concurrent.futures`: executors, `submit`, `Future.result()`
- `ProcessPoolExecutor`: pickling, spawn vs fork, the `__main__` guard
- `ThreadPoolExecutor` sizing for IO workloads
- Why asyncio doesn't help with regular file IO
- Overlapping two pools concurrently (submit-all, then collect)
