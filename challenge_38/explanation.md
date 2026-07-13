# Explanation — Challenge 38

## Concepts required
- Metaclasses: classes are instances of their metaclass; `ServiceMeta.__new__` runs when the `class` statement executes, receiving `(name, bases, namespace)` *before* the type exists.
- Method wrapping with `functools.wraps`; regex-based case conversion.
- The escalation ladder: decorator → `__init_subclass__` → metaclass.

## How each feature is implemented
1. **Interface enforcement:** concrete classes (no `abstract=True`) must have `handle` in their own namespace or inherit one from bases — checked before the type is even built, so a violating `class` statement raises immediately. The `abstract` class keyword lets `ServiceBase` itself skip the check (note: `__init_subclass__` wouldn't run for the base class at all — a subtle metaclass difference).
2. **Timing injection:** iterate the raw `namespace` dict; every callable whose name starts with `handle` is replaced with a `_timed` wrapper *in the namespace itself*, so the finished class never exposes unwrapped methods. Only methods defined in *this* class body are wrapped — inherited ones were already wrapped when their own class was created, avoiding double-wrapping.
3. **`service_name`:** `namespace.setdefault(...)` injects the snake_case name while letting a class override it explicitly. The two-step regex handles acronym runs (`HTTPGatewayService` → `http_gateway_service`).

## The required judgment call (also in the docstring)
- Could be done otherwise: **(1)** and **(3)** via `__init_subclass__` on a base; **all three** via a class decorator (it sees the finished class and can `setattr` wrapped methods).
- What the metaclass uniquely buys:
  - **Pre-creation namespace rewriting** — the class never exists in an unwrapped state; decorators mutate after the fact.
  - **Unforgeable inheritance** — every subclass, in any module, gets the treatment automatically; a decorator can be forgotten, and `type(cls) is ServiceMeta` is a checkable guarantee (`isinstance(PaymentService, ServiceMeta)`).
  - Full control of the class object itself: intercepting `Metaclass.__call__` (instantiation), class-level dunders, `__prepare__` for ordered/validating namespaces.
- Practical rule: use the *least* powerful tool that does the job — metaclasses compose badly (two independent metaclasses on one hierarchy = `TypeError: metaclass conflict`).

## Python features used
- **`type.__new__` override**, **class keyword args through the metaclass**, **`functools.wraps`**, **`re.sub` with backreferences**, `namespace.setdefault`, `try/finally` timing.
