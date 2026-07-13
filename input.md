# Python — 40 Challenges (Intermediate → Expert)

Difficulty rises gradually. No solutions included. Complete or rewrite the marked sections.

---

### 01 — Modernize String Formatting and Path Handling
Legacy 3.6-era code using `os.path` and `%`-formatting.
```python
import os

def build_report_path(base_dir, user, year):
    filename = "report_%s_%d.txt" % (user, year)
    full = os.path.join(base_dir, "reports", filename)
    if not os.path.exists(os.path.dirname(full)):
        os.makedirs(os.path.dirname(full))
    return full
```
**Complete:** Rewrite using `pathlib.Path` and f-strings. Add full type hints. Preserve behavior exactly (including directory creation semantics).

---

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

---

### 03 — Dict Dispatch → Structural Pattern Matching
```python
def handle_event(event: dict):
    kind = event.get("type")
    if kind == "deploy":
        if event.get("env") == "prod" and event.get("approved"):
            return f"deploying {event['service']} to prod"
        return "deploy blocked"
    elif kind == "rollback":
        return f"rolling back {event.get('service', 'unknown')}"
    elif kind == "scale":
        n = event.get("replicas")
        if isinstance(n, int) and n > 0:
            return f"scaling to {n}"
    return "ignored"
```
**Complete:** Rewrite with `match`/`case` using mapping patterns, guards, and capture patterns. Every branch above must be represented. Add a `case _` fallback.

---

### 04 — Enum + Exhaustive Handling
```python
STATE_PENDING = 0
STATE_RUNNING = 1
STATE_DONE = 2
STATE_FAILED = 3

def describe(state):
    if state == 0:
        return "waiting"
    # ... incomplete
```
**Complete:** Define a proper `enum.Enum` (or `StrEnum`), rewrite `describe` with `match`, and make the code fail loudly (e.g., `assert_never`-style using `typing.Never`) if a new enum member is added but not handled.

---

### 05 — Type Hints for a Generic Container (3.12 syntax)
```python
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def peek(self):
        return self._items[-1] if self._items else None
```
**Complete:** Make `Stack` generic using Python 3.12's `class Stack[T]:` syntax. Annotate all methods, including the `T | None` return. Add `__len__` and `__iter__` with correct annotations.

---

### 06 — Walrus, Comprehensions, and Generator Hygiene
```python
def first_long_lines(path, limit):
    results = []
    f = open(path)
    lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 80:
            results.append(stripped)
            if len(results) == limit:
                break
    f.close()
    return results
```
**Complete:** Rewrite as a lazy generator function that never loads the whole file, uses a `with` block, and uses the walrus operator where it genuinely improves the code. Then write a one-line call site that materializes at most `limit` items using `itertools.islice`.

---

### 07 — Keyword-Only and Positional-Only Parameters
```python
def transfer(source, dest, amount, currency, dry_run, audit):
    ...
```
Call sites keep breaking because arguments are passed positionally in the wrong order.
**Complete:** Redesign the signature so `source`/`dest` are positional-only, `amount` may be either, and everything else is keyword-only with sensible defaults. Add type hints and a `TypedDict` or dataclass for the return value describing the transfer result.

---

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

---

### 09 — Write a Parameterized Retry Decorator
```python
import functools, time

def retry(times: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # TODO: attempt fn up to `times` times,
            # sleeping `delay` (exponential backoff) between failures,
            # re-raising the last exception if all attempts fail.
            ...
        return wrapper
    return decorator
```
**Complete:** Implement the wrapper body. Then add a second version that also works on `async def` functions — the decorator must detect coroutine functions and dispatch accordingly.

---

### 10 — Context Manager Two Ways
```python
class Timer:
    """Measures elapsed wall time of a block and stores it in .elapsed"""
    # TODO
```
**Complete:** (a) Implement `Timer` as a class with `__enter__`/`__exit__`, ensuring `.elapsed` is set even if the block raises. (b) Implement the same as a generator with `@contextlib.contextmanager` — decide how to expose `.elapsed` given the generator form. (c) Make the class version *reentrant-safe or explicitly not* — document your choice in a docstring.

---

