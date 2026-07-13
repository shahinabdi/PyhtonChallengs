"""Challenge 05 — A generic Stack using Python 3.12 type-parameter syntax."""

from collections.abc import Iterator


class Stack[T]:
    """LIFO stack, generic over its element type (PEP 695 syntax)."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item. Raises IndexError when empty."""
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        # Iterate top-of-stack first — the natural LIFO view.
        return reversed(self._items)


if __name__ == "__main__":
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    s.push(3)

    assert len(s) == 3
    assert s.peek() == 3
    assert list(s) == [3, 2, 1]
    assert s.pop() == 3

    empty: Stack[str] = Stack()
    assert empty.peek() is None
    try:
        empty.pop()
    except IndexError:
        pass
    else:
        raise AssertionError("pop on empty stack must raise")
    print("ok")
