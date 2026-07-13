"""Challenge 33 — Layered architecture: dependency inversion + AST checker.

(a) THE REFACTOR SKETCH (dependency inversion):

    BEFORE (violation — domain depends outward):
        # domain/models.py
        from myapp.adapters.postgres import PostgresUserRepo   # BAD
        class User:
            def save(self): PostgresUserRepo().save(self)

    AFTER (dependency points inward; domain owns the interface):
        # domain/models.py — imports nothing from other layers
        class User: ...
        class UserRepository(Protocol):          # the PORT
            def save(self, user: User) -> None: ...

        # adapters/postgres.py — implements the domain's interface
        from myapp.domain.models import User, UserRepository
        class PostgresUserRepo:                  # the ADAPTER
            def save(self, user: User) -> None: ...

        # services/signup.py — depends on the abstraction only
        from myapp.domain.models import User, UserRepository
        def signup(repo: UserRepository, email: str) -> User: ...

        # api/http.py — composition root wires the concrete adapter in
        from myapp.adapters.postgres import PostgresUserRepo
        from myapp.services.signup import signup

    The domain now defines WHAT persistence looks like; adapters supply
    HOW. Every arrow points inward (ports & adapters / clean architecture).
"""

import ast
import sys
from pathlib import Path

# (b) THE CHECKER — layer -> set of layers it may import from.
ALLOWED: dict[str, set[str]] = {
    "domain": set(),
    "services": {"domain"},
    "adapters": {"domain", "services"},
    "api": {"domain", "services", "adapters"},
}


def iter_imports(tree: ast.AST) -> list[str]:
    """Yield dotted module names imported anywhere in the tree."""
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append(node.module)
    return found


def check_layers(root: Path, package: str) -> list[str]:
    """Return a list of violation messages (empty = architecture is clean)."""
    violations: list[str] = []
    for py_file in sorted((root / package).rglob("*.py")):
        rel = py_file.relative_to(root / package)
        if len(rel.parts) < 2:
            continue  # top-level files (e.g. __init__.py) are unlayered
        layer = rel.parts[0]
        if layer not in ALLOWED:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for imported in iter_imports(tree):
            parts = imported.split(".")
            if parts[0] != package or len(parts) < 2:
                continue  # stdlib/third-party imports are always fine
            target_layer = parts[1]
            if target_layer in ALLOWED and target_layer != layer \
                    and target_layer not in ALLOWED[layer]:
                violations.append(
                    f"{package}/{rel.as_posix()}: layer '{layer}' may not "
                    f"import from layer '{target_layer}' "
                    f"(found: import {imported}; allowed for '{layer}': "
                    f"{sorted(ALLOWED[layer]) or 'nothing'})"
                )
    return violations


if __name__ == "__main__":
    import tempfile
    from textwrap import dedent

    # Build a sample tree containing exactly the challenge's violation.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        files = {
            "myapp/__init__.py": "",
            "myapp/domain/__init__.py": "",
            "myapp/domain/models.py": dedent("""
                from dataclasses import dataclass
                from myapp.adapters.postgres import PostgresUserRepo  # VIOLATION
                @dataclass
                class User:
                    email: str
            """),
            "myapp/services/__init__.py": "",
            "myapp/services/signup.py": "from myapp.domain.models import User\n",
            "myapp/adapters/__init__.py": "",
            "myapp/adapters/postgres.py": dedent("""
                from myapp.domain.models import User
                class PostgresUserRepo: ...
            """),
            "myapp/api/__init__.py": "",
            "myapp/api/http.py": dedent("""
                from myapp.services.signup import *
                from myapp.adapters.postgres import PostgresUserRepo
            """),
        }
        for rel_path, content in files.items():
            f = root / rel_path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content, encoding="utf-8")

        violations = check_layers(root, "myapp")
        for v in violations:
            print(f"LAYERING VIOLATION: {v}")
        assert len(violations) == 1 and "domain" in violations[0]

        # Apply the sketched fix: domain defines the port, imports nothing.
        (root / "myapp/domain/models.py").write_text(dedent("""
            from dataclasses import dataclass
            from typing import Protocol

            @dataclass
            class User:
                email: str

            class UserRepository(Protocol):
                def save(self, user: "User") -> None: ...
        """), encoding="utf-8")

        assert check_layers(root, "myapp") == []
        print("after inversion: architecture clean")

    # Real-world usage: exit nonzero for CI.
    sys.exit(0)