### 11 — ExitStack for Dynamic Resource Acquisition
```python
def open_all(paths: list[str]):
    """Open every file; if ANY open fails, close the ones already opened,
    then re-raise. On success return the list of file objects."""
    handles = []
    # TODO (without ExitStack this is fiddly — use contextlib.ExitStack)
```
**Complete:** Implement with `ExitStack`, including the success case where ownership of the open files transfers to the caller (`pop_all`).

---

### 12 — A Descriptor for Validated Fields
```python
class Bounded:
    """Descriptor enforcing min <= value <= max on instances."""
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __set_name__(self, owner, name):
        ...  # TODO: store the attribute name

    def __get__(self, obj, objtype=None):
        ...  # TODO: instance lookup; return self when accessed on the class

    def __set__(self, obj, value):
        ...  # TODO: validate and store per-instance (no shared state!)

class Thermostat:
    celsius = Bounded(-30, 60)
```
**Complete:** Implement the three methods. Store values in the instance `__dict__` under a private name. Raise `ValueError` with a message that includes the attribute name.

---

### 13 — Cached Property from Scratch
```python
class lazy_property:
    """Like functools.cached_property: compute once, then behave
    like a plain attribute (no recomputation, no __set__)."""
    def __init__(self, fn):
        ...
    # TODO
```
**Complete:** Implement using the non-data-descriptor trick (only `__get__`, plus `__set_name__`). Explain in a comment *why* the absence of `__set__` makes subsequent accesses skip the descriptor.

---

### 14 — Slots, Memory, and Inheritance
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Point3D(Point):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z
```
**Complete:** Add `__slots__` to both classes correctly (no duplicated slots, no accidental `__dict__`). Then write a small script using `sys.getsizeof` + `tracemalloc` that demonstrates the memory difference for 1M instances. Note one feature you lose with slots.

---

### 15 — Sync → Async: HTTP-ish Fan-out
```python
import time

def fetch(url: str) -> str:
    time.sleep(0.2)          # pretend network I/O
    return f"body-of-{url}"

def crawl(urls: list[str]) -> dict[str, str]:
    return {u: fetch(u) for u in urls}
```
**Complete:** Convert to `async` using `asyncio` (`asyncio.sleep` as the stand-in). `crawl` must run all fetches concurrently with `asyncio.TaskGroup` (3.11+), preserve the url→body mapping, and cap concurrency at 5 simultaneous fetches with an `asyncio.Semaphore`.

---

### 16 — Async Timeouts and Cancellation
```python
async def fetch_with_fallback(primary: str, fallback: str) -> str:
    # TODO:
    # 1. Try fetching `primary` with a 1.0s timeout (asyncio.timeout).
    # 2. On timeout, fetch `fallback` instead (no timeout).
    # 3. If the caller cancels this coroutine, the cancellation must
    #    propagate — do NOT swallow CancelledError.
    ...
```
**Complete:** Implement the body. Then explain in a comment why `except Exception` would be safe here but a bare `except` would break cancellation in versions before 3.8 — and what changed since.

---

### 17 — Producer/Consumer with asyncio.Queue
```python
import asyncio

async def producer(q: asyncio.Queue, items: list[str]) -> None:
    ...  # put items, then signal completion

async def consumer(q: asyncio.Queue, results: list[str]) -> None:
    ...  # consume until told to stop; append processed items

async def main(items: list[str], n_consumers: int = 3) -> list[str]:
    ...  # wire it together; must terminate cleanly with no hanging tasks
```
**Complete:** Implement all three. Choose and justify (in a comment) a shutdown strategy: sentinel values vs `q.join()` + `task.cancel()`.

---

### 18 — Bridging Sync and Async Worlds
```python
def blocking_hash(path: str) -> str:
    """CPU+IO heavy: reads a file and hashes it. Cannot be made async."""
    ...

async def hash_many(paths: list[str]) -> dict[str, str]:
    # TODO: run blocking_hash for all paths WITHOUT blocking the event loop.
    ...
```
**Complete:** Implement using `asyncio.to_thread` (or `loop.run_in_executor` with a `ProcessPoolExecutor` — pick one and justify the choice for CPU-bound vs IO-bound work in a comment).

---

### 19 — Async Iterator + Async Context Manager
```python
class Paginator:
    """Async-iterates over pages from a fake API, and is also an async
    context manager that "opens" and "closes" a session."""
    def __init__(self, total_pages: int):
        self.total_pages = total_pages
    # TODO: __aenter__, __aexit__, __aiter__, __anext__
