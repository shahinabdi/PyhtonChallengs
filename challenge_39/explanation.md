# Explanation — Challenge 39

## Concepts required
- Data descriptors (challenge 12's machinery) as ORM columns.
- Metaclasses (challenge 38's machinery) collecting class-body declarations.
- Code generation: synthesizing `__init__`, `to_dict`, `__repr__` as closures installed on the class.
- How Django/SQLAlchemy/Pydantic-style declarative APIs actually work — this is their skeleton.

## The division of labor
**`Field` (per-attribute):** a data descriptor. `__set_name__` learns its column name; `__set__` validates `isinstance(value, py_type)` on *every* assignment — construction and later mutation alike (`user.email = 123` fails just like `User(email=123)`). Values live in the instance `__dict__`; since `Field` is a data descriptor it still intercepts reads/writes for its public name. The error message names class, field, expected and actual types — ORM errors are read far more often than written.

**`ModelMeta` (per-class):** runs once per model definition:
1. **Collects fields in order** — class bodies execute into a dict, and dicts preserve insertion order, so `_fields` matches the declaration order (this ordering is what lets real ORMs emit stable `CREATE TABLE` column order).
2. **Validates exactly one primary key** at class-definition time — a schema error crashes the import, not the first query.
3. **Generates `__init__`** requiring every field as a kwarg. Crucially it assigns via `setattr`, which routes through `Field.__set__` — the metaclass *reuses* the descriptor's validation instead of duplicating it. Unknown kwargs are rejected with the offending names.
4. **Generates `to_dict` and `__repr__`** from the same `_fields` — one source of truth.

The `if not fields: return cls` guard leaves field-less bases/mixins untouched.

## Design notes and trade-offs
- `isinstance` means `bool` passes an `int` field (bool subclasses int) — Python-consistent; noted in the code with the strict alternative.
- Generated `__init__` makes all fields required; real ORMs add `default=`/`nullable=` on `Field` — a natural extension.
- Could `__init_subclass__` do this? Mostly yes (collect + validate), but models would have to inherit a base with fields *and* the base class itself couldn't be processed the same way; the metaclass also owns `__repr__`/`__init__` injection before any instance exists. Declarative ORM bases are the canonical "metaclass is actually justified" case.
- Inherited fields from model bases aren't merged here (namespace-only scan) — real ORMs walk the MRO; a good extension exercise.

## Python features used
- **Descriptor protocol** (`__set_name__`, `__get__`, `__set__`), **metaclass `__new__`**, **closures installed as methods**, ordered class namespaces, definition-time validation.
