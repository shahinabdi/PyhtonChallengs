# Challenge 36 — Study Checklist

To solve this challenge, you should understand:
- Lexing with regular expressions (`re.match` with a position)
- Grammar notation (BNF-ish) and how rules map to functions
- Recursive-descent parsing; precedence via call hierarchy
- Left associativity and why the loop (not recursion) provides it
- Frozen dataclasses as AST nodes; `__match_args__`
- `match`/`case` class patterns for tree evaluation
- Union type aliases (`type Expr = Num | BinOp`)
- Error handling: unexpected tokens, premature end, trailing input
