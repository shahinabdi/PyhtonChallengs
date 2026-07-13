"""Challenge 37 — __init_subclass__ registry with definition-time checks."""

import json
from typing import Any, ClassVar


class Serializer:
    """Subclasses must declare `format: str` and implement dumps().
    They auto-register into Serializer.registry keyed by format.
    Duplicate formats or missing attributes fail AT CLASS DEFINITION
    TIME. Intermediate bases pass abstract=True to skip registration."""

    registry: ClassVar[dict[str, type["Serializer"]]] = {}

    def __init_subclass__(cls, *, abstract: bool = False, **kwargs: Any) -> None:
        # Always cooperate with other bases in the MRO.
        super().__init_subclass__(**kwargs)

        if abstract:
            return  # intermediate base: no contract check, no registration

        # `format` must be declared (inheriting one from an abstract
        # intermediate is fine — hence getattr, not cls.__dict__).
        fmt = getattr(cls, "format", None)
        if fmt is None:
            raise TypeError(
                f"{cls.__name__} must declare a class attribute `format: str`"
            )
        if not isinstance(fmt, str):
            raise TypeError(
                f"{cls.__name__}.format must be str, "
                f"got {type(fmt).__name__} ({fmt!r})"
            )

        dumps = getattr(cls, "dumps", None)
        if dumps is None or dumps is Serializer.dumps:
            raise TypeError(f"{cls.__name__} must implement dumps(self, data)")

        if fmt in Serializer.registry:
            other = Serializer.registry[fmt].__name__
            raise TypeError(
                f"duplicate serializer format {fmt!r}: "
                f"{cls.__name__} clashes with {other}"
            )

        Serializer.registry[fmt] = cls

    def dumps(self, data: Any) -> str:  # contract anchor for the check above
        raise NotImplementedError

    @classmethod
    def for_format(cls, fmt: str) -> "Serializer":
        try:
            return cls.registry[fmt]()
        except KeyError:
            known = ", ".join(sorted(cls.registry)) or "<none>"
            raise ValueError(f"no serializer for {fmt!r}; known: {known}") from None


class JsonSerializer(Serializer):
    format = "json"

    def dumps(self, data: Any) -> str:
        return json.dumps(data, sort_keys=True)


class TextSerializer(Serializer, abstract=True):
    """Intermediate base: adds a helper, is NOT registered itself."""

    separator = "\n"

    def join(self, parts: list[str]) -> str:
        return self.separator.join(parts)


class KeyValueSerializer(TextSerializer):
    format = "kv"

    def dumps(self, data: Any) -> str:
        return self.join(f"{k}={v}" for k, v in dict(data).items())  # type: ignore[arg-type]


if __name__ == "__main__":
    assert sorted(Serializer.registry) == ["json", "kv"]
    assert "TextSerializer" not in {c.__name__ for c in Serializer.registry.values()}

    assert Serializer.for_format("json").dumps({"b": 1, "a": 2}) == '{"a": 2, "b": 1}'
    assert Serializer.for_format("kv").dumps({"x": 1}) == "x=1"

    # Every violation fails AT CLASS DEFINITION TIME:
    for description, definition in {
        "missing format": lambda: type(
            "NoFormat", (Serializer,), {"dumps": lambda self, d: ""}
        ),
        "non-str format": lambda: type(
            "BadFormat", (Serializer,), {"format": 42, "dumps": lambda self, d: ""}
        ),
        "missing dumps": lambda: type(
            "NoDumps", (Serializer,), {"format": "yaml"}
        ),
        "duplicate format": lambda: type(
            "JsonAgain", (Serializer,), {"format": "json", "dumps": lambda self, d: ""}
        ),
    }.items():
        try:
            definition()
        except TypeError as exc:
            print(f"{description:18s} -> TypeError: {exc}")
        else:
            raise AssertionError(f"{description} was not caught")
    print("ok")
