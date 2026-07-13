### 11 — ExitStack for Dynamic Resource Acquisition
```python
def open_all(paths: list[str]):
    """Open every file; if ANY open fails, close the ones already opened,
    then re-raise. On success return the list of file objects."""
    handles = []
    # TODO (without ExitStack this is fiddly — use contextlib.ExitStack)
```
**Complete:** Implement with `ExitStack`, including the success case where ownership of the open files transfers to the caller (`pop_all`).
