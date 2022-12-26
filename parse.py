"""
Parse a string of Lisp code into an AST.

Supports these types of tokens:
* Integers/floats
* Strings
* Booleans
* Strings
* Symbols
"""

from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


def parse(text: str, callbacks: Callbacks[T]) -> T:
    """
    Parse a string of Lisp code into an AST.
    """
    ...


class Callbacks(Protocol[T]):
    """
    Callbacks for the parser.
    """

    def on_integer(self, value: int) -> T:
        ...

    def on_float(self, value: float) -> T:
        ...

    def on_boolean(self, value: bool) -> T:
        ...

    def on_string(self, value: str) -> T:
        ...

    def on_symbol(self, value: str) -> T:
        ...

    def on_list(self, values: list[T]) -> T:
        ...


AstNode = int | float | bool | str | list["AstNode"]


class AstCallback(Callbacks[AstNode]):
    """
    Callbacks for the parser that build an AST.
    """

    def on_integer(self, value: int) -> AstNode:
        return value

    def on_float(self, value: float) -> AstNode:
        return value

    def on_boolean(self, value: bool) -> AstNode:
        return value

    def on_string(self, value: str) -> AstNode:
        return repr(value)

    def on_symbol(self, value: str) -> AstNode:
        return value

    def on_list(self, values: list[AstNode]) -> AstNode:
        return values


def parse_ast(text: str) -> AstNode:
    """
    Parse a string of Lisp code into an AST.

    >>> parse_ast("(first (list 1 (+ 2 3) 9))")
    ['first', ['list', 1, ['+', 2, 3], 9]]
    >>> parse_ast("(list 1 True \"hello\" 'world' 3.14)")
    ['list', 1, True, "'hello'", "'world'", 3.14]
    """
    return parse(text, AstCallback())
