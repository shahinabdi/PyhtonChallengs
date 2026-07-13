### 03 — Dict Dispatch → Structural Pattern Matching
```python
def handle_event(event: dict):
    kind = event.get("type")
    if kind == "deploy":
        if event.get("env") == "prod" and event.get("approved"):
            return f"deploying {event['service']} to prod"
        return "deploy blocked"
    elif kind == "rollback":
        return f"rolling back {event.get('service', 'unknown')}"
    elif kind == "scale":
        n = event.get("replicas")
        if isinstance(n, int) and n > 0:
            return f"scaling to {n}"
    return "ignored"
```
**Complete:** Rewrite with `match`/`case` using mapping patterns, guards, and capture patterns. Every branch above must be represented. Add a `case _` fallback.
