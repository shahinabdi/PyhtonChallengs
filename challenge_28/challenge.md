### 28 — Strategy Pattern, Pythonic Edition
```python
class PriceCalculator:
    def calc(self, order, customer_type):
        if customer_type == "regular":
            return order.total
        elif customer_type == "member":
            return order.total * 0.9
        elif customer_type == "vip":
            base = order.total * 0.8
            return base - (5 if order.total > 100 else 0)
        # new types keep getting added here...
```
**Complete:** Refactor to a strategy registry: strategies are plain functions registered via a decorator (`@pricing_strategy("vip")`), stored in a module-level dict, looked up at call time with a clear error for unknown types. Add one new strategy to prove extension requires zero edits to `PriceCalculator`.
