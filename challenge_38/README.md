# Challenge 38 — Study Checklist

To solve this challenge, you should understand:
- What a metaclass is (classes as instances of `type`)
- `type.__new__(mcls, name, bases, namespace)` and when it runs
- Mutating the class namespace before type creation
- Class keyword arguments reaching the metaclass
- Method wrapping with `functools.wraps`
- Regex `re.sub` with groups/backreferences (snake_case conversion)
- Metaclass vs `__init_subclass__` vs class decorator — the escalation ladder
- Metaclass conflicts in multiple inheritance
