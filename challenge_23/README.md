# Challenge 23 — Study Checklist

To solve this challenge, you should understand:
- String immutability and the cost model of `+` concatenation
- The `"".join()` idiom and its single-allocation strategy
- CPython's refcount-1 in-place concat optimization (and why not to rely on it)
- `io.StringIO` and when a write-buffer API is preferable
- f-strings, including nested quotes (PEP 701, 3.12)
- String interning: what it is and what it does NOT affect
- Micro-benchmarking with `timeit.repeat`
