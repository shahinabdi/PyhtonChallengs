"""Challenge 20 — The right concurrency model for each workload."""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def cpu_task(n: int) -> int:      # pure CPU, ~0.5s each
    return sum(i * i for i in range(n))


def io_task(path: str) -> bytes:  # pure disk IO
    with open(path, "rb") as f:
        return f.read()


def run_all(
    cpu_jobs: list[int], io_jobs: list[str]
) -> tuple[list[int], list[bytes]]:
    """Run CPU jobs in processes, IO jobs in threads, concurrently.

    EXPECTED SPEEDUP AND WHY:
    * CPU half -> ProcessPoolExecutor: pure-Python bytecode holds the GIL,
      so threads would serialize to ~1x. Separate processes each have
      their own interpreter+GIL: expect ~min(8, cores)x speedup (e.g. ~8x
      on an 8-core box), minus pickle/spawn overhead — jobs at ~0.5s each
      comfortably amortize it.
    * IO half -> ThreadPoolExecutor: threads BLOCKED on disk reads release
      the GIL, so 50 reads overlap. Speedup is bounded by the disk, not
      the CPU: on an SSD roughly min(n_workers, what the drive can queue),
      i.e. up to ~16x with 16 workers, far less on spinning rust where
      seeks serialize. Processes here would add pickling of every result
      buffer for zero benefit; asyncio alone wouldn't help either because
      regular file IO has no non-blocking mode — even aiofiles uses
      threads underneath.
    Both pools run simultaneously: submit is non-blocking, so the CPU and
    IO halves also overlap EACH OTHER, not just internally.
    """
    with (
        ProcessPoolExecutor() as procs,          # defaults to cpu count
        ThreadPoolExecutor(max_workers=16) as threads,
    ):
        cpu_futures = [procs.submit(cpu_task, n) for n in cpu_jobs]
        io_futures = [threads.submit(io_task, p) for p in io_jobs]
        # Gather in submission order; .result() re-raises worker errors.
        cpu_results = [f.result() for f in cpu_futures]
        io_results = [f.result() for f in io_futures]
    return cpu_results, io_results


if __name__ == "__main__":
    # The __main__ guard is MANDATORY: ProcessPoolExecutor spawns fresh
    # interpreters (always on Windows) that re-import this module.
    import tempfile
    import time
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        io_paths = []
        for i in range(50):
            p = Path(tmp) / f"blob{i}.bin"
            p.write_bytes(bytes([i]) * 200_000)
            io_paths.append(str(p))

        cpu_jobs = [2_000_000] * 8

        start = time.perf_counter()
        cpu_res, io_res = run_all(cpu_jobs, io_paths)
        elapsed = time.perf_counter() - start

        assert cpu_res == [cpu_task(2_000_000)] * 8
        assert len(io_res) == 50 and io_res[3] == bytes([3]) * 200_000

        seq_start = time.perf_counter()
        _ = [cpu_task(n) for n in cpu_jobs]
        _ = [io_task(p) for p in io_paths]
        seq_elapsed = time.perf_counter() - seq_start

        print(f"concurrent: {elapsed:.2f}s   sequential: {seq_elapsed:.2f}s "
              f"({seq_elapsed / elapsed:.1f}x)")
    print("ok")
