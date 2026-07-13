# Challenge 29 — Study Checklist

To solve this challenge, you should understand:
- The Repository pattern and why domains depend on abstractions
- The Unit of Work pattern and transaction boundaries
- `abc.ABC` and `@abstractmethod`
- Context managers: commit-on-clean-exit / rollback-on-exception in `__exit__`
- Staged (pending) vs committed state; read-your-own-writes
- Why `__exit__` must not swallow the exception
- How this maps to real ORMs (SQLAlchemy session/flush/commit)
