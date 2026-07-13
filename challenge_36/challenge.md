### 36 — Small Interpreter: Tokenize + Evaluate
```python
# Grammar:  expr := term (("+"|"-") term)*
#           term := factor (("*"|"/") factor)*
#           factor := NUMBER | "(" expr ")"
def tokenize(src: str) -> list[str]: ...
def evaluate(tokens: list[str]) -> float: ...
```
**Complete:** Implement a recursive-descent evaluator with correct precedence and parentheses. Then refactor `evaluate` to first build an AST (dataclass nodes) and evaluate via a `match` on node types — two clean layers.
