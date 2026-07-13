"""Challenge 09 — Parameterized retry decorator, sync and async."""

import asyncio
import functools
import inspect
import time
from collections.abc import Callable
from typing import Any


def retry(
    times: int = 3,
    delay: float = 0.5,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Retry ``fn`` up to ``times`` attempts with exponential backoff.

    Works on both plain functions and ``async def`` functions: the
    decorator inspects the target once, at decoration time, and returns
    the matching wrapper (an async wrapper must `await` the coroutine
    and use `asyncio.sleep`, or it would block the event loop).
    """
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                current_delay = delay
                for attempt in range(1, times + 1):
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions:
                        if attempt == times:
                            raise  # last attempt: re-raise the live exception
                        await asyncio.sleep(current_delay)
                        current_delay *= 2

            return async_wrapper

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(current_delay)
                    current_delay *= 2

        return wrapper

    return decorator


if __name__ == "__main__":
    calls = {"sync": 0, "async": 0}

    @retry(times=3, delay=0.01)
    def flaky() -> str:
        calls["sync"] += 1
        if calls["sync"] < 3:
            raise ConnectionError("boom")
        return "sync-ok"

    @retry(times=3, delay=0.01)
    async def flaky_async() -> str:
        calls["async"] += 1
        if calls["async"] < 2:
            raise TimeoutError("boom")
        return "async-ok"

    assert flaky() == "sync-ok" and calls["sync"] == 3
    assert asyncio.run(flaky_async()) == "async-ok" and calls["async"] == 2

    @retry(times=2, delay=0.01, exceptions=(ValueError,))
    def always_fails() -> None:
        raise ValueError("permanent")

    try:
        always_fails()
    except ValueError as exc:
        assert str(exc) == "permanent"
    print("ok")
