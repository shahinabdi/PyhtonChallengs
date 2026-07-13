"""Challenge 27 — Structural typing with Protocol (+ a generic variant)."""

import csv
import io
import json
from typing import Protocol, runtime_checkable


# ---- the protocol (think of this as module `report.types`) ---------------
@runtime_checkable
class Exporter(Protocol):
    def export(self, data: dict) -> str: ...


def save_report(exporter: Exporter, data: dict) -> str:
    payload = exporter.export(data)
    return f"saved {len(payload)} bytes"


# ---- conforming implementations ------------------------------------------
class JsonExporter:
    def export(self, data: dict) -> str:
        return json.dumps(data, sort_keys=True)


class CsvExporter:
    def export(self, data: dict) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return buf.getvalue()


# ---- "third-party" exporter ----------------------------------------------
# Pretend this class lives in another package. It imports NOTHING from the
# protocol's module — no Exporter import, no subclassing, no registration.
# It conforms purely by SHAPE: it has `export(self, data: dict) -> str`,
# so type checkers accept it where Exporter is expected. That is
# structural typing; nominal typing (ABCs) would require an explicit
# inheritance/registration link between the two modules.
class MarkdownExporter:
    def export(self, data: dict) -> str:
        rows = "\n".join(f"| {k} | {v} |" for k, v in data.items())
        return f"| key | value |\n|---|---|\n{rows}"


# ---- generic variant -------------------------------------------------------
@runtime_checkable
class GenericExporter[T](Protocol):
    """Same idea, but generic: an exporter of T-shaped inputs.
    GenericExporter[list[str]] means: export takes list[str]."""

    def export(self, data: T) -> str: ...


class LinesExporter:
    """Conforms to GenericExporter[list[str]]."""

    def export(self, data: list[str]) -> str:
        return "\n".join(data)


def save_generic[T](exporter: GenericExporter[T], data: T) -> str:
    return f"saved {len(exporter.export(data))} bytes"


if __name__ == "__main__":
    data = {"service": "auth", "errors": 3}

    for exporter in (JsonExporter(), CsvExporter(), MarkdownExporter()):
        print(f"{type(exporter).__name__:18s}", save_report(exporter, data))
        # runtime_checkable enables isinstance — checks method PRESENCE
        # only, not the signature/return type.
        assert isinstance(exporter, Exporter)

    class NotAnExporter:
        def dump(self, data: dict) -> str:  # wrong method name
            return ""

    assert not isinstance(NotAnExporter(), Exporter)

    assert save_generic(LinesExporter(), ["a", "b", "c"]) == "saved 5 bytes"
    # Type checker catches: save_generic(LinesExporter(), {"not": "a list"})
    print("ok")
