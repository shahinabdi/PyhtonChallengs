# Challenge 05 — Study Checklist

To solve this challenge, you should understand:
- What generic classes are and why containers should be generic
- PEP 695 syntax: `class Stack[T]:` (Python 3.12+)
- The older `TypeVar` + `Generic[T]` spelling (for reading existing code)
- Annotating `self._items: list[T]`
- Optional returns: `T | None`
- `__len__` and `__iter__` protocols; `collections.abc.Iterator`
