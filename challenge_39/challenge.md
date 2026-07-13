### 39 — Descriptor + Metaclass Combo: A Mini ORM Field System
```python
class Field:
    def __init__(self, py_type: type, primary_key: bool = False): ...
    # descriptor protocol TODO

class ModelMeta(type):
    """Collect Field attributes into cls._fields (ordered),
    validate exactly one primary key, generate __init__ that
    accepts fields as kwargs with type checking."""
    ...  # TODO

class User(metaclass=ModelMeta):
    id = Field(int, primary_key=True)
    email = Field(str)
```
**Complete:** Implement `Field` (with `__set_name__`, type-validated `__set__`) and `ModelMeta`. `User(id=1, email="a@b.c")` must work; `User(id="x", ...)` must raise `TypeError`. Also generate a `to_dict()` method.
