# Explanation — Challenge 40

## Concepts required (the capstone pulls prior challenges together)
- Dual-form decorators (challenge 09's factory pattern, plus the bare/parameterized trick).
- Graph algorithms: DFS topological ordering and three-color cycle detection.
- `asyncio.TaskGroup` + per-task `Future`s as completion signals (challenges 15–17).
- Status modeling with `StrEnum` (challenge 35); PEP 695 `type` aliases.

## Key design decisions

**`task` usable with and without arguments.** One function handles both: bare `@task` passes the function as `fn` → wrap immediately; `@task(depends_on=[...])` passes `fn=None` → return the real decorator. The decorator returns a `Task` *object* (not a wrapped function) because the engine needs metadata (`depends_on`, `name`) — the decorated name becomes a graph node. `@dataclass(eq=False)` keeps identity hashing so tasks work as dict keys.

**Cycle detection with the path.** Three-color DFS: GREY = on the current path; meeting a GREY dependency is a back edge, and the slice of the visit stack from that node onward *is* the cycle — reported as `a -> b -> a`, which is what a human debugging a workflow actually needs. (Stdlib `graphlib.TopologicalSorter` also detects cycles and is the production choice; hand-rolling exposes the algorithm.)

**Scheduling via completion futures, not layered batches.** Each task gets a `Future`; `run_one` awaits its dependencies' futures, then runs. All tasks start inside one `TaskGroup`, and readiness resolves *dynamically*: independent tasks (transform/audit) run concurrently the moment their shared dependency finishes — no artificial "level barriers" where a slow task in one layer would stall an unrelated ready task.

**Failure containment.** A task exception is caught inside `run_one`, recorded, and published as `FAILED` through its future. Dependents see a non-`SUCCEEDED` outcome and mark themselves `SKIPPED` — transitively (skipped is also not-succeeded). Crucially the exception is *not* re-raised inside the TaskGroup: that would cancel unrelated branches, and the spec says stop *dependents*, not the world. The demo asserts `transform` still succeeds while `load2` is skipped.

**The final report** maps every task name to `TaskStatus` — the per-task status accounting the spec requires, with errors summarized separately.

## Extensions to try
Results flowing between tasks (futures already carry a slot), per-task timeout/retry (challenges 09/16), max-concurrency semaphore (challenge 15), `graphlib`-based scheduler comparison.

## Python features used
- **PEP 695 `type` aliases**, **`StrEnum`**, **`asyncio.TaskGroup` + `loop.create_future()`**, **dual-form decorator**, three-color DFS, `dataclass(eq=False)`.
