"""Challenge 28 — Strategy pattern via a decorator-fed registry."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Order:
    total: float


type PricingStrategy = Callable[[Order], float]

_STRATEGIES: dict[str, PricingStrategy] = {}


def pricing_strategy(name: str) -> Callable[[PricingStrategy], PricingStrategy]:
    """Register a plain function as the pricing strategy for `name`."""

    def register(fn: PricingStrategy) -> PricingStrategy:
        if name in _STRATEGIES:
            raise ValueError(f"pricing strategy {name!r} already registered")
        _STRATEGIES[name] = fn
        return fn  # unchanged — the decorator only records it

    return register


class PriceCalculator:
    """Dispatch-only: knows HOW to look up strategies, never WHAT they are.
    Adding a customer type requires zero edits here (Open/Closed)."""

    def calc(self, order: Order, customer_type: str) -> float:
        try:
            strategy = _STRATEGIES[customer_type]
        except KeyError:
            known = ", ".join(sorted(_STRATEGIES)) or "<none>"
            raise ValueError(
                f"unknown customer type {customer_type!r}; known: {known}"
            ) from None
        return strategy(order)


@pricing_strategy("regular")
def regular_price(order: Order) -> float:
    return order.total


@pricing_strategy("member")
def member_price(order: Order) -> float:
    return order.total * 0.9


@pricing_strategy("vip")
def vip_price(order: Order) -> float:
    base = order.total * 0.8
    return base - (5 if order.total > 100 else 0)


# THE PROOF: a brand-new strategy — note that PriceCalculator above was
# not touched. In a real codebase this could live in another module;
# importing that module is what registers it.
@pricing_strategy("employee")
def employee_price(order: Order) -> float:
    return order.total * 0.5


if __name__ == "__main__":
    calc = PriceCalculator()
    order = Order(total=200.0)

    assert calc.calc(order, "regular") == 200.0
    assert calc.calc(order, "member") == 180.0
    assert calc.calc(order, "vip") == 155.0      # 160 - 5 (total > 100)
    assert calc.calc(Order(80.0), "vip") == 64.0  # no rebate at <=100
    assert calc.calc(order, "employee") == 100.0  # the zero-edit extension

    try:
        calc.calc(order, "alien")
    except ValueError as exc:
        print(f"clear error: {exc}")

    try:
        @pricing_strategy("vip")  # duplicate registration is a bug — fail loud
        def vip_again(order: Order) -> float:
            return 0.0
    except ValueError as exc:
        print(f"duplicate blocked: {exc}")
    print("ok")
