# Explanation — Challenge 23

## Concepts required
- String immutability and what `out = out + piece` really allocates.
- `str.join`'s two-pass strategy (measure total length → single allocation → memcpy).
- `io.StringIO` as a growable in-memory text buffer.
- CPython-specific realities: the refcount-1 in-place concat optimization, and string interning (and why it's a red herring here).

## Why each version behaves as it does
- **Naive concat**: strings are immutable, so each `+` conceptually builds a brand-new string copying all prior content — textbook O(n²). CPython quietly rescues the common `s = s + x` pattern when `s` has refcount 1 by resizing in place, so the measured gap is smaller than the theory suggests — but that's an implementation detail (PyPy lacks it; a second reference to `out` defeats it) and reallocation/copy churn remains. Never *rely* on it.
- **`"".join(fragments)`**: join walks the fragments, sums their lengths, allocates the exact final buffer **once**, then copies each fragment in. One allocation, no regrowth — this is why it wins and why it's the canonical idiom.
- **`io.StringIO`**: an amortized-growth buffer, like a text `list.append`. It loses slightly to join on per-write method-call overhead, but is the right tool when building happens incrementally across many functions or when a file-like object is needed (e.g., passing to `csv.writer`).
- **f-string template + `"".join(list-comp)`**: same allocation profile as join; the list comprehension edges out the generator because `join` materializes a generator into a list internally anyway — handing it a list skips that step. F-strings themselves are compiled to efficient bytecode (faster than `%` or `.format`).

## Which wins
`join` over a **list** comprehension (the f-string-template variant), with plain join-over-generator a whisker behind, then StringIO, then concat. Record your own numbers — the *ratios* are the durable lesson, not the milliseconds.

## Interning footnote
Interning (CPython caching identifier-like literals so `"abc" is "abc"`) affects identity comparisons and memory for repeated literals — it does **not** speed up concatenation of runtime-built strings, which are never auto-interned. Knowing what interning *doesn't* do is the point of its mention.

## Python features used
- **`str.join`**, **`io.StringIO`**, **f-strings** (including nested-quote f-strings, relaxed in 3.12 by PEP 701), **`timeit.repeat`**.
