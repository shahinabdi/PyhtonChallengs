# Challenge 08 — Study Checklist

To solve this challenge, you should understand:
- `TypedDict` basics and `total=True/False`
- `Required[...]` and `NotRequired[...]` (PEP 655)
- `Unpack[TD]` on `**kwargs` (PEP 692)
- That TypedDicts are plain dicts at runtime — no validation happens
- `dict.get(key, default)` for optional keys
- When explicit keyword-only parameters beat typed `**kwargs` (and the forwarding case where they don't)
