### 09 — Write a Parameterized Retry Decorator
```python
import functools, time

def retry(times: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # TODO: attempt fn up to `times` times,
            # sleeping `delay` (exponential backoff) between failures,
            # re-raising the last exception if all attempts fail.
            ...
        return wrapper
    return decorator
```
**Complete:** Implement the wrapper body. Then add a second version that also works on `async def` functions — the decorator must detect coroutine functions and dispatch accordingly.
