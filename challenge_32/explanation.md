# Explanation — Challenge 32

## Concepts required
- Dependency injection (constructor injection specifically) and inversion of control.
- `typing.Protocol` for typing dependencies by capability, not by class.
- The composition root concept: one place where the object graph is assembled.
- Test doubles: hand-written fakes vs mock libraries.

## Why this approach is correct
- **The original couples construction to use.** `SignupService.__init__` building `PostgresDb("prod-dsn")` means: no tests without a prod database, no config without editing the class, hidden dependencies invisible in the signature. Constructor injection inverts it — the service *declares* what it needs (`sender: Sender, db: Database`) and does no construction.
- **Protocols type the seams.** `Sender` and `Database` describe the minimal capabilities `SignupService` uses. Because protocols are structural (challenge 27), `FakeSender`/`InMemoryDb` satisfy them without importing prod code, and `EmailSender` satisfies `Sender` without knowing the protocol exists. Notice the protocol is *narrower* than any real DB class — depend on what you use, nothing more (interface segregation).
- **`build_app(config)` is the composition root** — the single location that knows concrete types and wiring order (`SmtpClient → EmailSender → SignupService`). Config enters here, and only here. Swapping Postgres for SQLite is a one-line change in one file. Everything below the root is oblivious.
- **The test wires fakes in two lines.** No `unittest.mock.patch` (which reaches into module internals and couples tests to import paths), no DI container. Hand-written fakes also double as executable documentation of the contract, and assertions inspect real state (`sender.sent`) rather than mock call records.

## Alternatives and trade-offs
- **Default arguments** (`def __init__(self, sender: Sender | None = None)` building prod defaults) — convenient but re-hides the dependency and re-imports prod code everywhere; avoid.
- **DI frameworks** (dependency-injector, punq) add scopes/lifetimes/auto-wiring — worth it only when the graph gets big; the manual composition root scales surprisingly far and stays debuggable.
- ABCs instead of Protocols would force fakes to inherit — needless coupling for pure interfaces.

## Python features used
- **`typing.Protocol`** contracts, **keyword-only-ish explicit wiring**, plain classes as fakes, composition root function.
