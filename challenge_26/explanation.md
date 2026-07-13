# Explanation — Challenge 26

## Concepts required
- The itertools mindset: compose lazy primitives instead of writing index loops.
- Key primitives: `batched`, `islice`, `pairwise`, `groupby`, `cycle`.
- Iterator sharing: multiple consumers of the *same* iterator advance it cooperatively.

## Each function

**`chunked`** — `itertools.batched(iterable, size)` (3.12) is literally this operation; we wrap each tuple in `list` to match the example. The pre-3.12 spelling is instructive: take **one** shared `iter()`, and repeatedly `list(islice(iterator, size))` — each `islice` consumes the next `size` items because it drains the *same* underlying iterator. The walrus (`while chunk := ...`) loops until an empty chunk signals exhaustion.

**`pairwise_deltas`** — `pairwise([3,7,4])` yields `(3,7), (7,4)`; a generator expression subtracts. Zero or one input items yield nothing, which falls out naturally rather than needing a guard.

**`run_lengths`** — `groupby` groups **consecutive** equal elements (no key function needed for plain equality). `sum(1 for _ in group)` counts each group without building a list. Caveat baked into the tests: `"aba"` gives three runs — `groupby` is not a histogram (`collections.Counter` is).

**`round_robin`** — the canonical itertools recipe. `cycle(iter(it).__next__ for it in iters)` endlessly rotates over the *bound `__next__` methods* of each iterator. When one raises `StopIteration`, we shrink: `cycle(islice(nexts, active))` rebuilds the cycle from the next `active` elements of the old cycle — dropping exactly the exhausted iterator (it's the one *after* the last `active` survivors in rotation order). No indexes, no deque bookkeeping, and output order `A,1,x,B,2,y,z` matches the spec.

## Why lazy matters
All four return iterators; the demo proves `chunked` over an infinite counter works — only what's requested is computed. This is what makes these utilities compose into the pipelines of challenge 25.

## Alternatives and trade-offs
- `more_itertools` ships `chunked`, `run_length`, `interleave_longest` — production code should use it; the exercise builds the intuition.
- A `deque`-based round-robin (`popleft`/`append`) is easier to read but is manual bookkeeping — exactly what the challenge forbids.

## Python features used
- **`itertools.batched`/`islice`/`pairwise`/`groupby`/`cycle`**, **PEP 695 generic functions** (`def chunked[T](...)`), **walrus in `while`**, bound-method references (`iter(it).__next__`).
