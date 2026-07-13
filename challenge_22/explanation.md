# Explanation — Challenge 22

## Concepts required
- How `lru_cache` builds its key: all positional/keyword args must be hashable; `dict` isn't (mutable ⇒ unhashable by design).
- Closures as a way to exclude an argument from a cache key.
- Hashable frozen forms: `frozenset`, tuples.
- Object identity (`id()`), its lifetime rules, and why identity-keyed caches are traps.

## The three fixes

**1. Closure/factory (`make_route_cost`) — the recommended default.**
The graph is captured lexically; `functools.cache` sees only `(start, end)`. Each graph gets its own cache with a lifetime tied to the returned function — drop the function, free the cache. Costs: caching is per-factory-call (call the factory twice with the same graph and you get two independent caches), and the class-based equivalent (a `RouteFinder` class holding the graph, caching in an instance dict) may suit codebases that dislike closures. Contract: don't mutate the graph after binding — true of *every* caching scheme.

**2. Frozen form (`route_cost_frozen`).**
`frozenset[(node, frozenset(edges.items()))]` is deeply hashable, and keys are **value-based**: two structurally equal graphs share entries — the only variant with that property. Costs: O(graph) freeze on every call (amortize by having callers freeze once), thaw overhead inside, and the cache *retains* every distinct frozen graph → memory growth.

**3. `id(graph)`-keyed memo — implemented to show why it's dangerous.**
Three failure modes, demonstrated in the code:
- **Mutation staleness**: `id` is unchanged when contents change; the demo mutates the graph and the cache confidently returns the old cost.
- **Id reuse**: CPython recycles memory addresses; after the original graph is garbage-collected, a *new* graph can receive the same `id` and silently inherit the dead graph's cache entries.
- **Unbounded, untied lifetime**: the cache stores only the integer id, so entries never expire with their graph. Repairing this properly (weakrefs, per-object caches) reinvents Fix 1.

## Verdict
Prefer **(1)** for one-graph-many-queries workloads; **(2)** when value equality across graph copies matters; never ship **(3)**.

## Python features used
- **`functools.cache` / `lru_cache`**, `cache_info()`, **closures**, **`frozenset`**, **PEP 695 `type` alias** (`type Graph = ...`), `functools.wraps`.
