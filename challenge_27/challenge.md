### 27 — Protocols over Inheritance
```python
class JsonExporter:
    def export(self, data: dict) -> str: ...

class CsvExporter:
    def export(self, data: dict) -> str: ...

def save_report(exporter, data):   # currently untyped
    payload = exporter.export(data)
    ...
```
**Complete:** Define an `Exporter` `typing.Protocol` (make it `@runtime_checkable`), annotate `save_report`, and add a third conforming exporter *without importing anything from the module that defines the protocol* — demonstrating structural typing. Then add a generic `Exporter[T]` variant where `export` takes `T` instead of `dict`.
