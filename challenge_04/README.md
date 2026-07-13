# Challenge 04 — Study Checklist

To solve this challenge, you should understand:
- `enum.Enum` (and when `IntEnum` / `StrEnum` are better fits)
- Why integer constants are fragile compared to enums
- `match` value patterns (dotted names) vs capture patterns (bare names)
- `typing.Never` — the empty/bottom type
- `typing.assert_never` and static exhaustiveness checking
- How type checkers narrow an enum type across `case` arms
