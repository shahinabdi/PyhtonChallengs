"""Challenge 16 — asyncio.timeout, fallback, and cancellation safety."""

import asyncio


async def fetch(url: str, duration: float = 0.2) -> str:
    await asyncio.sleep(duration)
    return f"body-of-{url}"


async def fetch_with_fallback(primary: str, fallback: str) -> str:
    # WHY `except TimeoutError` IS SAFE FOR CANCELLATION:
    # asyncio.timeout() cancels the enclosed work when the deadline hits,
    # then converts *that internal* CancelledError into TimeoutError as it
    # leaves the `async with` block. An EXTERNAL cancellation (caller does
    # task.cancel()) is NOT converted — it stays a CancelledError, and
    # since Python 3.8 CancelledError inherits from BaseException, not
    # Exception. So `except TimeoutError` (or even `except Exception`)
    # can never swallow it, and cancellation propagates as required.
    #
    # A bare `except:` catches BaseException — it would swallow the
    # caller's CancelledError in ANY Python version, breaking task
    # cancellation. Before 3.8 the trap was wider: CancelledError still
    # inherited from Exception, so even the innocuous-looking
    # `except Exception:` would eat cancellations. The 3.8 change
    # (bpo-32528) is what makes `except Exception` safe today.
    try:
        async with asyncio.timeout(1.0):
            return await fetch(primary)
    except TimeoutError:
        return await fetch(fallback)


if __name__ == "__main__":

    async def main() -> None:
        # 1. Primary fast enough: primary wins.
        fast = await fetch_with_fallback("primary-fast", "fallback")
        assert fast == "body-of-primary-fast"

        # 2. Primary too slow: TimeoutError -> fallback body.
        async def slow_fetch_with_fallback() -> str:
            try:
                async with asyncio.timeout(0.05):
                    return await fetch("primary-slow", duration=10)
            except TimeoutError:
                return await fetch("fallback")

        assert await slow_fetch_with_fallback() == "body-of-fallback"

        # 3. External cancellation propagates.
        task = asyncio.create_task(
            fetch_with_fallback("primary", "fallback")
        )
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("cancellation propagated as designed")
        assert task.cancelled()

    asyncio.run(main())
    print("ok")
