"""Challenge 17 — Producer/consumer with asyncio.Queue and clean shutdown."""

import asyncio


async def producer(q: asyncio.Queue[str], items: list[str]) -> None:
    for item in items:
        await q.put(item)  # backpressure: blocks when the queue is full
    # No explicit completion signal needed: shutdown is driven by
    # q.join() + cancel in main() — see the strategy comment there.


async def consumer(q: asyncio.Queue[str], results: list[str]) -> None:
    while True:
        item = await q.get()
        try:
            results.append(item.upper())  # "process" the item
        finally:
            # task_done() in finally: even if processing raises, join()
            # must not deadlock waiting for this item forever.
            q.task_done()


async def main(items: list[str], n_consumers: int = 3) -> list[str]:
    # SHUTDOWN STRATEGY: q.join() + task.cancel(), chosen over sentinels.
    #
    # * Sentinels need one sentinel PER consumer (a lone None would stop
    #   only one of them), a type that can never collide with real data,
    #   and pollute the queue's item type (str | None everywhere).
    # * join()+cancel keeps the data plane clean: producer puts only real
    #   items; q.join() waits until every item was get()-ed AND marked
    #   task_done(); then we cancel the now-idle consumers. Consumers are
    #   guaranteed to be idle at that point (all work acknowledged), so
    #   cancellation can never interrupt processing mid-item.
    # * TaskGroup treats child cancellation as normal completion, not an
    #   error, so the group exits cleanly with no hanging tasks.
    #
    # Sentinels ARE the better choice when consumers must run per-item
    # cleanup on shutdown or when cancellation is unacceptable — trade-off
    # noted.
    q: asyncio.Queue[str] = asyncio.Queue(maxsize=8)
    results: list[str] = []

    async with asyncio.TaskGroup() as tg:
        consumers = [
            tg.create_task(consumer(q, results)) for _ in range(n_consumers)
        ]
        await producer(q, items)   # feed everything (respecting maxsize)
        await q.join()             # wait until every item is processed
        for c in consumers:
            c.cancel()             # consumers are idle; stop them
    return results


if __name__ == "__main__":
    items = [f"item-{i}" for i in range(20)]
    out = asyncio.run(main(items))
    assert sorted(out) == sorted(i.upper() for i in items), out
    assert len(out) == 20
    print(f"processed {len(out)} items with 3 consumers, clean exit")
    print("ok")
