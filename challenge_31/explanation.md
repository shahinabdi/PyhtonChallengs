# Explanation — Challenge 31

## Concepts required
- Dynamic imports: `importlib.import_module`, `pkgutil.iter_modules`, package `__path__`.
- Class introspection: `inspect.getmembers`, `issubclass`, `inspect.isabstract`.
- `__init_subclass__` as an import-time registration hook.
- The two plugin architectures and when each fits.

## Path 1 — Discovery (`load_plugins`)
1. `importlib.import_module(package)` loads the package itself; its `__path__` lists the directories to scan.
2. `pkgutil.iter_modules(pkg.__path__, prefix=...)` enumerates the modules *without importing them*; `import_module` then loads each one.
3. `inspect.getmembers(module, inspect.isclass)` + filters find concrete `Plugin` subclasses. The filters matter: exclude the base itself, exclude abstract intermediates (`inspect.isabstract`), and exclude re-exports (`obj.__module__ == module.__name__` — otherwise `from x import SomePlugin` in another module double-registers it).
4. Instantiate and key by `instance.name`.

The demo builds a real package in a temp directory and loads two plugins from it — proving the machinery works on actual files, not just theory.

## Path 2 — Self-registration (`__init_subclass__`)
`AutoPlugin.__init_subclass__` runs at **class definition time**: merely importing a module containing `class MetricsPlugin(AutoPlugin):` adds it to the registry. No scanning code — but *something must still import the module*.

## Which fits third-party plugins better? (the required judgment)
**Discovery.** Self-registration's Achilles heel is that it only fires on import — and for third-party code, nothing imports the plugin module unless the host goes looking. So a discovery loop is needed *anyway*; at that point it may as well do the registration too. Discovery also lets the host control the search locations, wrap each module import in a try/except (one broken third-party plugin shouldn't kill the app), and defer loading. `__init_subclass__` registration is ideal *within* a single codebase where all modules get imported in normal operation.

For real third-party distribution, the production-grade answer is **entry points** (`importlib.metadata.entry_points(group="myapp.plugins")`) — plugins declare themselves in their packaging metadata, no filesystem scanning at all.

## Python features used
- **`pkgutil.iter_modules`**, **`importlib.import_module`**, **`inspect.getmembers`/`isabstract`**, **`__init_subclass__`**, ABC + class attribute contract.
