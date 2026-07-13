# Challenge 18 — Study Checklist

To solve this challenge, you should understand:
- Why blocking calls freeze the asyncio event loop
- `asyncio.to_thread` and `loop.run_in_executor`
- `ThreadPoolExecutor` vs `ProcessPoolExecutor`
- The GIL: which workloads threads can parallelize (IO, GIL-releasing C code)
- Pickling and spawn costs of process pools (especially on Windows)
- `asyncio.gather` and result ordering
- `hashlib.file_digest` for chunked file hashing
