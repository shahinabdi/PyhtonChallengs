# Explanation — Challenge 25

## Concepts required
- Generator functions and generator expressions as *stages*.
- Pipeline composition: each stage takes an iterable, returns an iterator — so stages snap together like Unix pipes.
- Pull-based laziness: nothing executes until the final consumer iterates.
- Chunking with bounded memory.

## Why this approach is correct
- **Each stage is lazy.** `read_lines` streams the file (never `readlines()`); `parse` transforms one line at a time; `only_errors` / `by_service` are generator expressions — one-liner filters. Composing them creates a chain of suspended frames; when the consumer asks for one window, the request *pulls* records up through the chain one at a time. Peak memory is O(n) for the window buffer plus one record per stage, regardless of file size — a 100 GB log works.
- **Uniform interface** (`Iterable[Record] -> Iterator[Record]`) is what makes stages freely reorderable and testable in isolation: each can be unit-tested by feeding it a plain list.
- **`window`** buffers up to `n` records, yields the full list, then starts a *fresh* list. Reassigning (rather than `buffer.clear()`) matters: the consumer may hold on to yielded windows, and clearing would mutate them retroactively — a classic chunking bug. The trailing `if buffer:` emits the short final window.
- **Parsing detail:** `str.partition("=")` splits key/value safely, and `msg=` is treated as "rest of line" since messages contain spaces — a realistic log-parsing wrinkle.

## Alternatives and trade-offs
- `itertools.batched(records, n)` (3.12) implements `window`'s exact semantics (returning tuples) — knowing you just reimplemented a stdlib tool is part of the lesson; hand-rolling shows *why* it's O(n) memory.
- If "window" meant *sliding* windows, `collections.deque(maxlen=n)` would be the tool instead.
- Push-based alternatives (callbacks, RxPy) invert control; generator pipelines keep plain `for`-loop ergonomics.

## Python features used
- **Generator functions**, **generator expressions**, **`str.partition`**, **walrus in a filter** (`if line := line.strip()`), **PEP 695 `type` alias**, composition-by-nesting call syntax.
