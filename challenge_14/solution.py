"""Challenge 14 — __slots__, memory measurement, and inheritance rules."""

import sys
import tracemalloc


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Point3D(Point):
    # Only the NEW attribute. Repeating "x", "y" here would waste memory
    # (duplicate slot storage) and shadow the parent's slots. And if ANY
    # class in the MRO lacks __slots__, instances get a __dict__ anyway
    # and the whole benefit silently evaporates.
    __slots__ = ("z",)

    def __init__(self, x: float, y: float, z: float) -> None:
        super().__init__(x, y)
        self.z = z


# Dict-based twins for comparison.
class PointDict:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def measure(cls: type, n: int) -> tuple[int, int]:
    """Return (per-instance getsizeof, total tracemalloc bytes for n objects)."""
    sample = cls(1.0, 2.0)
    shallow = sys.getsizeof(sample)
    if hasattr(sample, "__dict__"):
        shallow += sys.getsizeof(sample.__dict__)  # the hidden extra object

    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    objs = [cls(float(i), float(i)) for i in range(n)]
    after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    total = sum(stat.size_diff for stat in after.compare_to(before, "filename"))
    del objs
    return shallow, total


if __name__ == "__main__":
    # 1_000_000 instances as specified; pass a smaller argv[1] on tight machines.
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000

    for cls in (PointDict, Point):
        shallow, total = measure(cls, N)
        kind = "dict-based" if hasattr(cls("0", 0) if False else cls(0, 0), "__dict__") else "slotted   "
        print(f"{cls.__name__:10} ({kind}): "
              f"getsizeof≈{shallow:4d} B/instance, "
              f"tracemalloc total for {N:,} instances: {total / 2**20:8.1f} MiB")

    # Slots enforced: no accidental __dict__, no dynamic attributes.
    p = Point3D(1, 2, 3)
    assert not hasattr(p, "__dict__")
    try:
        p.color = "red"  # type: ignore[attr-defined]
    except AttributeError as exc:
        print(f"lost feature demo — dynamic attributes: {exc}")

    # FEATURE YOU LOSE (pick one, this is it): arbitrary dynamic attribute
    # assignment. Others: weakref support (unless "__weakref__" is added to
    # __slots__), functools.cached_property, and pickling quirks.
    print("ok")
