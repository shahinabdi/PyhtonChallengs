# Explanation — Challenge 08

## Concepts required
- `TypedDict`: static typing for dict shapes.
- `Required` / `NotRequired` per-key markers (PEP 655).
- `Unpack[SomeTypedDict]` on `**kwargs` (PEP 692) — typing keyword arguments as a whole.

## Why this approach is correct
Bare `**kwargs` erases all information: callers can't discover the accepted keys, typos (`cpus=4`) pass silently and either crash later or get ignored, and `kwargs["image"]` is a hidden required argument that fails with `KeyError` at runtime.

`def create_container(**kwargs: Unpack[ContainerSpec])` tells the type checker: "the keyword arguments, taken together, must form a `ContainerSpec`." Which keys must a caller supply? **Only `image`** — it's `Required`. `cpu`, `memory_mb`, and `env` are `NotRequired`: callers may omit them, which is precisely why the function body keeps `.get(key, default)` — the defaults live in the function, not in the type.

The checker now enforces, at every call site:
- `image` present (missing → error),
- no unknown keys (typo `cpus` → error),
- correct value types (`cpu="two"` → error).

Runtime behavior is unchanged — `TypedDict` and `Unpack` impose zero runtime cost or validation; they are purely static.

## Alternatives and trade-offs
- **Explicit keyword-only parameters** (`def create_container(*, image: str, cpu: float = 1.0, ...)`) are usually *better* — defaults are visible in the signature and runtime enforces required args. `Unpack` earns its keep when kwargs must be forwarded through wrapper layers (`def wrapper(**kw: Unpack[ContainerSpec]): return create_container(**kw)`), which plain signatures can't express.
- A `dataclass` config object is another option, but changes every call site.
- Note the subtlety: on a `total=True` TypedDict plain keys are already `Required`; `NotRequired` is what does the real work here. (On `total=False`, the roles invert.)

## Python features used
- **`TypedDict`**, **`Required` / `NotRequired`** (PEP 655), **`Unpack`** on `**kwargs` (PEP 692).
