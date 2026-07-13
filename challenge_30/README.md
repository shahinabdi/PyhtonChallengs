# Challenge 30 — Study Checklist

To solve this challenge, you should understand:
- The observer/event-bus pattern and its memory-leak failure mode
- `weakref.ref` and dereferencing (`ref()` → object or `None`)
- Why bound methods need `weakref.WeakMethod`
- Why lambdas/closures die instantly under weak references
- `ExceptionGroup` and `except*` (PEP 654)
- Iteration-during-mutation bugs and the snapshot idiom
- Lazy pruning of dead references
