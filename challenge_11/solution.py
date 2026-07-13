"""Challenge 11 — ExitStack for all-or-nothing resource acquisition."""

from contextlib import ExitStack
from pathlib import Path
from typing import IO


def open_all(paths: list[str | Path]) -> list[IO[str]]:
    """Open every file; if ANY open fails, close the ones already opened,
    then re-raise. On success return the list of file objects — the caller
    now owns them and is responsible for closing them."""
    with ExitStack() as stack:
        handles: list[IO[str]] = [
            stack.enter_context(open(p, encoding="utf-8")) for p in paths
        ]
        # All opens succeeded: detach the callbacks so the `with` block's
        # normal exit does NOT close the files. pop_all() moves them onto a
        # fresh ExitStack whose cleanup we simply never trigger — ownership
        # transfers to the caller.
        stack.pop_all()
        return handles
    # If any open(p) raised, we never reach pop_all(): the `with` block
    # unwinds and ExitStack closes every file registered so far, in LIFO
    # order, then the exception propagates.


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        good = [Path(tmp) / f"f{i}.txt" for i in range(3)]
        for p in good:
            p.write_text(f"hello from {p.name}", encoding="utf-8")

        # Success path: caller receives open handles and must close them.
        files = open_all(list(good))
        try:
            assert [f.read() for f in files] == [f"hello from f{i}.txt" for i in range(3)]
            assert all(not f.closed for f in files)
        finally:
            for f in files:
                f.close()

        # Failure path: third path doesn't exist; first two must be closed.
        bad = list(good[:2]) + [Path(tmp) / "missing.txt"]
        try:
            open_all(bad)
        except FileNotFoundError:
            print("failure path: FileNotFoundError propagated as expected")
        else:
            raise AssertionError("expected FileNotFoundError")
    print("ok")
