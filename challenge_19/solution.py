"""Challenge 19 — Async iterator + async context manager, two ways."""

import asyncio
from collections.abc import AsyncIterator
from types import TracebackType


class Paginator:
    """Async-iterates over pages from a fake API; also an async context
    manager that opens/closes a session."""

    def __init__(self, total_pages: int) -> None:
        self.total_pages = total_pages
        self._page = 0
        self._session_open = False

    # -- async context manager protocol ------------------------------
    async def __aenter__(self) -> "Paginator":
        await asyncio.sleep(0.01)  # pretend to open an HTTP session
        self._session_open = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self._session_open = False
        await asyncio.sleep(0.01)  # pretend to close the session
        return False  # propagate exceptions

    # -- async iterator protocol (manual form) ------------------------
    def __aiter__(self) -> "Paginator":
        # NOTE: __aiter__ is a PLAIN method returning the iterator.
        return self

    async def __anext__(self) -> dict[str, int]:
        if not self._session_open:
            raise RuntimeError("iterate inside `async with Paginator(...)`")
        if self._page >= self.total_pages:
            raise StopAsyncIteration  # the correct end-of-iteration signal
        self._page += 1
        await asyncio.sleep(0.01)  # pretend to fetch the page
        return {"page": self._page, "items": self._page * 10}

    # -- the same iteration as an async generator method --------------
    async def pages(self) -> AsyncIterator[dict[str, int]]:
        """Async-generator rewrite of __aiter__/__anext__.

        Comparison: one method instead of two, no manual cursor state
        (the loop variable IS the state, suspended at each yield), and
        StopAsyncIteration is raised for us when the function returns.
        The manual protocol wins only when the iterator needs to be an
        object with extra methods/state or resumable from outside.
        """
        if not self._session_open:
            raise RuntimeError("iterate inside `async with Paginator(...)`")
        for page in range(1, self.total_pages + 1):
            await asyncio.sleep(0.01)
            yield {"page": page, "items": page * 10}


if __name__ == "__main__":

    async def main() -> None:
        # Manual protocol.
        collected = []
        async with Paginator(3) as p:
            async for page in p:
                collected.append(page["page"])
        assert collected == [1, 2, 3]

        # StopAsyncIteration is raised at the end.
        async with Paginator(0) as p0:
            try:
                await p0.__anext__()
            except StopAsyncIteration:
                print("StopAsyncIteration raised as required")

        # Async generator form.
        async with Paginator(3) as p2:
            got = [page["page"] async for page in p2.pages()]
        assert got == [1, 2, 3]

    asyncio.run(main())
    print("ok")
