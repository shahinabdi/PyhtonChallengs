# Explanation — Challenge 16

## Concepts required
- `asyncio.timeout()` (3.11+) context manager and how it differs from `wait_for`.
- Cancellation mechanics: `CancelledError`, `task.cancel()`, and edge-triggered delivery at `await` points.
- The exception hierarchy change in 3.8: `CancelledError` moved from `Exception` to `BaseException`.

## Why this approach is correct
- **Timeout:** `async with asyncio.timeout(1.0):` starts a deadline. If the enclosed `await` doesn't finish in time, the timeout machinery **cancels** the inner work; when that internal `CancelledError` reaches the `async with` boundary, it is *converted* into `TimeoutError`. Catching `TimeoutError` and fetching the fallback implements the requirement directly.
- **Cancellation propagates:** if the *caller* cancels this coroutine, a `CancelledError` is raised at the current `await`. `asyncio.timeout` is careful to convert **only the cancellation it caused itself** (it checks whether its own deadline fired); an external cancellation passes through unchanged. Our `except TimeoutError` clause doesn't match `CancelledError`, so requirement 3 is satisfied with no extra code.

## The `except` question (as commented in the code)
- **Bare `except:`** catches `BaseException` — including `CancelledError` in every Python version. A task that swallows `CancelledError` becomes uncancellable: `task.cancel()` appears to succeed but the task keeps running. This also breaks `asyncio.timeout` itself (which relies on cancellation) and `TaskGroup` teardown.
- **`except Exception:`** is safe *today* because since **Python 3.8** `asyncio.CancelledError` derives from `BaseException` (like `KeyboardInterrupt` and `SystemExit`), so `Exception` doesn't match it. **Before 3.8**, `CancelledError` subclassed `Exception`, so `except Exception` silently ate cancellations — a notorious source of hung shutdowns. The class was re-parented precisely so that routine error handling can't interfere with control-flow exceptions.
- Best practice regardless: catch the *narrowest* exception that you can actually handle (`TimeoutError` here).

## Alternatives and trade-offs
- `asyncio.wait_for(fetch(primary), 1.0)`: same effect pre-3.11, but wraps a coroutine rather than a block and has historically trickier edge cases. `timeout()` is the modern API.
- Racing both fetches and taking the first success is lower latency but doubles load — a different contract.

## Python features used
- **`asyncio.timeout`**, **`TimeoutError`** (which `asyncio.TimeoutError` now aliases), **`task.cancel()` / `CancelledError`**, exception hierarchy design.
