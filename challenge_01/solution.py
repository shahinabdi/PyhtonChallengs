"""Challenge 01 — Modernize string formatting and path handling."""

from pathlib import Path


def build_report_path(base_dir: str | Path, user: str, year: int) -> Path:
    """Return the report path, ensuring its parent directory exists.

    Behavior mirrors the legacy version: the ``reports`` directory (and any
    missing parents) is created if absent, and the file itself is NOT created.
    """
    filename = f"report_{user}_{year}.txt"
    full = Path(base_dir) / "reports" / filename
    # exist_ok=True is the pathlib equivalent of the legacy
    # `if not exists: makedirs` — minus its check-then-act race condition.
    full.parent.mkdir(parents=True, exist_ok=True)
    return full


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = build_report_path(tmp, "alice", 2026)
        print(path)
        assert path.parent.is_dir()
        assert path.name == "report_alice_2026.txt"
        assert not path.exists()  # only the directory is created, not the file
        # Calling again on an existing directory must not raise.
        assert build_report_path(tmp, "alice", 2026) == path
    print("ok")
