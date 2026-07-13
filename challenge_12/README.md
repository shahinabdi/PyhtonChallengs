# Challenge 12 — Study Checklist

To solve this challenge, you should understand:
- The descriptor protocol: `__get__`, `__set__`, `__delete__`
- `__set_name__` and when Python calls it
- Data vs non-data descriptors and attribute lookup precedence
- Why descriptor state must live in the instance `__dict__`, not on the descriptor
- The `obj is None` convention for class-level access
- How `property` relates to descriptors
