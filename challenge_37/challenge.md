### 37 — `__init_subclass__` Registry with Validation
```python
class Serializer:
    """Subclasses must declare `format: str` and implement dumps().
    They auto-register into Serializer.registry keyed by format.
    Duplicate formats or missing attributes must fail AT CLASS
    DEFINITION TIME, not at first use."""
    registry: dict[str, type["Serializer"]] = {}
    ...  # TODO: __init_subclass__
```
**Complete:** Implement `__init_subclass__` with the validations above (raise `TypeError` with precise messages). Support `abstract=True` intermediate subclasses that skip registration.
