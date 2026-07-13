# Explanation — Challenge 33

## Concepts required
- Layered / clean / hexagonal architecture: dependencies point inward, the domain is dependency-free.
- The Dependency Inversion Principle: high-level policy owns the interface; low-level detail implements it.
- `ast` module: parsing Python source without executing it; `ast.Import` / `ast.ImportFrom` nodes.
- Architecture-as-code: enforcing rules in CI rather than in review comments.

## (a) The inversion
`domain/models.py` importing `adapters/postgres.py` means business rules know about Postgres — the arrow points outward, so you can't test the domain without adapters, and swapping databases touches the domain. The fix is to move the *interface* to where it's consumed: the domain defines `UserRepository(Protocol)` (the **port**); `adapters/postgres.py` imports *from the domain* and implements it (the **adapter**); services depend on the protocol; only the outermost layer (`api`, the composition root) touches concrete adapters. Same runtime behavior, arrows all point inward.

## (b) The checker
- **Why `ast` and not imports/regex:** importing modules to inspect them *executes* them (side effects, missing deps in CI); regex trips on strings and comments. `ast.parse` reads the source safely and precisely.
- `iter_imports` walks the tree collecting `import x.y` and `from x.y import z` module paths (`node.level == 0` skips relative imports — extend if you use them; `ast.walk` also catches imports nested inside functions, where circular-import workarounds hide).
- The rule table `ALLOWED` maps each layer to layers it may import. For every project-internal import, the file's layer (first path segment under the package) is checked against the imported module's layer; violations produce messages naming the file, both layers, the offending import, and what *is* allowed — actionable, not just "bad import".
- The demo materializes the challenge's exact tree, catches the one violation, applies the sketched fix, and shows a clean run. In CI you'd `sys.exit(1)` when violations exist.

## Alternatives and trade-offs
- **import-linter** is the production tool (declarative contracts in `pyproject.toml`); writing the checker once teaches you what it does.
- `ImportFrom` of a *name* (`from myapp import adapters`) then `adapters.postgres` usage evades this simple checker — import-linter handles module-attribute access patterns more robustly.
- Putting the port in `services` instead of `domain` is a legitimate variant when persistence is a service-level concern.

## Python features used
- **`ast.parse` / `ast.walk` / `ast.Import` / `ast.ImportFrom`**, **`Path.rglob`**, rule tables as dicts, `Protocol` in the refactor sketch.
