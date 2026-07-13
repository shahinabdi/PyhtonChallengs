"""Challenge 29 — Repository + Unit of Work with staged commits."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any


@dataclass
class Entity:
    id: int
    name: str


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, entity: Entity) -> None: ...

    @abstractmethod
    def get(self, entity_id: int) -> Entity | None: ...


class InMemoryRepository(AbstractRepository):
    """Two-layer storage: `_committed` is durable, `_staged` collects the
    current transaction. Reads see staged-over-committed (read-your-own-
    writes); commit merges staged down; rollback just drops it."""

    def __init__(self) -> None:
        self._committed: dict[int, Entity] = {}
        self._staged: dict[int, Entity] = {}

    def add(self, entity: Entity) -> None:
        self._staged[entity.id] = entity

    def get(self, entity_id: int) -> Entity | None:
        if entity_id in self._staged:
            return self._staged[entity_id]
        return self._committed.get(entity_id)

    def commit(self) -> None:
        self._committed.update(self._staged)
        self._staged.clear()

    def rollback(self) -> None:
        self._staged.clear()


class UnitOfWork:
    """Context manager: commits on clean exit, rolls back on exception."""

    def __init__(self, repo: InMemoryRepository) -> None:
        self.repo = repo

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self.repo.commit()
        else:
            self.repo.rollback()
        return False  # never swallow the business exception


if __name__ == "__main__":
    repo = InMemoryRepository()

    # Happy path: clean exit -> commit.
    with UnitOfWork(repo) as uow:
        uow.repo.add(Entity(1, "ada"))
        uow.repo.add(Entity(2, "bob"))
        assert uow.repo.get(1).name == "ada"   # read-your-own-writes
    assert repo.get(1) is not None and repo.get(2) is not None

    # Failure path: the exception rolls the staged change back.
    try:
        with UnitOfWork(repo) as uow:
            uow.repo.add(Entity(3, "eve"))
            assert uow.repo.get(3) is not None  # visible inside the UoW...
            raise RuntimeError("business rule violated")
    except RuntimeError as exc:
        print(f"transaction aborted: {exc}")

    assert repo.get(3) is None                  # ...gone after rollback
    assert repo.get(1).name == "ada"            # earlier commit untouched
    print("ok")
