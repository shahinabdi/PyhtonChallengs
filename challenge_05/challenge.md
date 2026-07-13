### 05 — Type Hints for a Generic Container (3.12 syntax)
```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1] if self._items else None
```
**Complete:** Make `Stack` generic using Python 3.12's `class Stack[T]:` syntax. Annotate all methods, including the `T | None` return. Add `__len__` and `__iter__` with correct annotations.
