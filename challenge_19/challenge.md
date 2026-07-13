### 19 — Async Iterator + Async Context Manager
```python
class Paginator:
    """Async-iterates over pages from a fake API, and is also an async
    context manager that "opens" and "closes" a session."""
    def __init__(self, total_pages: int):
        self.total_pages = total_pages
    # TODO: __aenter__, __aexit__, __aiter__, __anext__
```
**Complete:** Implement so this works:
```python
async with Paginator(3) as p:
    async for page in p:
        print(page)
```
`__anext__` must raise the correct exception at the end. Then rewrite the iteration part as an async generator method and compare.
