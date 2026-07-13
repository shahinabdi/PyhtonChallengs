"""Challenge 38 — A real metaclass: enforce, wrap, and inject."""

import functools
import re
import time
from collections.abc import Callable
from typing import Any


def _snake_case(name: str) -> str:
    """PaymentService -> payment_service, HTTPService -> http_service."""
    step1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step1).lower()


def _timed(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[timing] {fn.__qualname__} took {elapsed:.3f} ms")

    return wrapper


class ServiceMeta(type):
    """1) Every concrete class must define `handle(self, request)`.
       2) Every method whose name starts with `handle` gets wrapped
          to log call duration.
       3) Classes get an auto-generated `service_name` = snake_case
          of the class name.

    WHICH FEATURES ACTUALLY NEED A METACLASS?
    (1) and (3) could be done with __init_subclass__ on a base class, and
    all three with a class decorator — wrapping methods (2) too, since a
    decorator sees the finished class and can setattr replacements.
    What the metaclass uniquely buys:
      * It rewrites the NAMESPACE BEFORE the type object exists, so the
        class is never observable in its unwrapped state (decorators
        mutate after creation; __init_subclass__ can't replace the
        namespace at all — and doesn't run for the base class itself).
      * It is INESCAPABLE and INHERITED: every subclass anywhere gets the
        treatment without remembering a decorator or inheriting a
        specific base — `type(cls)` IS the guarantee.
      * Only a metaclass can change what `class` produces (isinstance of
        the class object itself, __call__ interception, etc.).
    Rule of thumb: prefer decorator < __init_subclass__ < metaclass;
    reach for the metaclass when the guarantee must be unforgeable.
    """

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        abstract = kwargs.pop("abstract", False)

        # (1) Enforce the interface on concrete classes (own or inherited).
        if not abstract:
            has_handle = "handle" in namespace or any(
                hasattr(base, "handle") for base in bases
            )
            if not has_handle:
                raise TypeError(
                    f"{name} must define handle(self, request) "
                    f"(or inherit it); mark intermediate bases abstract=True"
                )

        # (2) Wrap every handle* method defined in THIS class body.
        for attr, value in namespace.items():
            if attr.startswith("handle") and callable(value):
                namespace[attr] = _timed(value)

        # (3) Inject the derived service_name (overridable by declaring one).
        namespace.setdefault("service_name", _snake_case(name))

        return super().__new__(mcls, name, bases, namespace, **kwargs)


class ServiceBase(metaclass=ServiceMeta, abstract=True):
    """Optional convenience base so users write class X(ServiceBase)."""


class PaymentService(ServiceBase):
    def handle(self, request: dict) -> str:
        time.sleep(0.01)
        return f"charged {request['amount']}"

    def handle_refund(self, request: dict) -> str:
        return f"refunded {request['amount']}"

    def helper(self) -> str:  # not handle* -> not wrapped
        return "no timing for me"


class HTTPGatewayService(ServiceBase):
    def handle(self, request: dict) -> str:
        return "routed"


if __name__ == "__main__":
    svc = PaymentService()

    assert PaymentService.service_name == "payment_service"
    assert HTTPGatewayService.service_name == "http_gateway_service"

    assert svc.handle({"amount": 42}) == "charged 42"      # prints timing
    assert svc.handle_refund({"amount": 7}) == "refunded 7"  # prints timing
    assert svc.helper() == "no timing for me"              # silent

    try:
        class BrokenService(ServiceBase):  # no handle -> definition-time error
            pass
    except TypeError as exc:
        print(f"enforced: {exc}")

    # The metaclass guarantee: every service IS an instance of ServiceMeta.
    assert isinstance(PaymentService, ServiceMeta)
    print("ok")
