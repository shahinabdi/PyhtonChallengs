"""Challenge 10 — A Timer context manager, class-based and generator-based."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType


class Timer:
    """Measure elapsed wall time of a block; result lands in ``.elapsed``.

    Reentrancy: this class is **explicitly NOT reentrant**. A single Timer
    instance owns a single ``.elapsed`` slot, so nesting the same instance
    would silently overwrite the outer measurement. Entering an already-
    entered Timer therefore raises RuntimeError. Use one instance per
    block (they're cheap) if you need nesting.
    """

    elapsed: float | None

    def __init__(self) -> None:
        self.elapsed = None
        self._start: float | None = None

    def __enter__(self) -> "Timer":
        if self._start is not None:
            raise RuntimeError("Timer is not reentrant; use a new instance")
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        # Runs whether the block raised or not, so .elapsed is always set.
        assert self._start is not None
        self.elapsed = time.perf_counter() - self._start
        self._start = None
        return False  # never swallow exceptions


class _TimerResult:
    """Mutable holder the generator form yields; filled in on exit."""

    elapsed: float | None = None


@contextmanager
def timer() -> Iterator[_TimerResult]:
    """Generator form. A generator can't hand out an attribute on itself,
    so we yield a small result object and mutate it in `finally` — the
    caller keeps a reference and reads `.elapsed` after the block."""
    result = _TimerResult()
    start = time.perf_counter()
    try:
        yield result
    finally:
        # `finally` plays the role of __exit__: runs on success AND on raise.
        result.elapsed = time.perf_counter() - start


if __name__ == "__main__":
    with Timer() as t:
        time.sleep(0.05)
    assert t.elapsed is not None and t.elapsed >= 0.05

    # .elapsed is set even when the block raises.
    t2 = Timer()
    try:
        with t2:
            time.sleep(0.01)
            raise ValueError("boom")
    except ValueError:
        pass
    assert t2.elapsed is not None and t2.elapsed >= 0.01

    # Non-reentrancy is enforced, not silent.
    t3 = Timer()
    with t3:
        try:
            with t3:
                pass
        except RuntimeError as exc:
            print(f"reentry blocked: {exc}")

    with timer() as r:
        time.sleep(0.02)
    assert r.elapsed is not None and r.elapsed >= 0.02
    print("ok")
