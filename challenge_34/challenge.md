### 34 — Circular Imports and Module Design
```python
# order.py
from customer import Customer
class Order:
    def __init__(self, customer: Customer): ...

# customer.py
from order import Order
class Customer:
    def orders(self) -> list[Order]: ...
```
**Complete:** Fix the circular import three ways and rank them: (1) `from __future__ import annotations` / string annotations + `TYPE_CHECKING`, (2) restructuring into a shared module, (3) deferred import inside the method. State in comments which you'd choose for a growing codebase and why.
