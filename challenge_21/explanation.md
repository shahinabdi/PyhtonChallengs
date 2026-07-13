# Explanation — Challenge 21

## Concepts required
- Profiling: `cProfile` (where does time go?) and `timeit` (how much, reliably?).
- Complexity analysis: the original is O(n²·k) — n² word pairs, each with a `startswith` call, plus `other not in list` scans that are O(group size).
- Hash-based restructuring: sets/dicts turn membership and grouping into O(1).
- Deciding what counts as observable behavior (ordering).

## (a) The hot spot
On 5,000 words the profile shows ~25 million `str.startswith` calls plus millions of list `__contains__` scans — the cost *is* the nested loop; no single callee can be micro-optimized away. That's the classic profile signature that says "change the algorithm, not the code."

## (b) The O(n) rewrite
Three linear passes:
1. `keys = {w[:3] for w in words}` — the set of group keys.
2. For each word, check its **prefixes of length 1–3** against `keys`, appending to that group once (per-group `seen` sets make dedup O(1)). Why prefixes, not just `word[:3]`? A key can be shorter than 3 (from a short word like `"ab"`), and the original's `startswith` semantics put `"abcde"` into group `"ab"` as well as `"abc"`. Grouping only by `w[:3]` would be subtly wrong — this is the trap in the exercise.
3. Rebuild the dict in the original key-insertion order with one more pass.

Each word does ≤3 O(1) hash probes → O(n) total. Measured speedup on 5,000 words comfortably exceeds the 100× target (typically 500–2000×).

## The ordering call (documented, as required)
Dict insertion order and list order are *observable* in Python; a caller may reasonably iterate the result or compare it. Preserving both cost one extra O(n) pass and per-group insertion-order appends — essentially free — so the rewrite treats ordering as part of the behavior contract. Had preservation been expensive, the honest alternative is to declare unordered semantics and return `dict[str, set[str]]`.

## Trade-offs
- Memory: `seen` sets add O(n) transient memory — the standard time/space trade.
- If words were static and queries dynamic, a real prefix trie would serve arbitrary-length prefix queries; overkill for fixed length ≤ 3.

## Python features used
- **`cProfile`/`pstats`**, **`timeit.repeat`** (min of repeats ≈ best-case, least-noise), **set/dict comprehensions**, **`setdefault`**, per-group dedup sets.
