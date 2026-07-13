### 31 — Plugin Architecture: Discovery + Registration
```python
# app/plugins/__init__.py
class Plugin(ABC):
    name: str
    @abstractmethod
    def run(self, ctx: dict) -> None: ...

def load_plugins(package: str) -> dict[str, Plugin]:
    """Import every module in `package`, find Plugin subclasses,
    instantiate and return them keyed by .name."""
    ...  # TODO: pkgutil.iter_modules + importlib
```
**Complete:** Implement `load_plugins`. Then add an alternative registration path using `__init_subclass__` on `Plugin` so subclasses self-register at import time, and note in comments which approach fits a third-party-plugin scenario better.
