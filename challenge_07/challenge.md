### 07 — Keyword-Only and Positional-Only Parameters
```python
def transfer(source, dest, amount, currency, dry_run, audit):
    ...
```
Call sites keep breaking because arguments are passed positionally in the wrong order.
**Complete:** Redesign the signature so `source`/`dest` are positional-only, `amount` may be either, and everything else is keyword-only with sensible defaults. Add type hints and a `TypedDict` or dataclass for the return value describing the transfer result.
