# Explanation — Challenge 27

## Concepts required
- Structural ("duck") typing vs nominal typing.
- `typing.Protocol` (PEP 544) and `@runtime_checkable`.
- Generic protocols with PEP 695 syntax (`class GenericExporter[T](Protocol)`).

## Why this approach is correct
- **The protocol states the shape**: anything with `export(self, data: dict) -> str` *is* an `Exporter` to the type checker. `save_report(exporter: Exporter, ...)` is now fully typed while accepting all three exporters.
- **The decoupling demo is the core lesson.** `MarkdownExporter` imports nothing from the protocol's module, doesn't subclass anything, isn't registered anywhere — yet it type-checks as an `Exporter` because conformance is decided by *structure*, not by ancestry. With ABC-based (nominal) typing, the third-party module would need to import your ABC and inherit from it, creating a dependency in exactly the wrong direction. Protocols let the *consumer* define what it needs; providers conform incidentally. This is the typed version of duck typing, and it's how you type plugin systems and adapter layers without circular imports.
- **`@runtime_checkable`** additionally allows `isinstance(obj, Exporter)`. Its limits matter: the check verifies only that the *method names exist* — not parameter types, not return types. It's a smoke test, not a contract check; the type checker does the real verification.
- **Generic variant:** `class GenericExporter[T](Protocol)` parameterizes the input type. `save_generic[T](exporter: GenericExporter[T], data: T)` ties the two arguments together: pass a `LinesExporter` (an exporter of `list[str]`) with a dict and the checker rejects the call.

## Alternatives and trade-offs
- **ABCs** remain right when you want to *share implementation* (template methods) or need reliable runtime enforcement — inheritance is explicit documentation.
- Protocols can't ensure implementers stay in sync when the protocol grows a method; a static-check run is the safety net (nominal ABCs fail at instantiation instead).
- Note: protocols with non-method members lose `runtime_checkable` `isinstance` precision further — attribute presence only.

## Python features used
- **`typing.Protocol`**, **`@runtime_checkable`**, **PEP 695 generic classes and functions**, `...` (Ellipsis) method stubs.
