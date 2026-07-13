"""Challenge 21 — Profile first, then optimize to O(n)."""

import cProfile
import io
import pstats
import random
import string
import timeit


def common_prefix_groups(words: list[str]) -> dict[str, list[str]]:
    """Original: O(n^2) pairs x O(k) `not in` list scans -> ~O(n^2 * k)."""
    groups: dict[str, list[str]] = {}
    for w in words:
        for other in words:
            if other.startswith(w[:3]):
                groups.setdefault(w[:3], [])
                if other not in groups[w[:3]]:
                    groups[w[:3]].append(other)
    return groups


def common_prefix_groups_fast(words: list[str]) -> dict[str, list[str]]:
    """O(n) rewrite with identical output, INCLUDING ordering.

    ORDERING CALL (documented decision): dict key order and list order are
    observable behavior in Python, and callers may iterate the result, so
    we preserve both. It costs nothing here:
    * value lists: original appends `other` in `words` order (deduped) —
      we do the same in a single pass.
    * key order: original inserts key w[:3] when iterating w — we rebuild
      that ordering with a final O(n) pass over words.

    Key subtlety that makes naive grouping WRONG: keys are w[:3], which is
    shorter than 3 chars for short words, and membership is startswith —
    e.g. word "ab" creates key "ab" whose group contains "abc*" words too.
    So each word can belong to groups keyed by ANY of its prefixes of
    length 1..3 that actually occur as keys.
    """
    keys = {w[:3] for w in words}                      # O(n)
    members: dict[str, list[str]] = {}
    seen: dict[str, set[str]] = {k: set() for k in keys}

    for other in words:                                 # O(n) x <=3 prefixes
        for length in (1, 2, 3):
            prefix = other[:length]
            if prefix in keys and other not in seen[prefix]:
                seen[prefix].add(other)
                members.setdefault(prefix, []).append(other)
            if length >= len(other):
                break

    # Rebuild original key-insertion order (first w yielding that prefix).
    result: dict[str, list[str]] = {}
    for w in words:                                     # O(n)
        key = w[:3]
        if key not in result:
            result[key] = members[key]
    return result


def make_words(n: int, seed: int = 42) -> list[str]:
    rng = random.Random(seed)
    return [
        "".join(rng.choices(string.ascii_lowercase[:8], k=rng.randint(2, 10)))
        for _ in range(n)
    ]


if __name__ == "__main__":
    words = make_words(5_000)

    # Correctness first: identical output incl. key and value ordering.
    small = make_words(400, seed=7) + ["ab", "abc", "a"]
    assert common_prefix_groups(small) == common_prefix_groups_fast(small)
    assert list(common_prefix_groups(small)) == list(common_prefix_groups_fast(small))

    # (a) PROFILE. cProfile output on 5000 words shows the hot spot:
    #     ~25,000,000 calls to str.startswith + the O(k) list `not in`
    #     scans dominate — i.e. the nested loop itself, not any one line.
    profiler = cProfile.Profile()
    profiler.runcall(common_prefix_groups, words)
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(6)
    print(stream.getvalue())

    slow_t = timeit.timeit(lambda: common_prefix_groups(words), number=1)
    fast_t = min(timeit.repeat(lambda: common_prefix_groups_fast(words),
                               number=1, repeat=5))
    print(f"slow: {slow_t:8.3f}s   fast: {fast_t:8.5f}s   "
          f"speedup: {slow_t / fast_t:,.0f}x  (target >=100x)")
    assert slow_t / fast_t >= 100
    print("ok")