```
**Complete:** Implement so this works:
```python
async with Paginator(3) as p:
    async for page in p:
        print(page)
```
`__anext__` must raise the correct exception at the end. Then rewrite the iteration part as an async generator method and compare.

---

### 20 — Threading vs Asyncio vs Multiprocessing: Choose and Implement
```python
def cpu_task(n: int) -> int:      # pure CPU, ~0.5s each
    return sum(i * i for i in range(n))

def io_task(path: str) -> bytes:  # pure disk IO
    with open(path, "rb") as f:
        return f.read()
```
**Complete:** Write `run_all(cpu_jobs, io_jobs)` that executes 8 CPU tasks and 50 IO tasks with the *appropriate* concurrency model for each (given the GIL), combines the results, and returns them. Add a comment stating expected speedup for each half and why.

---

### 21 — Profile First, Then Optimize
```python
def common_prefix_groups(words: list[str]) -> dict[str, list[str]]:
    groups = {}
    for w in words:
        for other in words:
            if other.startswith(w[:3]):
                groups.setdefault(w[:3], [])
                if other not in groups[w[:3]]:
                    groups[w[:3]].append(other)
    return groups
```
**Complete:** (a) Profile with `cProfile` and `timeit` on 5,000 random words and record the hot spot. (b) Rewrite to O(n) with identical output (same keys, same membership — decide whether original ordering is part of "behavior" and document your call). Target ≥100× speedup.

---

### 22 — lru_cache Pitfalls
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def route_cost(graph: dict, start: str, end: str) -> float:
    ...
```
This raises `TypeError: unhashable type: 'dict'`.
**Complete:** Fix caching three ways and compare trade-offs in comments: (1) restructure so the graph is bound in a closure/class and only `(start, end)` is cached; (2) convert the graph to a hashable frozen form; (3) implement a small custom memoization decorator keyed on `id(graph)` + args — and state why (3) is dangerous.

---

### 23 — String Building and Interning
```python
def render_rows(rows: list[tuple[str, int]]) -> str:
    out = ""
    for name, qty in rows:
        out = out + "<tr><td>" + name + "</td><td>" + str(qty) + "</td></tr>"
    return "<table>" + out + "</table>"
```
**Complete:** Rewrite three ways — `str.join` on a generator, `io.StringIO`, and a single f-string template with `"".join` — then benchmark all four (including the original) at 100k rows and record results in a comment. Which wins and why (think allocation behavior)?

---

### 24 — Slot In a Cache Layer Without Changing Callers
```python
class UserService:
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id: int) -> "User":
        return self._db.fetch("users", user_id)   # slow

    def update_user(self, user_id: int, **fields) -> None:
        self._db.update("users", user_id, fields)
```
**Complete:** Add an in-memory TTL cache (write-through invalidation on `update_user`) *without changing the public API or the callers*. Implement it as a wrapper/proxy class implementing the same interface, plus a small `TTLCache` (dict + monotonic timestamps). Bound the cache size.

---

### 25 — Generators as Pipelines
```python
# Log lines look like: "2026-07-08T10:00:00 ERROR service=auth msg=..."
def read_lines(path): ...
def parse(lines): ...        # yield dicts
def only_errors(records): ...
def by_service(records, service): ...
```
**Complete:** Implement all four as lazy generator stages, compose them into a pipeline, and add a fifth stage `window(records, n)` that yields lists of `n` consecutive records (last window may be short) — without ever holding more than `n` records in memory.

---

### 26 — itertools Fluency
```python
from itertools import *

def chunked(iterable, size):      # [1,2,3,4,5], 2 -> [1,2],[3,4],[5]
    ...
def pairwise_deltas(nums):        # [3,7,4] -> [4,-3]
    ...
def run_lengths(s):               # "aaabbc" -> [("a",3),("b",2),("c",1)]
    ...
def round_robin(*iters):          # "AB","12","xyz" -> A1xB2yz... (order: A,1,x,B,2,y,z)
    ...
```
**Complete:** Implement each using itertools primitives (`islice`, `pairwise`, `groupby`, `cycle`, `chain`, ...) — no manual index bookkeeping, all lazy.

