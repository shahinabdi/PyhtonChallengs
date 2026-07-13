# Explanation — Challenge 29

## Concepts required
- The Repository pattern: persistence hidden behind a collection-like interface.
- The Unit of Work pattern: transaction boundaries as an object, here a context manager.
- ABCs (`abc.ABC`, `@abstractmethod`) for the repository contract.
- Staging: separating "pending" from "durable" state to make rollback possible.

## Why this approach is correct
- **Staged writes are the rollback mechanism.** The repo keeps two dicts: `_committed` (durable) and `_staged` (this transaction). `add` only touches `_staged`. `commit()` merges staged→committed; `rollback()` throws staged away — the committed layer is never mutated mid-transaction, so aborting is trivially safe. This mirrors how real ORMs (SQLAlchemy's session) buffer changes until flush/commit.
- **Read-your-own-writes:** `get` checks `_staged` first, so code inside a transaction sees its own pending changes — the behavior business logic expects — while other repo users would still see only committed state.
- **`UnitOfWork.__exit__` encodes the transaction rule** in one place: `exc_type is None` → commit; otherwise rollback. Returning `False` propagates the business exception — a UoW that swallowed errors would turn failures into silent data loss. The usage snippet demonstrates both paths: entity 3 is visible inside the failing transaction and gone after it.
- **The ABC keeps the domain honest:** services depend on `AbstractRepository`, so swapping `InMemoryRepository` for `PostgresRepository` is a construction-time decision (see challenge 32's composition root), and unit tests run against memory.

## Alternatives and trade-offs
- Real UoWs own *multiple* repositories plus the connection, committing all-or-nothing; this skeleton shows the seam with one.
- Copy-on-enter (snapshot the whole store, restore on failure) also enables rollback but is O(data) per transaction; staging is O(changes).
- Updates/deletes need staging too (e.g., tombstone markers) — the pattern extends naturally.
- For most apps, using the database's native transactions via SQLAlchemy is the practical answer; the pattern earns its keep by decoupling domain code from that machinery.

## Python features used
- **`abc.ABC` / `@abstractmethod`**, **context manager protocol**, dataclass entities, `dict` staging layers, `Entity | None` optional returns.
