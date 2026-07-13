"""Challenge 04 — Enum + exhaustive handling with assert_never."""

from enum import Enum
from typing import assert_never


class State(Enum):
    PENDING = 0
    RUNNING = 1
    DONE = 2
    FAILED = 3


def describe(state: State) -> str:
    match state:
        case State.PENDING:
            return "waiting"
        case State.RUNNING:
            return "in progress"
        case State.DONE:
            return "finished"
        case State.FAILED:
            return "failed"
        case _:
            # Two safety nets in one:
            # * Statically: if a new member (say State.PAUSED) is added, the
            #   type checker narrows `state` in each case; whatever is left
            #   over reaches assert_never, whose parameter is typed `Never`.
            #   A non-empty leftover type is a type error at CI time.
            # * At runtime: assert_never raises AssertionError immediately,
            #   instead of silently returning None.
            assert_never(state)


if __name__ == "__main__":
    for state, expected in [
        (State.PENDING, "waiting"),
        (State.RUNNING, "in progress"),
        (State.DONE, "finished"),
        (State.FAILED, "failed"),
    ]:
        assert describe(state) == expected

    # Demonstrate the loud runtime failure for an unhandled value.
    try:
        describe("not-a-state")  # type: ignore[arg-type]
    except AssertionError as exc:
        print(f"caught as designed: {exc!r}")
    print("ok")
