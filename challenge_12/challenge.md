### 12 — A Descriptor for Validated Fields
```python
class Bounded:
    """Descriptor enforcing min <= value <= max on instances."""
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __set_name__(self, owner, name):
        ...  # TODO: store the attribute name

    def __get__(self, obj, objtype=None):
        ...  # TODO: instance lookup; return self when accessed on the class

    def __set__(self, obj, value):
        ...  # TODO: validate and store per-instance (no shared state!)

class Thermostat:
    celsius = Bounded(-30, 60)
```
**Complete:** Implement the three methods. Store values in the instance `__dict__` under a private name. Raise `ValueError` with a message that includes the attribute name.
