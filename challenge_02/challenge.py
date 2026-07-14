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