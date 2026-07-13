# Explanation — Challenge 05

## Concepts required
- Generics: why a container should carry its element type in the type system.
- PEP 695 (Python 3.12): `class Stack[T]:` declares a type parameter inline — no more `TypeVar("T")` + `Generic[T]` boilerplate.
- Protocol methods `__len__` and `__iter__` and their expected signatures.

## Why this approach is correct
- `class Stack[T]:` introduces `T` scoped to the class. Every mention of `T` in the body (`push(item: T)`, `pop() -> T`) refers to the same parameter, so `Stack[int]().push("x")` is a static type error.
- `self._items: list[T] = []` ties the internal storage to the same parameter — without this annotation the list would be `list[Any]` and the guarantees evaporate.
- `peek() -> T | None`: the union return is required because an empty stack yields `None`. Callers are forced by the type checker to handle the `None` case.
- `__len__(self) -> int` makes `Stack` satisfy `Sized`; `__iter__(self) -> Iterator[T]` makes it `Iterable[T]`, so `list(s)`, `for x in s`, and `len(s)` all type-check. Returning `reversed(self._items)` iterates in LIFO order, which matches what "iterating a stack" usually means (document either choice).

## Alternatives and trade-offs
- Pre-3.12 spelling: `T = TypeVar("T")` + `class Stack(Generic[T])`. Same runtime behavior, more boilerplate, and `T` leaks into module scope.
- `peek()` raising instead of returning `None` gives a `-> T` return with no union — cleaner for callers who consider empty-peek a bug. The challenge mandates `T | None`.
- Inheriting from `collections.deque` would give push/pop for free but exposes the whole deque API — composition keeps the interface minimal.

## Python features used
- **PEP 695 type parameter syntax** (`class Stack[T]:`), **`T | None` unions**, **`collections.abc.Iterator`** annotations, **`reversed()`** returning a lazy iterator.
