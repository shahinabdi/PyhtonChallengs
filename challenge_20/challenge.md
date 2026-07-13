### 20 — Threading vs Asyncio vs Multiprocessing: Choose and Implement
```python
def cpu_task(n: int) -> int:      # pure CPU, ~0.5s each
    return sum(i * i for i in range(n))

def io_task(path: str) -> bytes:  # pure disk IO
    with open(path, "rb") as f:
        return f.read()
```
**Complete:** Write `run_all(cpu_jobs, io_jobs)` that executes 8 CPU tasks and 50 IO tasks with the *appropriate* concurrency model for each (given the GIL), combines the results, and returns them. Add a comment stating expected speedup for each half and why.
