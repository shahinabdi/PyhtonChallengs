### 08 — Replace `**kwargs` Soup with TypedDict + Unpack
```python
def create_container(**kwargs):
    image = kwargs["image"]
    cpu = kwargs.get("cpu", 1.0)
    memory_mb = kwargs.get("memory_mb", 512)
    env = kwargs.get("env", {})
    ...
```
**Complete:** Define a `TypedDict` (with `Required`/`NotRequired`) and change the signature to `def create_container(**kwargs: Unpack[ContainerSpec])`. Type-check mentally: which keys must a caller supply?
