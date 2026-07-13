"""Challenge 08 — Typed **kwargs with TypedDict + Unpack (PEP 692)."""

from typing import NotRequired, Required, TypedDict, Unpack


class ContainerSpec(TypedDict):
    # total=True is the default, so plain keys are already required;
    # Required[...] is spelled out here for teaching clarity.
    image: Required[str]
    cpu: NotRequired[float]
    memory_mb: NotRequired[int]
    env: NotRequired[dict[str, str]]


def create_container(**kwargs: Unpack[ContainerSpec]) -> str:
    """Only `image` MUST be supplied by the caller; the NotRequired keys
    may be omitted entirely (that's why .get with defaults stays correct).
    A type checker rejects create_container(cpu=2.0) — missing `image` —
    and create_container(image="x", cpus=4) — unknown key."""
    image = kwargs["image"]
    cpu = kwargs.get("cpu", 1.0)
    memory_mb = kwargs.get("memory_mb", 512)
    env = kwargs.get("env", {})

    env_str = ",".join(f"{k}={v}" for k, v in env.items()) or "-"
    return f"container[image={image} cpu={cpu} mem={memory_mb}MB env={env_str}]"


if __name__ == "__main__":
    print(create_container(image="python:3.12"))
    print(
        create_container(
            image="redis:7",
            cpu=2.0,
            memory_mb=1024,
            env={"MAXMEMORY": "512mb"},
        )
    )

    # These would be flagged by mypy/pyright (runtime doesn't enforce them):
    #   create_container(cpu=2.0)               # error: missing required "image"
    #   create_container(image="x", cpus=4)     # error: unexpected key "cpus"
    #   create_container(image="x", cpu="two")  # error: wrong value type
    print("ok")
