"""Challenge 22 — Three ways around lru_cache's hashability requirement."""

import functools
from collections.abc import Callable
from typing import Any

type Graph = dict[str, dict[str, float]]

# Shared uncached core: cheapest path cost via Dijkstra-lite (no heapq to
# keep the focus on caching, fine for small graphs).
def _route_cost(graph: Graph, start: str, end: str) -> float:
    costs = {start: 0.0}
    frontier = {start}
    while frontier:
        node = min(frontier, key=lambda n: costs[n])
        frontier.remove(node)
        if node == end:
            return costs[node]
        for neighbor, weight in graph.get(node, {}).items():
            new_cost = costs[node] + weight
            if new_cost < costs.get(neighbor, float("inf")):
                costs[neighbor] = new_cost
                frontier.add(neighbor)
    return float("inf")


# ---- Fix 1: bind the graph in a closure; cache only (start, end) -------
def make_route_cost(graph: Graph) -> Callable[[str, str], float]:
    """BEST DEFAULT. The unhashable graph never enters the cache key; each
    graph gets its own function + cache, garbage-collected together.
    Trade-off: callers must hold the returned function; caching is
    per-factory-call (two calls with the same graph -> two caches). The
    graph must not be mutated after binding — same contract as any cache."""

    @functools.cache
    def route_cost(start: str, end: str) -> float:
        return _route_cost(graph, start, end)

    return route_cost


# ---- Fix 2: freeze the graph into a hashable form -----------------------
def freeze(graph: Graph) -> frozenset[tuple[str, frozenset[tuple[str, float]]]]:
    return frozenset(
        (node, frozenset(edges.items())) for node, edges in graph.items()
    )


@functools.lru_cache(maxsize=None)
def _route_cost_frozen(
    frozen: frozenset[tuple[str, frozenset[tuple[str, float]]]],
    start: str,
    end: str,
) -> float:
    graph: Graph = {node: dict(edges) for node, edges in frozen}
    return _route_cost(graph, start, end)


def route_cost_frozen(graph: Graph, start: str, end: str) -> float:
    """Correct across *equal* graphs (value-based key: two equal graphs
    share cache entries) and immune to identity reuse. Trade-offs: freezing
    is O(graph) per call unless the caller caches the frozen form, and the
    frozen graph is retained in the cache -> memory grows with distinct
    graphs; thaw adds overhead too."""
    return _route_cost_frozen(freeze(graph), start, end)


# ---- Fix 3: memoize keyed on id(graph) — DANGEROUS ----------------------
def memo_by_graph_id(fn: Callable[..., float]) -> Callable[..., float]:
    """WHY THIS IS DANGEROUS:
    1. Stale hits after mutation: id() doesn't change when the graph's
       CONTENTS change -> mutate the graph, get yesterday's answer.
    2. id() values are REUSED after garbage collection: a dead graph's id
       can be recycled by a brand-new, different graph -> cache returns
       costs for a graph that no longer exists. (CPython reuses freed
       addresses constantly.)
    3. The cache holds no reference to the graph, only its id, so nothing
       ties entry lifetime to graph lifetime — unbounded growth AND the
       reuse bug above. Fixing that needs weakrefs + per-object caches,
       at which point you've rebuilt Fix 1 badly."""
    cache: dict[tuple[int, Any, Any], float] = {}

    @functools.wraps(fn)
    def wrapper(graph: Graph, start: str, end: str) -> float:
        key = (id(graph), start, end)
        if key not in cache:
            cache[key] = fn(graph, start, end)
        return cache[key]

    return wrapper


route_cost_by_id = memo_by_graph_id(_route_cost)


if __name__ == "__main__":
    g: Graph = {
        "a": {"b": 1.0, "c": 4.0},
        "b": {"c": 1.5, "d": 5.0},
        "c": {"d": 1.0},
        "d": {},
    }

    rc = make_route_cost(g)
    assert rc("a", "d") == 3.5
    assert rc("a", "d") == 3.5  # cache hit
    assert rc.cache_info().hits >= 1

    assert route_cost_frozen(g, "a", "d") == 3.5
    equal_copy = {k: dict(v) for k, v in g.items()}
    assert route_cost_frozen(equal_copy, "a", "d") == 3.5  # value-equal hit

    assert route_cost_by_id(g, "a", "d") == 3.5
    # Danger demo: mutate the graph -> stale answer from the id-keyed cache.
    g["a"]["d"] = 0.5
    assert _route_cost(g, "a", "d") == 0.5          # truth: 0.5
    assert route_cost_by_id(g, "a", "d") == 3.5     # stale lie: 3.5
    print("id-keyed cache served a stale result after mutation — as warned")
    print("ok")
