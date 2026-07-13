"""Challenge 12 — A data descriptor for validated, bounded fields."""


class Bounded:
    """Descriptor enforcing minimum <= value <= maximum on instances."""

    def __init__(self, minimum: float, maximum: float) -> None:
        if minimum > maximum:
            raise ValueError(f"minimum ({minimum}) > maximum ({maximum})")
        self.minimum = minimum
        self.maximum = maximum
        self.public_name = "<unset>"
        self.private_name = "<unset>"

    def __set_name__(self, owner: type, name: str) -> None:
        # Called automatically at class creation: tells the descriptor
        # which attribute name it was assigned to ("celsius").
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj: object | None, objtype: type | None = None):
        if obj is None:
            # Accessed on the class (Thermostat.celsius): return the
            # descriptor itself, so introspection and help() work.
            return self
        try:
            return obj.__dict__[self.private_name]
        except KeyError:
            raise AttributeError(
                f"{objtype.__name__ if objtype else type(obj).__name__}."
                f"{self.public_name} was never set"
            ) from None

    def __set__(self, obj: object, value: float) -> None:
        if not (self.minimum <= value <= self.maximum):
            raise ValueError(
                f"{self.public_name} must be in "
                f"[{self.minimum}, {self.maximum}], got {value!r}"
            )
        # Per-instance storage: each object keeps its own value in its own
        # __dict__. Storing on `self` (the descriptor) would be shared by
        # every instance of the owner class — the classic descriptor bug.
        obj.__dict__[self.private_name] = value


class Thermostat:
    celsius = Bounded(-30, 60)


if __name__ == "__main__":
    t1 = Thermostat()
    t2 = Thermostat()
    t1.celsius = 21.5
    t2.celsius = -5

    assert t1.celsius == 21.5
    assert t2.celsius == -5          # no shared state between instances
    assert isinstance(Thermostat.celsius, Bounded)  # class access -> descriptor

    try:
        t1.celsius = 100
    except ValueError as exc:
        assert "celsius" in str(exc)
        print(f"rejected as designed: {exc}")

    try:
        Thermostat().celsius
    except AttributeError as exc:
        print(f"unset access: {exc}")
    print("ok")
