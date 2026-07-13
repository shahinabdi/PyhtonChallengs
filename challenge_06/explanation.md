# Explanation — Challenge 06

## Concepts required
- Generator functions (`yield`) and lazy evaluation.
- File objects as line iterators (`for line in f`) vs `readlines()`.
- The walrus operator `:=` (PEP 572) and when it *actually* helps.
- `itertools.islice` for bounded consumption of an unbounded/lazy source.
- Context managers for deterministic resource cleanup.

## Why this approach is correct
- **Never loads the whole file:** `f.readlines()` materializes every line into a list. Iterating the file object directly reads buffered chunks and yields one line at a time — memory is O(1) in file size.
- **`with` + generator interaction:** the `with` block lives *inside* the generator. When the caller stops early (as `islice` does), Python eventually calls `close()` on the generator, which throws `GeneratorExit` at the paused `yield`; the `with` block then closes the file. The original's `f.close()` was skipped entirely if an exception occurred mid-loop.
- **Walrus, used where it earns its place:** `if len(stripped := line.strip()) > min_length:` binds the stripped value *inside* the condition, so the `yield` can reuse it. Without it you'd either call `.strip()` twice or add a separate assignment line — this is exactly the "test-and-use" pattern PEP 572 was designed for.
- **Separation of concerns:** the generator knows nothing about `limit`. Truncation is the caller's business, expressed in one line with `islice`, which stops pulling after `limit` items — the rest of the file is never read.

## Alternatives and trade-offs
- A generator expression `(s for line in f if len(s := line.strip()) > 80)` works, but tying it to the file's lifetime is awkward — the named generator function with its own `with` block is more robust.
- `functools.partial` or a class-based iterator adds nothing here.

## Python features used
- **Generator functions**, **walrus operator `:=`**, **`itertools.islice`**, **file iteration protocol**, **`GeneratorExit`/cleanup semantics** (implicitly).
