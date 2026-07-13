### 33 — Layered Architecture Enforcement
```
myapp/
  domain/models.py        # must import NOTHING from other layers
  services/signup.py      # may import domain only
  adapters/postgres.py    # may import domain + services interfaces
  api/http.py             # outermost
```
The current code has `domain/models.py` importing from `adapters/postgres.py`.
**Complete:** (a) Sketch the refactor that inverts that dependency (define the repository interface in `domain` or `services`, implement it in `adapters`). (b) Write a checker script that walks the package with `ast`, extracts imports per module, and fails with a clear message on any layering violation.
