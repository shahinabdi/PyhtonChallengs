"""Challenge 40 — Capstone: a mini async workflow engine."""

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

type Ctx = dict[str, object]
type TaskFn = Callable[[Ctx], Awaitable[object]]


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"  # a dependency failed or was skipped


@dataclass(eq=False)  # identity hash: tasks are nodes, not values
class Task:
    fn: TaskFn
    depends_on: tuple["Task", ...] = ()
    name: str = ""

    def __repr__(self) -> str:
        return f"<task {self.name}>"


class CycleError(ValueError):
    def __init__(self, path: list[str]) -> None:
        super().__init__(f"dependency cycle: {' -> '.join(path)}")
        self.path = path


def task(
    fn: TaskFn | None = None, *, depends_on: Sequence[Task] = ()
) -> Task | Callable[[TaskFn], Task]:
    """Decorator usable bare (@task) or parameterized (@task(depends_on=[...])).

    Bare: `fn` is the function -> wrap directly.
    Parameterized: called with only kwargs -> return the real decorator.
    """
    def wrap(f: TaskFn) -> Task:
        return Task(fn=f, depends_on=tuple(depends_on), name=f.__name__)

    return wrap(fn) if fn is not None else wrap


def _collect(tasks: Sequence[Task]) -> list[Task]:
    """All tasks incl. transitive dependencies, deduped, stable order."""
    seen: dict[Task, None] = {}

    def visit(t: Task) -> None:
        if t not in seen:
            for dep in t.depends_on:
                visit(dep)
            seen[t] = None

    for t in tasks:
        visit(t)
    return list(seen)  # dependencies precede dependents = topological order


def _check_cycles(tasks: Sequence[Task]) -> None:
    """DFS three-color cycle detection; raises with the actual cycle path."""
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[Task, int] = dict.fromkeys(tasks, WHITE)
    stack: list[Task] = []

    def visit(t: Task) -> None:
        color[t] = GREY
        stack.append(t)
        for dep in t.depends_on:
            if color.get(dep, WHITE) == GREY:  # back edge -> cycle
                cycle_start = stack.index(dep)
                path = [x.name for x in stack[cycle_start:]] + [dep.name]
                raise CycleError(path)
            if color.get(dep, WHITE) == WHITE:
                visit(dep)
        stack.pop()
        color[t] = BLACK

    for t in tasks:
        if color[t] == WHITE:
            visit(t)


async def run_workflow(
    tasks: Sequence[Task], ctx: Ctx
) -> dict[str, TaskStatus]:
    """Run the graph: independent tasks concurrently, dependents only
    after all dependencies succeed; a failure SKIPs its dependents (it
    does not abort unrelated branches). Returns name -> final status."""
    all_tasks = _collect(tasks)          # also a valid topological order
    _check_cycles(all_tasks)

    status: dict[Task, TaskStatus] = dict.fromkeys(all_tasks, TaskStatus.PENDING)
    errors: dict[str, BaseException] = {}
    loop = asyncio.get_running_loop()
    # Completion future per task: dependents await these instead of
    # polling; setting the result releases every waiter at once.
    done: dict[Task, asyncio.Future[TaskStatus]] = {
        t: loop.create_future() for t in all_tasks
    }

    async def run_one(t: Task) -> None:
        dep_outcomes = [await done[dep] for dep in t.depends_on]
        if any(outcome is not TaskStatus.SUCCEEDED for outcome in dep_outcomes):
            status[t] = TaskStatus.SKIPPED
        else:
            status[t] = TaskStatus.RUNNING
            try:
                await t.fn(ctx)
            except Exception as exc:
                # Contain the failure: mark FAILED, record the error, let
                # unrelated branches continue. Raising here would make the
                # TaskGroup cancel the entire workflow.
                status[t] = TaskStatus.FAILED
                errors[t.name] = exc
            else:
                status[t] = TaskStatus.SUCCEEDED
        done[t].set_result(status[t])

    async with asyncio.TaskGroup() as tg:
        for t in all_tasks:
            tg.create_task(run_one(t))

    report = {t.name: status[t] for t in all_tasks}
    if errors:
        print(f"workflow errors: { {k: repr(v) for k, v in errors.items()} }")
    return report


# ---- demo -------------------------------------------------------------------
if __name__ == "__main__":

    @task
    async def extract(ctx: Ctx) -> None:
        await asyncio.sleep(0.02)
        ctx["rows"] = [1, 2, 3]

    @task(depends_on=[extract])
    async def transform(ctx: Ctx) -> None:
        await asyncio.sleep(0.02)
        ctx["rows"] = [r * 10 for r in ctx["rows"]]  # type: ignore[index]

    @task(depends_on=[extract])
    async def audit(ctx: Ctx) -> None:
        await asyncio.sleep(0.02)
        ctx["audited"] = True

    @task(depends_on=[transform, audit])
    async def load(ctx: Ctx) -> None:
        ctx["loaded"] = ctx["rows"]

    async def main() -> None:
        # Happy path: transform/audit run CONCURRENTLY after extract.
        ctx: Ctx = {}
        report = await run_workflow([extract, transform, audit, load], ctx)
        assert all(s is TaskStatus.SUCCEEDED for s in report.values()), report
        assert ctx["loaded"] == [10, 20, 30] and ctx["audited"] is True
        print("happy path:", dict(report))

        # Failure path: audit fails -> load SKIPPED, transform still runs.
        @task(depends_on=[extract])
        async def audit_fail(ctx: Ctx) -> None:
            raise RuntimeError("audit found a problem")

        @task(depends_on=[transform, audit_fail])
        async def load2(ctx: Ctx) -> None:
            ctx["loaded2"] = True

        ctx2: Ctx = {}
        report2 = await run_workflow([extract, transform, audit_fail, load2], ctx2)
        assert report2["extract"] is TaskStatus.SUCCEEDED
        assert report2["transform"] is TaskStatus.SUCCEEDED   # unrelated branch ran
        assert report2["audit_fail"] is TaskStatus.FAILED
        assert report2["load2"] is TaskStatus.SKIPPED
        assert "loaded2" not in ctx2
        print("failure path:", dict(report2))

        # Cycle detection with the cycle path in the message.
        a = Task(fn=extract.fn, name="a")
        b = Task(fn=extract.fn, depends_on=(a,), name="b")
        a.depends_on = (b,)  # a -> b -> a
        try:
            await run_workflow([a, b], {})
        except RecursionError:
            raise AssertionError("cycle not detected before recursion")
        except CycleError as exc:
            print(f"cycle detected: {exc}")
            assert exc.path[0] == exc.path[-1]

    asyncio.run(main())
    print("ok")
