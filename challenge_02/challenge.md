### 02 — Replace a "Bag of Attributes" Class with a Dataclass
```python
class Server:
    def __init__(self, host, port, tags=None, healthy=True):
        self.host = host
        self.port = port
        self.tags = tags if tags is not None else []
        self.healthy = healthy

    def __repr__(self):
        return "Server(%s:%s)" % (self.host, self.port)

    def __eq__(self, other):
        return (self.host, self.port) == (other.host, other.port)
```
**Complete:** Convert to a `@dataclass`. Handle the mutable default correctly with `field(default_factory=...)`. Equality must remain based only on `(host, port)` — figure out which dataclass options achieve that.
