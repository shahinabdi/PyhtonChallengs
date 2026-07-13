"""Challenge 34 — Three fixes for a circular import, materialized and tested.

Each fix is written as real module source, dumped into its own temp
directory, imported, and exercised — proving all three actually break the
cycle rather than just claiming to.

RANKING FOR A GROWING CODEBASE (best -> last resort):
  1) TYPE_CHECKING + deferred annotations  — when the cycle is TYPE-ONLY
     (as here: each module needs the other purely for hints). Zero runtime
     coupling, zero restructuring, standard idiom every reader knows.
  2) Restructure into a shared module      — when there is REAL runtime
     mutual dependency. The cycle is a design smell: two things that need
     each other at runtime are one cohesive cluster — move them together
     (models.py) or extract the shared core. Scales best long-term, but
     costs a refactor and can grow a "dumping ground" module if abused.
  3) Deferred (in-function) import         — a targeted patch. Works, but
     hides the dependency from readers and tools, moves ImportError to
     call time, and every deferred import is a landmine for the next
     refactor. Use to firefight, then schedule fix 1 or 2.
CHOICE: for hint-only cycles (the common case) -> fix 1; the moment the
dependency is behavioral -> fix 2. Fix 3 only as a stopgap.
"""

import importlib
import sys
from pathlib import Path
from textwrap import dedent

FIXES: dict[str, dict[str, str]] = {
    # ---- Fix 1: TYPE_CHECKING guard + string/deferred annotations -------
    "fix1_type_checking": {
        "order.py": dedent("""
            from __future__ import annotations
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:                 # never executed at runtime
                from customer import Customer

            class Order:
                def __init__(self, customer: Customer, total: float) -> None:
                    self.customer = customer  # annotation is lazy -> no import needed
                    self.total = total
        """),
        "customer.py": dedent("""
            from __future__ import annotations
            from typing import TYPE_CHECKING

            if TYPE_CHECKING:
                from order import Order

            class Customer:
                def __init__(self, name: str) -> None:
                    self.name = name
                    self._orders: list[Order] = []

                def add_order(self, order: Order) -> None:
                    self._orders.append(order)

                def orders(self) -> list[Order]:
                    return list(self._orders)
        """),
    },
    # ---- Fix 2: restructure — both classes live in one cohesive module --
    "fix2_shared_module": {
        "models.py": dedent("""
            from __future__ import annotations

            class Customer:
                def __init__(self, name: str) -> None:
                    self.name = name
                    self._orders: list[Order] = []

                def add_order(self, order: Order) -> None:
                    self._orders.append(order)

                def orders(self) -> list[Order]:
                    return list(self._orders)

            class Order:
                def __init__(self, customer: Customer, total: float) -> None:
                    self.customer = customer
                    self.total = total
        """),
        # Thin re-export shims keep old import paths alive during migration:
        "order.py": "from models import Order\n",
        "customer.py": "from models import Customer\n",
    },
    # ---- Fix 3: deferred import inside the method ------------------------
    "fix3_deferred_import": {
        "order.py": dedent("""
            class Order:
                def __init__(self, customer, total: float) -> None:
                    self.customer = customer
                    self.total = total
        """),
        "customer.py": dedent("""
            class Customer:
                def __init__(self, name: str) -> None:
                    self.name = name
                    self._orders = []

                def add_order(self, order) -> None:
                    from order import Order   # deferred: runs at CALL time,
                    if not isinstance(order, Order):   # cycle already resolved
                        raise TypeError("expected an Order")
                    self._orders.append(order)

                def orders(self):
                    return list(self._orders)
        """),
    },
}


def try_fix(name: str, files: dict[str, str], base: Path) -> None:
    """Materialize one fix into its own dir, import it, exercise it."""
    fix_dir = base / name
    fix_dir.mkdir()
    for filename, source in files.items():
        (fix_dir / filename).write_text(source, encoding="utf-8")

    sys.path.insert(0, str(fix_dir))
    # Drop any modules a previous fix left behind so imports are fresh.
    for mod in ("order", "customer", "models"):
        sys.modules.pop(mod, None)
    try:
        customer_mod = importlib.import_module("customer")
        order_mod = importlib.import_module("order")

        ada = customer_mod.Customer("ada")
        order = order_mod.Order(ada, 99.5)
        ada.add_order(order)
        assert ada.orders()[0].total == 99.5
        assert order.customer.name == "ada"
        print(f"{name}: imports cleanly, round-trip works")
    finally:
        sys.path.remove(str(fix_dir))
        for mod in ("order", "customer", "models"):
            sys.modules.pop(mod, None)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        for fix_name, fix_files in FIXES.items():
            try_fix(fix_name, fix_files, Path(tmp))
    print("ok")
