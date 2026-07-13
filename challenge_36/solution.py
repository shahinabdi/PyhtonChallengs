"""Challenge 36 — Tokenizer + recursive descent, then AST + match.

Grammar:  expr   := term (("+"|"-") term)*
          term   := factor (("*"|"/") factor)*
          factor := NUMBER | "(" expr ")"
"""

import re
from dataclasses import dataclass

# ---- lexer ----------------------------------------------------------------
_TOKEN_RE = re.compile(r"\s*(?:(\d+\.?\d*)|([+\-*/()]))")


def tokenize(src: str) -> list[str]:
    tokens: list[str] = []
    pos = 0
    while pos < len(src):
        m = _TOKEN_RE.match(src, pos)
        if m is None:
            raise SyntaxError(f"unexpected character {src[pos]!r} at {pos}")
        tokens.append(m.group(1) or m.group(2))
        pos = m.end()
    return tokens


# ---- version 1: direct recursive-descent evaluation ------------------------
class _Parser:
    """One method per grammar rule; precedence comes from the call
    structure itself: expr calls term calls factor, so * / bind tighter."""

    def __init__(self, tokens: list[str]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise SyntaxError("unexpected end of input")
        self.pos += 1
        return token

    def expr(self) -> float:
        value = self.term()
        while self.peek() in ("+", "-"):
            if self.take() == "+":
                value += self.term()
            else:
                value -= self.term()
        return value

    def term(self) -> float:
        value = self.factor()
        while self.peek() in ("*", "/"):
            if self.take() == "*":
                value *= self.factor()
            else:
                value /= self.factor()
        return value

    def factor(self) -> float:
        token = self.take()
        if token == "(":
            value = self.expr()
            if self.take() != ")":
                raise SyntaxError("expected ')'")
            return value
        try:
            return float(token)
        except ValueError:
            raise SyntaxError(f"expected a number, got {token!r}") from None


def evaluate(tokens: list[str]) -> float:
    parser = _Parser(tokens)
    result = parser.expr()
    if parser.peek() is not None:
        raise SyntaxError(f"trailing input from {parser.peek()!r}")
    return result


# ---- version 2: parse to an AST, then evaluate with match -------------------
@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"


type Expr = Num | BinOp


class _AstParser(_Parser):
    """Same grammar walk, but each rule BUILDS a node instead of computing.
    Only the 'what to do at each step' changes — that's the layering."""

    def expr(self) -> Expr:  # type: ignore[override]
        node = self.term()
        while self.peek() in ("+", "-"):
            node = BinOp(self.take(), node, self.term())
        return node

    def term(self) -> Expr:  # type: ignore[override]
        node = self.factor()
        while self.peek() in ("*", "/"):
            node = BinOp(self.take(), node, self.factor())
        return node

    def factor(self) -> Expr:  # type: ignore[override]
        token = self.take()
        if token == "(":
            node = self.expr()
            if self.take() != ")":
                raise SyntaxError("expected ')'")
            return node
        try:
            return Num(float(token))
        except ValueError:
            raise SyntaxError(f"expected a number, got {token!r}") from None


def parse(tokens: list[str]) -> Expr:
    parser = _AstParser(tokens)
    tree = parser.expr()
    if parser.peek() is not None:
        raise SyntaxError(f"trailing input from {parser.peek()!r}")
    return tree


def eval_ast(node: Expr) -> float:
    match node:
        case Num(value):
            return value
        case BinOp("+", left, right):
            return eval_ast(left) + eval_ast(right)
        case BinOp("-", left, right):
            return eval_ast(left) - eval_ast(right)
        case BinOp("*", left, right):
            return eval_ast(left) * eval_ast(right)
        case BinOp("/", left, right):
            return eval_ast(left) / eval_ast(right)
        case _:
            raise TypeError(f"unknown node: {node!r}")


def evaluate_via_ast(tokens: list[str]) -> float:
    return eval_ast(parse(tokens))


if __name__ == "__main__":
    cases = {
        "1 + 2 * 3": 7.0,                 # precedence
        "(1 + 2) * 3": 9.0,               # parentheses
        "10 - 4 - 3": 3.0,                # left associativity
        "8 / 4 / 2": 1.0,
        "2 * (3 + 4) - 5 / (1 + 1)": 11.5,
        "42": 42.0,
        "3.5 * 2": 7.0,
    }
    for src, expected in cases.items():
        tokens = tokenize(src)
        assert evaluate(tokens) == expected, (src, evaluate(tokens))
        assert evaluate_via_ast(tokens) == expected
        print(f"{src:28s} = {expected}")

    # The AST itself is inspectable — the payoff of the two-layer design.
    tree = parse(tokenize("1 + 2 * 3"))
    assert tree == BinOp("+", Num(1.0), BinOp("*", Num(2.0), Num(3.0)))

    for bad in ["1 +", "(1 + 2", "1 $ 2", "1 2"]:
        try:
            evaluate_via_ast(tokenize(bad))
        except SyntaxError as exc:
            print(f"rejected {bad!r}: {exc}")
    print("ok")