---

### 27 — Protocols over Inheritance
```python
class JsonExporter:
    def export(self, data: dict) -> str: ...

class CsvExporter:
    def export(self, data: dict) -> str: ...

def save_report(exporter, data):   # currently untyped
    payload = exporter.export(data)
    ...
```
**Complete:** Define an `Exporter` `typing.Protocol` (make it `@runtime_checkable`), annotate `save_report`, and add a third conforming exporter *without importing anything from the module that defines the protocol* — demonstrating structural typing. Then add a generic `Exporter[T]` variant where `export` takes `T` instead of `dict`.

---

### 28 — Strategy Pattern, Pythonic Edition
```python
class PriceCalculator:
    def calc(self, order, customer_type):
        if customer_type == "regular":
            return order.total
        elif customer_type == "member":
            return order.total * 0.9
        elif customer_type == "vip":
            base = order.total * 0.8
            return base - (5 if order.total > 100 else 0)
        # new types keep getting added here...
```
**Complete:** Refactor to a strategy registry: strategies are plain functions registered via a decorator (`@pricing_strategy("vip")`), stored in a module-level dict, looked up at call time with a clear error for unknown types. Add one new strategy to prove extension requires zero edits to `PriceCalculator`.

---

### 29 — Repository + Unit of Work Skeleton
```python
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, entity): ...
    @abstractmethod
    def get(self, entity_id): ...

class InMemoryRepository(AbstractRepository):
    ...  # TODO

class UnitOfWork:
    """Context manager: collects changes, commits on clean exit,
    rolls back on exception."""
    ...  # TODO
```
**Complete:** Implement both. The in-memory repo must support rollback (hint: stage changes, apply on commit). Write a short usage snippet showing an exception triggering rollback.

---

### 30 — Event Bus with Weak References
```python
class EventBus:
    def subscribe(self, event_type: str, handler): ...
    def unsubscribe(self, event_type: str, handler): ...
    def publish(self, event_type: str, payload): ...
```
**Complete:** Implement so that (a) handlers are held via `weakref.WeakMethod`/`weakref.ref` so a garbage-collected subscriber is auto-removed, (b) a handler raising an exception does not prevent other handlers from running (collect and re-raise as an `ExceptionGroup`), (c) publishing during publishing doesn't corrupt iteration.

---

### 31 — Plugin Architecture: Discovery + Registration
```python
# app/plugins/__init__.py
class Plugin(ABC):
    name: str
    @abstractmethod
    def run(self, ctx: dict) -> None: ...

def load_plugins(package: str) -> dict[str, Plugin]:
    """Import every module in `package`, find Plugin subclasses,
    instantiate and return them keyed by .name."""
    ...  # TODO: pkgutil.iter_modules + importlib
```
**Complete:** Implement `load_plugins`. Then add an alternative registration path using `__init_subclass__` on `Plugin` so subclasses self-register at import time, and note in comments which approach fits a third-party-plugin scenario better.

---

### 32 — Dependency Injection Without a Framework
```python
class EmailSender:
    def __init__(self):
        self.smtp = SmtpClient(host="prod-smtp")   # hard-wired!

class SignupService:
    def __init__(self):
        self.sender = EmailSender()                # hard-wired!
        self.db = PostgresDb("prod-dsn")           # hard-wired!

    def signup(self, email: str): ...
```
**Complete:** Refactor to constructor injection with `Protocol`-typed dependencies, then write a tiny composition root (`build_app(config)`) that wires prod implementations, and a test snippet that wires fakes. No DI library.

---

### 33 — Layered Architecture Enforcement
```
myapp/
  domain/models.py        # must import NOTHING from other layers
  services/signup.py      # may import domain only
  adapters/postgres.py    # may import domain + services interfaces
  api/http.py             # outermost
```
The current code has `domain/models.py` importing from `adapters/postgres.py`.
**Complete:** (a) Sketch the refactor that inverts that dependency (define the repository interface in `domain` or `services`, implement it in `adapters`). (b) Write a checker script that walks the package with `ast`, extracts imports per module, and fails with a clear message on any layering violation.

---

