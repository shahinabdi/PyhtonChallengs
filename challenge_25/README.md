# Challenge 25 — Study Checklist

To solve this challenge, you should understand:
- Generator functions vs generator expressions
- Pull-based pipeline composition (iterable in → iterator out)
- Why laziness bounds memory regardless of input size
- Chunking correctly: fresh list per window vs `clear()` mutation bug
- `str.split(maxsplit)` and `str.partition` for light parsing
- `itertools.batched` (3.12) as the stdlib equivalent of `window`
- `collections.deque(maxlen=n)` for the *sliding* window variant
