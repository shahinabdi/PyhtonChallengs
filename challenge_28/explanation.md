# Explanation — Challenge 28

## Concepts required
- The Strategy pattern — and why Python needs no class hierarchy for it (functions are first-class objects).
- Decorators as *registration* devices (side-effect decorators that return the function unchanged).
- Registry dictionaries and the Open/Closed principle.

## Why this approach is correct
- **Functions are the strategies.** The GoF Strategy pattern prescribes an interface + one class per algorithm because Java-era languages lacked first-class functions. In Python a `Callable[[Order], float]` *is* the interface; a plain function is a complete implementation. The `type PricingStrategy` alias documents it.
- **The decorator registers, nothing more.** `@pricing_strategy("vip")` runs at import time, drops the function into `_STRATEGIES`, and returns it untouched — the function stays independently callable and testable. Duplicate names raise immediately at definition time, catching copy-paste errors where they happen.
- **`PriceCalculator` is closed for modification, open for extension.** It contains only lookup + a precise error (`unknown customer type 'alien'; known: employee, member, regular, vip` — listing valid options turns a debugging session into a one-glance fix). The `employee` strategy proves the point: new behavior, zero calculator edits. In a larger codebase strategies live in their own modules and registration happens on import.
- `raise ... from None` hides the internal `KeyError` — the caller's mistake is the customer type, not our dict access.

## Alternatives and trade-offs
- **`match`/dict-literal dispatch**: fine when all cases are known in one place; the registry wins when cases are contributed from multiple modules/plugins.
- **Class-based strategies** still earn their keep when strategies carry configuration/state (e.g., a discount percentage injected at construction) — then register instances or use `functools.partial`.
- **Import-time registration caveat**: a strategy module that's never imported never registers. Pair with explicit imports at the composition root, or plugin discovery (challenge 31).

## Python features used
- **First-class functions**, **parameterized decorators**, **module-level registry dict**, **PEP 695 `type` alias for callables**, **`raise ... from None`**, dataclass `Order`.
