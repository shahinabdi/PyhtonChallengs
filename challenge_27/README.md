# Challenge 27 — Study Checklist

To solve this challenge, you should understand:
- Structural vs nominal typing
- `typing.Protocol` (PEP 544) and how conformance is checked
- `@runtime_checkable` and its isinstance limitations (names only)
- Why the conforming class needs no import of the protocol module
- Generic protocols: `class P[T](Protocol)` (PEP 695)
- Tying arguments together with a shared type parameter
- When ABCs still beat protocols (shared implementation, runtime enforcement)
