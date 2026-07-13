"""Challenge 18 — Running blocking code off the event loop."""

import asyncio
import hashlib
from pathlib import Path


def blocking_hash(path: str) -> str:
    """CPU+IO heavy: reads a file and hashes it. Cannot be made async."""
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


async def hash_many(paths: list[str]) -> dict[str, str]:
    # CHOICE: asyncio.to_thread (thread pool), not ProcessPoolExecutor.
    #
    # File hashing is dominated by disk reads (IO) plus hashlib crunching.
    # Threads are the right tool for BOTH halves here:
    #   * During file IO the GIL is released — threads truly overlap.
    #   * hashlib's C implementation ALSO releases the GIL while hashing
    #     buffers >2KB, so even the "CPU part" parallelizes in threads.
    #   * Threads share memory: no pickling of args/results, no process
    #     spawn cost (significant on Windows), works with any callable.
    #
    # A ProcessPoolExecutor would be the right call for PURE-Python CPU
    # work that holds the GIL (e.g. parsing, number crunching in Python
    # loops): processes sidestep the GIL entirely, at the price of pickle
    # overhead and per-process startup. For this workload it would be
    # strictly slower.
    results = await asyncio.gather(
        *(asyncio.to_thread(blocking_hash, p) for p in paths)
    )
    return dict(zip(paths, results, strict=True))


if __name__ == "__main__":
    import tempfile

    async def main() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths: list[str] = []
            for i in range(5):
                p = Path(tmp) / f"data{i}.bin"
                p.write_bytes(bytes([i]) * 1_000_000)
                paths.append(str(p))

            # Prove the loop stays responsive while hashing runs.
            heartbeat_ticks = 0

            async def heartbeat() -> None:
                nonlocal heartbeat_ticks
                while True:
                    await asyncio.sleep(0.001)
                    heartbeat_ticks += 1

            hb = asyncio.create_task(heartbeat())
            digests = await hash_many(paths)
            hb.cancel()

            assert len(digests) == 5
            assert all(len(d) == 64 for d in digests.values())
            # Deterministic check: same content -> same digest.
            assert digests[paths[0]] == hashlib.sha256(b"\x00" * 1_000_000).hexdigest()
            print(f"5 files hashed; event loop ticked {heartbeat_ticks}x meanwhile")

    asyncio.run(main())
    print("ok")
