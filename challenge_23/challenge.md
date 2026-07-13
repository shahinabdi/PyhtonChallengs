### 23 — String Building and Interning
```python
def render_rows(rows: list[tuple[str, int]]) -> str:
    out = ""
    for name, qty in rows:
        out = out + "<tr><td>" + name + "</td><td>" + str(qty) + "</td></tr>"
    return "<table>" + out + "</table>"
```
**Complete:** Rewrite three ways — `str.join` on a generator, `io.StringIO`, and a single f-string template with `"".join` — then benchmark all four (including the original) at 100k rows and record results in a comment. Which wins and why (think allocation behavior)?
