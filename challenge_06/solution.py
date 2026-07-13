"""Challenge 06 — Lazy generator with `with`, walrus, and islice."""

from collections.abc import Iterator
from itertools import islice
from pathlib import Path


def long_lines(path: str | Path, min_length: int = 80) -> Iterator[str]:
    """Yield stripped lines longer than ``min_length``, lazily.

    The file object is itself a lazy line iterator, so at no point is more
    than one line in memory. The `with` block guarantees the file is closed
    when the generator is exhausted, garbage-collected, or `.close()`d.
    """
    with open(path, encoding="utf-8") as f:
        for line in f:
            # Walrus: bind and test in one expression — avoids computing
            # `line.strip()` twice or spending a statement on a temp name.
            if len(stripped := line.strip()) > min_length:
                yield stripped


def first_long_lines(path: str | Path, limit: int) -> list[str]:
    # The one-line call site: islice stops pulling from the generator after
    # `limit` items, so the rest of the file is never even read.
    return list(islice(long_lines(path), limit))


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "sample.txt"
        sample.write_text(
            "short\n"
            + ("x" * 100 + "\n") * 3
            + "also short\n"
            + "y" * 90 + "\n",
            encoding="utf-8",
        )
        assert first_long_lines(sample, 2) == ["x" * 100, "x" * 100]
        assert first_long_lines(sample, 10) == ["x" * 100] * 3 + ["y" * 90]
    print("ok")
