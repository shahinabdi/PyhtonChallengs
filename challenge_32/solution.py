"""Challenge 32 — Constructor injection with Protocols, no framework."""

from typing import Any, Protocol


# ---- the contracts (what SignupService actually needs) -------------------
class Sender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class Database(Protocol):
    def insert(self, table: str, row: dict[str, Any]) -> None: ...

    def exists(self, table: str, key: str, value: Any) -> bool: ...


# ---- the service: depends on protocols, constructs NOTHING ---------------
class SignupService:
    def __init__(self, sender: Sender, db: Database) -> None:
        self._sender = sender
        self._db = db

    def signup(self, email: str) -> bool:
        if self._db.exists("users", "email", email):
            return False
        self._db.insert("users", {"email": email})
        self._sender.send(email, "Welcome!", "Thanks for signing up.")
        return True


# ---- prod implementations (would live in adapters/) ----------------------
class SmtpClient:
    def __init__(self, host: str) -> None:
        self.host = host

    def send_message(self, to: str, subject: str, body: str) -> None:
        print(f"[smtp {self.host}] -> {to}: {subject}")


class EmailSender:
    def __init__(self, smtp: SmtpClient) -> None:  # injected, not built
        self._smtp = smtp

    def send(self, to: str, subject: str, body: str) -> None:
        self._smtp.send_message(to, subject, body)


class PostgresDb:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._rows: dict[str, list[dict[str, Any]]] = {}  # stand-in

    def insert(self, table: str, row: dict[str, Any]) -> None:
        self._rows.setdefault(table, []).append(row)

    def exists(self, table: str, key: str, value: Any) -> bool:
        return any(r.get(key) == value for r in self._rows.get(table, []))


# ---- composition root: the ONE place that knows concrete types -----------
def build_app(config: dict[str, str]) -> SignupService:
    smtp = SmtpClient(host=config["smtp_host"])
    sender = EmailSender(smtp)
    db = PostgresDb(config["db_dsn"])
    return SignupService(sender=sender, db=db)


# ---- test fakes: satisfy the Protocols by shape, import no prod code ------
class FakeSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append((to, subject))


class InMemoryDb:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def insert(self, table: str, row: dict[str, Any]) -> None:
        self.rows.append(row)

    def exists(self, table: str, key: str, value: Any) -> bool:
        return any(r.get(key) == value for r in self.rows)


def test_signup_sends_welcome_and_dedupes() -> None:
    sender, db = FakeSender(), InMemoryDb()
    service = SignupService(sender=sender, db=db)  # wire fakes, no mocks lib

    assert service.signup("ada@example.com") is True
    assert service.signup("ada@example.com") is False  # duplicate blocked

    assert db.rows == [{"email": "ada@example.com"}]
    assert sender.sent == [("ada@example.com", "Welcome!")]


if __name__ == "__main__":
    app = build_app({"smtp_host": "prod-smtp", "db_dsn": "prod-dsn"})
    assert app.signup("first@example.com") is True

    test_signup_sends_welcome_and_dedupes()
    print("ok")
