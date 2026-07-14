from dataclasses import dataclass,field


@dataclass
class Server:
    host: str
    port: int
    tags: list[str] = field(default_factory=list, compare=False)
    healthy: bool = field(default=True, compare=False)
    # compare=False in the field definitions 
    # ensures that these attributes are ignored
    # in the generated __eq__ method
    def __repr__(self):
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