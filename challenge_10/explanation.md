# Explanation — Challenge 10

## Concepts required
- The context manager protocol: `__enter__` / `__exit__`, and what `__exit__`'s return value means.
- `contextlib.contextmanager`: turning a single-`yield` generator into a context manager.
- `time.perf_counter()` — the right clock for measuring elapsed intervals.
- Reentrancy of context managers (see `contextlib` docs' reentrant/reusable taxonomy).

## Why this approach is correct
**(a) Class version.** `__exit__` is *always* called when the block exits, exceptionally or not — so computing `.elapsed` there guarantees it is set even if the block raises. Returning `False` (or `None`) propagates any exception; returning `True` would swallow it, which a timer has no business doing.

**(b) Generator version.** The `@contextmanager` generator has no object for callers to hold — `with timer() as x` binds whatever the generator *yields*. So we yield a small mutable holder (`_TimerResult`) and fill in `.elapsed` in a `finally` block, which is the generator-form equivalent of `__exit__` (it runs whether the body raised or not — `contextmanager` re-raises the exception *into* the generator at the `yield` point). The caller keeps the reference and reads `.elapsed` after the block.

**(c) Reentrancy decision.** Chosen: **explicitly not reentrant**, enforced with a `RuntimeError` on double-entry. Rationale: one instance has one `.elapsed`; nesting the same instance would make the inner block clobber `_start` and produce a silently wrong outer measurement. Failing loudly beats corrupting data. A genuinely reentrant version would keep a *stack* of start times — but then `.elapsed` becomes ambiguous (whose elapsed?), which is exactly why the honest design is one instance per block. The instance *is* reusable (sequential re-use works fine) — reusable ≠ reentrant.

## Alternatives and trade-offs
- `time.monotonic()` also works; `perf_counter` has higher resolution. Never use `time.time()` — wall-clock adjustments (NTP) corrupt intervals.
- The generator could `yield lambda: time.perf_counter() - start` (a live-reading closure) — clever, but a result object is clearer.

## Python features used
- **`__enter__`/`__exit__`**, **`@contextlib.contextmanager`**, **`try/finally` in generators**, **`time.perf_counter`**, class-level annotations for documented attributes.
