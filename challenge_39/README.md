# Challenge 39 — Study Checklist

To solve this challenge, you should understand:
- The descriptor protocol as reusable per-attribute behavior (see challenge 12)
- Metaclass `__new__` and class-namespace scanning (see challenge 38)
- Why class bodies preserve declaration order
- Generating methods as closures and installing them on a class
- Routing generated `__init__` through descriptors (`setattr`) to reuse validation
- Definition-time schema validation (exactly one primary key)
- `isinstance` and the `bool`-is-an-`int` subtlety
- How Django models / SQLAlchemy declarative / Pydantic work under the hood
