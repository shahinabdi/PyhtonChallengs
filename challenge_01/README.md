# Challenge 01 — Study Checklist

To solve this challenge, you should understand:
- `pathlib.Path` basics (construction, the `/` join operator)
- f-strings vs `%`-formatting
- `Path.mkdir` with `parents=True` and `exist_ok=True` (directory creation semantics)
- Why check-then-create (`os.path.exists` + `makedirs`) is a race condition
- Type hints for functions, including `str | Path` unions
- `os.PathLike` — why returning `Path` is compatible with code expecting a path string
