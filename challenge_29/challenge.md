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
