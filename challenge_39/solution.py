"""Challenge 39 — Mini ORM: descriptors for fields, metaclass for models."""

from typing import Any


class Field:
    """Data descriptor: validates type on every assignment."""

    def __init__(self, py_type: type, primary_key: bool = False) -> None:
        self.py_type = py_type
        self.primary_key = primary_key
        self.name = "<unbound>"

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self  # class access -> the Field itself (introspection)
        return obj.__dict__[self.name]

    def __set__(self, obj: Any, value: Any) -> None:
        # NB: isinstance, so bool sneaks into int fields (bool subclasses
        # int) — matching Python's own semantics; use `type(value) is`
        # for strictness if desired.
        if not isinstance(value, self.py_type):
            raise TypeError(
                f"{type(obj).__name__}.{self.name} expects "
                f"{self.py_type.__name__}, got {type(value).__name__} "
                f"({value!r})"
            )
        obj.__dict__[self.name] = value

    def __repr__(self) -> str:
        pk = ", primary_key=True" if self.primary_key else ""
        return f"Field({self.py_type.__name__}{pk})"


class ModelMeta(type):
    """Collect Field attributes into cls._fields (ordered), validate
    exactly one primary key, generate __init__ (kwargs, type-checked via
    the descriptors) and to_dict()."""

    def __new__(
        mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> type:
        cls = super().__new__(mcls, name, bases, namespace)

        # Class bodies preserve definition order (dicts are ordered), so
        # _fields is ordered exactly as written in the class.
        fields = {
            attr: value
            for attr, value in namespace.items()
            if isinstance(value, Field)
        }
        cls._fields = fields

        if not fields:
            return cls  # a base/mixin without fields: leave it alone

        primary_keys = [n for n, f in fields.items() if f.primary_key]
        if len(primary_keys) != 1:
            raise TypeError(
                f"{name} must define exactly one primary key field, "
                f"found {len(primary_keys)}: {primary_keys or 'none'}"
            )
        cls._primary_key = primary_keys[0]

        def __init__(self: Any, **kwargs: Any) -> None:
            for field_name in type(self)._fields:
                if field_name not in kwargs:
                    raise TypeError(f"missing required field {field_name!r}")
                # setattr routes through Field.__set__ -> type check.
                setattr(self, field_name, kwargs.pop(field_name))
            if kwargs:
                raise TypeError(
                    f"unknown field(s) for {type(self).__name__}: "
                    f"{sorted(kwargs)}"
                )

        def to_dict(self: Any) -> dict[str, Any]:
            return {n: getattr(self, n) for n in type(self)._fields}

        def __repr__(self: Any) -> str:
            pairs = ", ".join(f"{n}={getattr(self, n)!r}" for n in type(self)._fields)
            return f"{type(self).__name__}({pairs})"

        cls.__init__ = __init__
        cls.to_dict = to_dict
        cls.__repr__ = __repr__
        return cls


class User(metaclass=ModelMeta):
    id = Field(int, primary_key=True)
    email = Field(str)


if __name__ == "__main__":
    user = User(id=1, email="a@b.c")
    assert user.id == 1 and user.email == "a@b.c"
    assert user.to_dict() == {"id": 1, "email": "a@b.c"}
    assert repr(user) == "User(id=1, email='a@b.c')"
    assert list(User._fields) == ["id", "email"]        # ordered
    assert User._primary_key == "id"
    assert isinstance(User.id, Field)                   # class access

    for bad_call in (
        lambda: User(id="x", email="a@b.c"),            # wrong type
        lambda: User(id=2),                             # missing field
        lambda: User(id=2, email="e", extra=True),      # unknown field
    ):
        try:
            bad_call()
        except TypeError as exc:
            print(f"rejected: {exc}")
        else:
            raise AssertionError("bad call was accepted")

    user.email = "new@b.c"                              # revalidated on set
    try:
        user.email = 123
    except TypeError as exc:
        print(f"rejected: {exc}")

    # Exactly-one-primary-key is enforced at class definition time.
    try:
        class NoPk(metaclass=ModelMeta):
            name = Field(str)
    except TypeError as exc:
        print(f"rejected: {exc}")

    try:
        class TwoPk(metaclass=ModelMeta):
            a = Field(int, primary_key=True)
            b = Field(int, primary_key=True)
    except TypeError as exc:
        print(f"rejected: {exc}")
    print("ok")
