"""Challenge 25 — Lazy generator pipeline over log lines."""

from collections.abc import Iterable, Iterator
from pathlib import Path

# Log lines look like: "2026-07-08T10:00:00 ERROR service=auth msg=login failed"

type Record = dict[str, str]


def read_lines(path: str | Path) -> Iterator[str]:
    """Stage 1: stream lines from disk, one at a time."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line := line.strip():
                yield line


def parse(lines: Iterable[str]) -> Iterator[Record]:
    """Stage 2: '2026-...T10:00:00 LEVEL k=v k=v...' -> dict per line."""
    for line in lines:
        timestamp, level, rest = line.split(" ", 2)
        record: Record = {"timestamp": timestamp, "level": level}
        for pair in rest.split(" "):
            key, _, value = pair.partition("=")
            if key == "msg":
                # msg is the tail; it may itself contain spaces/equals.
                record["msg"] = rest[rest.index("msg=") + 4:]
                break
            record[key] = value
        yield record


def only_errors(records: Iterable[Record]) -> Iterator[Record]:
    """Stage 3: pass through ERROR records only."""
    return (r for r in records if r["level"] == "ERROR")


def by_service(records: Iterable[Record], service: str) -> Iterator[Record]:
    """Stage 4: pass through records for one service."""
    return (r for r in records if r.get("service") == service)


def window(records: Iterable[Record], n: int) -> Iterator[list[Record]]:
    """Stage 5: yield lists of n consecutive records; last may be short.

    Memory: only the current buffer (<= n records) is ever held; the
    upstream stages hold one record each. Yielding the buffer and
    allocating a fresh list (rather than .clear()) means consumers may
    keep windows without them being mutated behind their backs.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    buffer: list[Record] = []
    for record in records:
        buffer.append(record)
        if len(buffer) == n:
            yield buffer
            buffer = []
    if buffer:
        yield buffer


if __name__ == "__main__":
    import tempfile

    lines = []
    for i in range(20):
        level = "ERROR" if i % 3 == 0 else "INFO"
        service = "auth" if i % 2 == 0 else "billing"
        lines.append(
            f"2026-07-08T10:00:{i:02d} {level} service={service} msg=event {i}"
        )

    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "app.log"
        log.write_text("\n".join(lines), encoding="utf-8")

        # The pipeline: each stage is lazy; nothing runs until iteration.
        pipeline = window(
            by_service(only_errors(parse(read_lines(log))), "auth"),
            n=3,
        )

        windows = list(pipeline)

    # ERROR rows: i in {0,3,6,9,12,15,18}; auth rows are even i -> {0,6,12,18}
    flat = [r["timestamp"][-2:] for w in windows for r in w]
    assert flat == ["00", "06", "12", "18"], flat
    assert [len(w) for w in windows] == [3, 1]      # last window short
    assert windows[0][0]["msg"] == "event 0"
    print(f"windows: {[len(w) for w in windows]}")
    print("ok")
