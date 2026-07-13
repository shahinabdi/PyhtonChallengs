"""Challenge 31 — Plugin discovery (pkgutil) + self-registration."""

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod


class Plugin(ABC):
    """Base for discovered plugins (path 1: explicit scan)."""

    name: str

    @abstractmethod
    def run(self, ctx: dict) -> None: ...


def load_plugins(package: str) -> dict[str, Plugin]:
    """Import every module in `package`, find Plugin subclasses,
    instantiate and return them keyed by .name.

    WHICH APPROACH FITS THIRD-PARTY PLUGINS BETTER? This one (discovery).
    Third-party code can't be trusted to inherit from OUR base eagerly at
    the right time: self-registration only fires when the plugin module is
    imported, so someone must import it anyway — and that someone is a
    discovery loop. Scanning also lets the host decide WHERE to look
    (a plugins/ dir, entry points), sandbox failures per module, and load
    lazily. __init_subclass__ registration shines WITHIN one codebase
    where all plugin modules are imported as a matter of course.
    """
    pkg = importlib.import_module(package)
    plugins: dict[str, Plugin] = {}
    for mod_info in pkgutil.iter_modules(pkg.__path__, prefix=f"{package}."):
        module = importlib.import_module(mod_info.name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, Plugin)
                and obj is not Plugin
                and not inspect.isabstract(obj)
                and obj.__module__ == module.__name__  # skip re-exports
            ):
                instance = obj()
                plugins[instance.name] = instance
    return plugins


class AutoPlugin(ABC):
    """Base for self-registering plugins (path 2: __init_subclass__)."""

    name: str
    registry: dict[str, type["AutoPlugin"]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        # Runs at class DEFINITION time, i.e. when the module is imported.
        if not inspect.isabstract(cls) and hasattr(cls, "name"):
            AutoPlugin.registry[cls.name] = cls

    @abstractmethod
    def run(self, ctx: dict) -> None: ...


if __name__ == "__main__":
    import sys
    import tempfile
    from pathlib import Path
    from textwrap import dedent

    # Build a real throwaway plugin package on disk to prove discovery.
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = Path(tmp) / "demo_plugins"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text(
            "from challenge_31_base import Plugin\n", encoding="utf-8"
        )
        (pkg_dir / "greet.py").write_text(dedent("""
            from demo_plugins import Plugin

            class GreetPlugin(Plugin):
                name = "greet"
                def run(self, ctx: dict) -> None:
                    ctx["out"] = f"hello {ctx.get('user', 'world')}"
        """), encoding="utf-8")
        (pkg_dir / "shout.py").write_text(dedent("""
            from demo_plugins import Plugin

            class ShoutPlugin(Plugin):
                name = "shout"
                def run(self, ctx: dict) -> None:
                    ctx["out"] = ctx.get("out", "").upper()
        """), encoding="utf-8")

        # Expose our Plugin base to the generated package.
        base = sys.modules.setdefault("challenge_31_base", sys.modules[__name__])
        sys.path.insert(0, tmp)
        try:
            plugins = load_plugins("demo_plugins")
        finally:
            sys.path.remove(tmp)

        assert sorted(plugins) == ["greet", "shout"], plugins
        ctx: dict = {"user": "ada"}
        plugins["greet"].run(ctx)
        plugins["shout"].run(ctx)
        assert ctx["out"] == "HELLO ADA"
        print(f"discovered: {sorted(plugins)}")

    # Path 2: self-registration happens the moment the class is defined.
    class MetricsPlugin(AutoPlugin):
        name = "metrics"
        def run(self, ctx: dict) -> None:
            ctx["metrics"] = True

    assert "metrics" in AutoPlugin.registry
    AutoPlugin.registry["metrics"]().run(ctx := {})
    assert ctx == {"metrics": True}
    print("ok")
