# Challenge 37 — Study Checklist

To solve this challenge, you should understand:
- `__init_subclass__` (PEP 487) and when it runs
- Keyword arguments in the `class` statement (`class C(Base, flag=True):`)
- Import time / class definition time vs first-use failure
- `getattr` vs `cls.__dict__` for inherited-attribute checks
- Detecting "not overridden" via identity with the base method
- `typing.ClassVar`
- Why this pattern replaced many metaclass uses
- Dynamic class creation with `type(name, bases, namespace)`
