"""Challenge 26 — itertools fluency: four lazy utilities."""

from collections.abc import Iterable, Iterator
from itertools import batched, cycle, groupby, islice, pairwise


def chunked[T](iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """[1,2,3,4,5], 2 -> [1,2], [3,4], [5]

    itertools.batched (3.12) does exactly this, yielding tuples;
    we map to list to match the challenge's example output.
    """
    return (list(batch) for batch in batched(iterable, size))


def chunked_islice[T](iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """Pre-3.12 spelling with islice against a shared iterator:
    each islice consumes the next `size` items from the SAME iterator."""
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk


def pairwise_deltas(nums: Iterable[float]) -> Iterator[float]:
    """[3,7,4] -> [4,-3] — consecutive differences, lazily."""
    return (b - a for a, b in pairwise(nums))


def run_lengths(s: Iterable[str]) -> Iterator[tuple[str, int]]:
    """"aaabbc" -> ("a",3), ("b",2), ("c",1) — run-length encoding.

    groupby groups CONSECUTIVE equal elements; sum(1 for _) counts the
    group lazily without materializing it.
    """
    return ((char, sum(1 for _ in group)) for char, group in groupby(s))


def round_robin[T](*iters: Iterable[T]) -> Iterator[T]:
    """"AB","12","xyz" -> A,1,x,B,2,y,z

    The classic itertools recipe: cycle over each iterator's __next__;
    when one is exhausted, shrink the cycle with islice to the remaining
    count. No index variables, fully lazy.
    """
    active = len(iters)
    nexts = cycle(iter(it).__next__ for it in iters)
    while active:
        try:
            for next_fn in nexts:
                yield next_fn()
        except StopIteration:
            active -= 1
            nexts = cycle(islice(nexts, active))


if __name__ == "__main__":
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(chunked_islice([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(chunked([], 3)) == []

    assert list(pairwise_deltas([3, 7, 4])) == [4, -3]
    assert list(pairwise_deltas([5])) == []           # <2 items -> no pairs

    assert list(run_lengths("aaabbc")) == [("a", 3), ("b", 2), ("c", 1)]
    assert list(run_lengths("")) == []
    assert list(run_lengths("aba")) == [("a", 1), ("b", 1), ("a", 1)]

    assert "".join(round_robin("AB", "12", "xyz")) == "A1xB2yz"
    assert list(round_robin()) == []
    assert "".join(round_robin("", "ab")) == "ab"

    # Laziness check: nothing above pulled from this infinite-ish source.
    def counter() -> Iterator[int]:
        n = 0
        while True:
            yield (n := n + 1)

    first_two_chunks = list(islice(chunked(counter(), 3), 2))
    assert first_two_chunks == [[1, 2, 3], [4, 5, 6]]
    print("ok")
