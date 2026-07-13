"""Challenge 13 — cached_property from scratch (non-data descriptor)."""

from collections.abc import Callable
from typing import Any


class lazy_property:
    """Like functools.cached_property: compute once, then behave like a
    plain attribute — no recomputation and no interception of writes.

    WHY THE MISSING __set__ IS THE WHOLE TRICK:
    Attribute lookup order for `obj.attr` is:
        1. DATA descriptors found on type(obj)        (have __set__/__delete__)
        2. obj.__dict__
        3. NON-DATA descriptors / class attributes    (only __get__)
    Because this class defines only __get__, it is a NON-data descriptor —
    step 3. On first access, __get__ runs, computes the value, and plants
    it in obj.__dict__ under the same name. From then on, step 2 finds the
    cached value BEFORE the lookup ever reaches the descriptor: subsequent
    accesses are plain dict lookups with zero descriptor overhead.
    (functools.cached_property uses exactly this mechanism.)
    """

    def __init__(self, fn: Callable[[Any], Any]) -> None:
        self.fn = fn
        self.attrname: str | None = None
        self.__doc__ = fn.__doc__

    def __set_name__(self, owner: type, name: str) -> None:
        self.attrname = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self  # class access: hand back the descriptor
        if self.attrname is None:
            raise TypeError("lazy_property used without __set_name__")
        value = self.fn(obj)
        # Plant the value in the instance dict under our own name; this
        # shadows the (non-data) descriptor for all future lookups.
        obj.__dict__[self.attrname] = value
        return value


class Dataset:
    def __init__(self, values: list[float]) -> None:
        self.values = values
        self.computations = 0

    @lazy_property
    def mean(self) -> float:
        """Arithmetic mean, computed at most once."""
        self.computations += 1
        return sum(self.values) / len(self.values)


if __name__ == "__main__":
    d = Dataset([1.0, 2.0, 3.0, 4.0])
    assert d.computations == 0                 # lazy: nothing computed yet
    assert d.mean == 2.5
    assert d.mean == 2.5
    assert d.computations == 1                 # computed exactly once
    assert "mean" in d.__dict__                # cache lives on the instance

    d.mean = 99.0                              # no __set__ -> plain write works
    assert d.mean == 99.0

    del d.__dict__["mean"]                     # invalidate the cache
    assert d.mean == 2.5 and d.computations == 2
    print("ok")
