"""Challenge 02 — Replace a "bag of attributes" class with a dataclass."""

from dataclasses import dataclass, field


@dataclass
class Server:
    host: str
    port: int
    # A mutable default like `tags=[]` would be shared by every instance;
    # default_factory builds a fresh list per instance. compare=False keeps
    # these two fields out of the generated __eq__, so equality stays
    # based only on (host, port) — exactly like the hand-written original.
    tags: list[str] = field(default_factory=list, compare=False)
    healthy: bool = field(default=True, compare=False)

    def __repr__(self) -> str:
        # dataclass never overwrites a method defined in the class body,
        # so this custom repr wins over the auto-generated one.
        return f"Server({self.host}:{self.port})"


if __name__ == "__main__":
    a = Server("web-1", 8080)
    b = Server("web-1", 8080, tags=["prod"], healthy=False)
    c = Server("web-2", 8080)

    assert a == b            # tags/healthy ignored in equality
    assert a != c
    assert repr(a) == "Server(web-1:8080)"

    a.tags.append("edge")
    assert b.tags == ["prod"]  # no shared mutable default
    print("ok")
