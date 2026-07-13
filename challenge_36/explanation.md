# Explanation — Challenge 36

## Concepts required
- Lexing (tokenizing) with regular expressions.
- Recursive-descent parsing: one function per grammar rule; precedence and associativity from call structure.
- ASTs as frozen dataclasses; evaluation via structural pattern matching.
- Union type aliases for node types.

## How the parser encodes the grammar
The grammar's *shape* is the algorithm:
- `expr := term (("+"|"-") term)*` → `expr()` calls `term()`, then loops on `+`/`-`. Because `expr` can only combine **terms**, and `term()` fully consumes `2 * 3` before returning, `1 + 2 * 3` groups as `1 + (2*3)` — **precedence falls out of the call hierarchy**, no precedence table needed.
- The `while` loops make operators **left-associative**: `10 - 4 - 3` builds `((10-4)-3)`, verified in the tests — a detail naive implementations get wrong.
- `factor` handles the recursion for parentheses: `"("` → recurse into `expr()` → require `")"`. This is where the grammar is genuinely recursive.
- End-of-input handling: `evaluate` checks for trailing tokens (`"1 2"` must fail), and `take()` raises on premature end (`"1 +"`).

## The two-layer refactor
`_AstParser` subclasses the parser and changes only the *actions*: where version 1 computed `value += ...`, version 2 constructs `BinOp("+", node, right)`. The traversal logic is identical — demonstrating that parsing (syntax → structure) and evaluation (structure → value) are separable concerns. Payoffs:
- The AST is **inspectable and testable** (`tree == BinOp("+", Num(1), BinOp("*", ...))`).
- New consumers reuse the same tree: a pretty-printer, an optimizer (constant folding), a compiler — none re-parse.
- `eval_ast` with `match` reads like the semantics spec: `case BinOp("+", left, right): return eval(left) + eval(right)`. Class patterns destructure dataclasses positionally (dataclasses generate `__match_args__` automatically).

## Alternatives and trade-offs
- Pratt (precedence-climbing) parsing scales better to many precedence levels; recursive descent mirrors the given grammar most directly.
- The shunting-yard algorithm produces RPN without recursion — a classic, but less extensible to real languages.
- `ast.literal_eval` or `eval` are non-answers: the point is owning the machinery. (Never `eval` untrusted input.)

## Python features used
- **`re.compile` + `match(src, pos)` scanning**, **frozen dataclasses**, **PEP 695 union alias** (`type Expr = Num | BinOp`), **`match` class patterns with positional capture**, inheritance to swap rule actions.
