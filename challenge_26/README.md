# Challenge 26 — Study Checklist

To solve this challenge, you should understand:
- Iterator protocol fundamentals (`iter`, `next`, `StopIteration`)
- `itertools.islice` and consuming from a shared iterator
- `itertools.batched` (3.12) for chunking
- `itertools.pairwise` for consecutive pairs
- `itertools.groupby` groups *consecutive* equals (not a histogram)
- `itertools.cycle` and the round-robin shrinking recipe
- Walrus operator in `while` loops
- PEP 695 generic function syntax (`def f[T](...)`)
