# Explanation — Challenge 03

## Concepts required
- `match`/`case` (PEP 634): mapping patterns, capture patterns, class patterns, guards, wildcard.
- Mapping patterns match on a *subset* of keys — extra keys in the dict are allowed, which is exactly the semantics of the original `event.get(...)` chain.
- Literal `True`/`False`/`None` patterns compare with `is`, not `==`.

## How each original branch maps
| Original | Pattern |
|---|---|
| deploy + prod + approved (truthy) | `{"type": "deploy", "env": "prod", "approved": approved, "service": service} if approved` |
| any other deploy | `{"type": "deploy"}` |
| rollback with service | `{"type": "rollback", "service": service}` |
| rollback without service (`get` default) | `{"type": "rollback"}` → `"rolling back unknown"` |
| scale with positive int | `{"type": "scale", "replicas": int(n)} if n > 0` |
| everything else | `case _` |

## Key details
- The **guard** `if approved` preserves the original truthiness test (`event.get("approved")` accepted `1`, `"yes"`, etc.). Using the literal pattern `True` would have tightened the behavior.
- `int(n)` is a **class pattern** with a positional capture — it performs the `isinstance(n, int)` check and binds in one step. Note `bool` is a subclass of `int`, matching the original's `isinstance` check exactly.
- One deliberate tightening: the original raised `KeyError` when a prod-approved deploy lacked `"service"`; the pattern requires the key, so that case now falls through to `"deploy blocked"`. Failing soft is usually preferable; replicate `event["service"]` inside the first branch if you need the crash.

## Alternatives and trade-offs
- A dict of handler functions (`{"deploy": handle_deploy, ...}`) scales better for many event types but can't express nested conditions declaratively.
- `if`/`elif` remains fine for two or three branches; `match` wins once structure (keys + types + guards) is part of the dispatch.

## Python features used
- **Mapping patterns**, **capture patterns**, **class patterns** (`int(n)`), **guards** (`if ...`), **wildcard** (`case _`).
