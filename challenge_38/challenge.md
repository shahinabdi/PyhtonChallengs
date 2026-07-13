### 38 — A Real Metaclass: Enforce Interface + Inject Behavior
```python
class ServiceMeta(type):
    """1) Every concrete class must define `handle(self, request)`.
       2) Every method whose name starts with `handle` gets wrapped
          to log call duration.
       3) Classes get an auto-generated `service_name` = snake_case
          of the class name."""
    ...  # TODO: __new__

class PaymentService(metaclass=ServiceMeta):
    def handle(self, request): ...
```
**Complete:** Implement `ServiceMeta.__new__`. Then add a short comment: which of these three features could have been done with `__init_subclass__` or a decorator instead, and what does the metaclass uniquely buy you?
