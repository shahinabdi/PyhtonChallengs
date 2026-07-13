### 14 — Slots, Memory, and Inheritance
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point3D(Point):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z
```
**Complete:** Add `__slots__` to both classes correctly (no duplicated slots, no accidental `__dict__`). Then write a small script using `sys.getsizeof` + `tracemalloc` that demonstrates the memory difference for 1M instances. Note one feature you lose with slots.
