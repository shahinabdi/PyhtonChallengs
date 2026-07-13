"""Challenge 23 — String building strategies, benchmarked."""

import io
import timeit


def render_rows_concat(rows: list[tuple[str, int]]) -> str:
    """Original: repeated `out = out + ...`."""
    out = ""
    for name, qty in rows:
        out = out + "<tr><td>" + name + "</td><td>" + str(qty) + "</td></tr>"
    return "<table>" + out + "</table>"


def render_rows_join(rows: list[tuple[str, int]]) -> str:
    """str.join on a generator of f-string fragments."""
    body = "".join(
        f"<tr><td>{name}</td><td>{qty}</td></tr>" for name, qty in rows
    )
    return f"<table>{body}</table>"


def render_rows_stringio(rows: list[tuple[str, int]]) -> str:
    """io.StringIO as an in-memory write buffer."""
    buf = io.StringIO()
    buf.write("<table>")
    for name, qty in rows:
        buf.write(f"<tr><td>{name}</td><td>{qty}</td></tr>")
    buf.write("</table>")
    return buf.getvalue()


def render_rows_template_join(rows: list[tuple[str, int]]) -> str:
    """Single f-string wrapping a "".join over a list comprehension."""
    return f"""<table>{"".join([f"<tr><td>{n}</td><td>{q}</td></tr>" for n, q in rows])}</table>"""


# BENCHMARK RESULTS (100_000 rows, CPython 3.12, one machine — rerun
# yourself; ratios are what matter, absolute times vary):
#
#   concat (original)      ~55 ms
#   str.join(generator)    ~23 ms
#   io.StringIO            ~30 ms
#   f-string + "".join     ~21 ms   <- winner (list comp beats genexp
#                                      slightly: join can pre-size)
#
# WHY: naive `out = out + piece` LOOKS quadratic — a fresh string each
# iteration, copying everything so far. CPython has an in-place resize
# optimization for `str = str + x` when refcount==1, which usually saves
# the original from true O(n^2)... but it's an implementation detail
# (absent on PyPy, defeated if any other reference to `out` exists) and
# still does many reallocations+memcpys as the buffer regrows.
# "".join computes the TOTAL length first, allocates the final string
# EXACTLY ONCE, then memcpys each fragment in: one allocation, zero
# regrowth. Feeding join a LIST lets it size in one pass (a generator is
# materialized into a list internally anyway). StringIO pays method-call
# and buffer-management overhead per write; it wins instead when you're
# building incrementally across many call sites or need a file-like API.
# (Interning is irrelevant here: CPython interns identifier-like literals
# and small strings, e.g. "abc" is "abc" -> True, but runtime-built row
# strings are never interned automatically.)


if __name__ == "__main__":
    rows = [(f"item-{i}", i) for i in range(100_000)]

    expected = render_rows_concat(rows[:50])
    for fn in (render_rows_join, render_rows_stringio, render_rows_template_join):
        assert fn(rows[:50]) == expected, fn.__name__

    for fn in (
        render_rows_concat,
        render_rows_join,
        render_rows_stringio,
        render_rows_template_join,
    ):
        t = min(timeit.repeat(lambda f=fn: f(rows), number=1, repeat=5))
        print(f"{fn.__name__:28s} {t * 1000:8.1f} ms")
    print("ok")
