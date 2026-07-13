### 01 — Modernize String Formatting and Path Handling
Legacy 3.6-era code using `os.path` and `%`-formatting.
```python
import os

def build_report_path(base_dir, user, year):
    filename = "report_%s_%d.txt" % (user, year)
    full = os.path.join(base_dir, "reports", filename)
    if not os.path.exists(os.path.dirname(full)):
        os.makedirs(os.path.dirname(full))
    return full
```
**Complete:** Rewrite using `pathlib.Path` and f-strings. Add full type hints. Preserve behavior exactly (including directory creation semantics).
