# Challenge 11 — Study Checklist

To solve this challenge, you should understand:
- `contextlib.ExitStack` and why it exists (dynamic number of resources)
- `stack.enter_context()` vs `stack.callback()`
- `stack.pop_all()` for transferring cleanup ownership
- LIFO cleanup ordering and exception chaining during unwind
- The all-or-nothing acquisition pattern (commit / roll back)
- File object lifecycle and `typing.IO`