### 34 — Circular Imports and Module Design
```python
# order.py
from customer import Customer
class Order:
    def __init__(self, customer: Customer): ...

# customer.py
from order import Order
class Customer:
    def orders(self) -> list[Order]: ...
```
**Complete:** Fix the circular import three ways and rank them: (1) `from __future__ import annotations` / string annotations + `TYPE_CHECKING`, (2) restructuring into a shared module, (3) deferred import inside the method. State in comments which you'd choose for a growing codebase and why.

---

### 35 — Finite State Machine as a Class
```python
class Document:
    """States: draft -> review -> approved -> published
                       review -> draft (reject)
       Illegal transitions raise InvalidTransition."""
    ...  # TODO
```
**Complete:** Implement with an explicit transition table (`dict[tuple[State, Event], State]`), a `dispatch(event)` method, and per-transition hooks (`on_enter_review`, discovered via `getattr`). Use `StrEnum` for states and events. No if/elif chains.

---

### 36 — Small Interpreter: Tokenize + Evaluate
```python
# Grammar:  expr := term (("+"|"-") term)*
#           term := factor (("*"|"/") factor)*
#           factor := NUMBER | "(" expr ")"
def tokenize(src: str) -> list[str]: ...
def evaluate(tokens: list[str]) -> float: ...
```
**Complete:** Implement a recursive-descent evaluator with correct precedence and parentheses. Then refactor `evaluate` to first build an AST (dataclass nodes) and evaluate via a `match` on node types — two clean layers.

---

### 37 — `__init_subclass__` Registry with Validation
```python
class Serializer:
    """Subclasses must declare `format: str` and implement dumps().
    They auto-register into Serializer.registry keyed by format.
    Duplicate formats or missing attributes must fail AT CLASS
    DEFINITION TIME, not at first use."""
    registry: dict[str, type["Serializer"]] = {}
    ...  # TODO: __init_subclass__
```
**Complete:** Implement `__init_subclass__` with the validations above (raise `TypeError` with precise messages). Support `abstract=True` intermediate subclasses that skip registration.

---

### 38 — A Real Metaclass: Enforce Interface + Inject Behavior
```python
class ServiceMeta(type):
    """1) Every concrete class must define `handle(self, request)`.
       2) Every method whose name starts with `handle` gets wrapped
          to log call duration.
       3) Classes get an auto-generated `service_name` = snake_case
          of the class name."""
    ...  # TODO: __new__

class PaymentService(metaclass=ServiceMeta):
    def handle(self, request): ...
```
**Complete:** Implement `ServiceMeta.__new__`. Then add a short comment: which of these three features could have been done with `__init_subclass__` or a decorator instead, and what does the metaclass uniquely buy you?

---

### 39 — Descriptor + Metaclass Combo: A Mini ORM Field System
```python
class Field:
    def __init__(self, py_type: type, primary_key: bool = False): ...
    # descriptor protocol TODO

class ModelMeta(type):
    """Collect Field attributes into cls._fields (ordered),
    validate exactly one primary key, generate __init__ that
    accepts fields as kwargs with type checking."""
    ...  # TODO

class User(metaclass=ModelMeta):
    id = Field(int, primary_key=True)
    email = Field(str)
```
**Complete:** Implement `Field` (with `__set_name__`, type-validated `__set__`) and `ModelMeta`. `User(id=1, email="a@b.c")` must work; `User(id="x", ...)` must raise `TypeError`. Also generate a `to_dict()` method.

---

### 40 — Capstone: Async Task Orchestrator
Design and partially implement a mini workflow engine:
```python
@task
async def extract(ctx): ...

@task(depends_on=[extract])
async def transform(ctx): ...

@task(depends_on=[extract])
async def audit(ctx): ...

@task(depends_on=[transform, audit])
async def load(ctx): ...

await run_workflow([extract, transform, audit, load], ctx={})
```
```python
def task(fn=None, *, depends_on=()): ...   # TODO
async def run_workflow(tasks, ctx): ...    # TODO
```
**Complete:** Implement `task` (usable with and without arguments) and `run_workflow`, which must: topologically sort, detect cycles (raise with the cycle path), run independent tasks concurrently (`TaskGroup`), stop dependents if a dependency fails, and report per-task status at the end. Type-hint everything with 3.12 syntax.