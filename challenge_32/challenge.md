### 32 — Dependency Injection Without a Framework
```python
class EmailSender:
    def __init__(self):
        self.smtp = SmtpClient(host="prod-smtp")   # hard-wired!

class SignupService:
    def __init__(self):
        self.sender = EmailSender()                # hard-wired!
        self.db = PostgresDb("prod-dsn")           # hard-wired!

    def signup(self, email: str): ...
```
**Complete:** Refactor to constructor injection with `Protocol`-typed dependencies, then write a tiny composition root (`build_app(config)`) that wires prod implementations, and a test snippet that wires fakes. No DI library.
