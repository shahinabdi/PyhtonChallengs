"""Challenge 07 — Positional-only / keyword-only parameter design."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class TransferResult:
    source: str
    dest: str
    amount: float
    currency: str
    dry_run: bool
    executed_at: datetime
    ok: bool


def transfer(
    source: str,
    dest: str,
    /,                      # everything before is positional-only
    amount: float,          # may be passed either way
    *,                      # everything after is keyword-only
    currency: str = "USD",
    dry_run: bool = False,
    audit: bool = True,
) -> TransferResult:
    """Move ``amount`` from ``source`` to ``dest``.

    `source` / `dest` are positional-only: callers can never write
    `transfer(dest=..., source=...)` and silently swap them by keyword,
    and the parameter names are free to change without breaking callers.
    The flags are keyword-only, so `transfer("a", "b", 10, True, False)`
    — the bug factory in the original — no longer compiles.
    """
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")

    if audit:
        pass  # write to the audit log here

    return TransferResult(
        source=source,
        dest=dest,
        amount=amount,
        currency=currency,
        dry_run=dry_run,
        executed_at=datetime.now(UTC),
        ok=True,
    )


if __name__ == "__main__":
    r1 = transfer("acct-1", "acct-2", 100.0)
    r2 = transfer("acct-1", "acct-2", amount=50.0, currency="EUR", dry_run=True)
    assert r1.ok and r1.currency == "USD"
    assert r2.dry_run and r2.currency == "EUR"

    try:
        transfer(source="acct-1", dest="acct-2", amount=1.0)  # type: ignore[call-arg]
    except TypeError:
        print("positional-only enforced: keyword use rejected")

    try:
        transfer("a", "b", 10.0, "EUR")  # type: ignore[misc]
    except TypeError:
        print("keyword-only enforced: positional currency rejected")
    print("ok")
