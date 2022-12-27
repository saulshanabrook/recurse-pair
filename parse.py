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

from dataclasses import dataclass, field
from typing import Generic, Literal, Protocol, TypeVar

T = TypeVar("T")


def parse(text: str, callbacks: Callbacks[T]) -> T:
    """
    Parse a string of Lisp code into an AST.
    """
    characters = list(text)
    res = _Parser(callbacks).parse(characters)
    if characters:
        raise ValueError(f"Unexpected remaining characters: {characters}")
    return res


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
    r"""
    Parse a string of Lisp code into an AST.

    >>> parse_ast("(first (list 1 (+ 2 3) 9))")
    ['first', ['list', 1, ['+', 2, 3], 9]]
    >>> parse_ast("(list 1 True \"hello\" 'world' 3.14)")
    ['list', 1, 'True', "'hello'", "'world'", 3.14]
    """
    return parse(text, AstCallback())


DIGITS = "0123456789"
SYMBOL_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ*-+/"


@dataclass
class _Parser(Generic[T]):
    callbacks: Callbacks[T]
    state: _State[T] = "initial"

    def parse(self, characters: list[str]) -> T:
        """
        Parse a string of Lisp code as an expression.
        """
        while characters:
            match (self.state, characters.pop(0)):
                case ("initial", " "):
                    pass
                # List
                case ("initial", "("):
                    self.state = _InList[T]()
                case (_InList(values), ")"):
                    return self.callbacks.on_list(values)
                case (_InList(values), " "):
                    pass
                case (_InList(values), c):
                    characters.insert(0, c)
                    values.append(_Parser(self.callbacks).parse(characters))
                case ("initial", d) if d in DIGITS:
                    self.state = _InDigits[T](d)
                #  Int
                case (_InDigits(value), d) if d in DIGITS:
                    self.state = _InDigits[T](value + d)
                case (_InDigits(value), " "):
                    return self.callbacks.on_integer(int(value))
                case (_InDigits(value), "."):
                    self.state = _InDecimal[T](value + ".")
                case (_InDigits(value), ")"):
                    characters.insert(0, ")")
                    return self.callbacks.on_integer(int(value))
                # Float
                case (_InDecimal(value), d) if d in DIGITS:
                    self.state = _InDecimal[T](value + d)
                case (_InDecimal(value), " "):
                    return self.callbacks.on_float(float(value))
                case (_InDecimal(value), ")"):
                    characters.insert(0, ")")
                    return self.callbacks.on_float(float(value))
                # Symbol
                case ("initial", s) if s in SYMBOL_CHARACTERS:
                    self.state = _InSymbol[T](s)
                case (_InSymbol(value), s) if s in SYMBOL_CHARACTERS:
                    self.state = _InSymbol[T](value + s)
                case (_InSymbol(value), " "):
                    return self.callbacks.on_symbol(value)
                case (_InSymbol(value), ")"):
                    characters.insert(0, ")")
                    return self.callbacks.on_symbol(value)
                # String
                case ("initial", "'"):
                    self.state = _InString[T]("", "'")
                case ("initial", '"'):
                    self.state = _InString[T]("", '"')
                case (_InString(value, '"'), '"') | (_InString(value, "'"), "'"):
                    return self.callbacks.on_string(value)
                case (_InString(value, quote_type), "\\"):
                    match characters.pop(0):
                        case '"' if quote_type == '"':
                            self.state = _InString[T](value + '"', quote_type)
                        case "'" if quote_type == "'":
                            self.state = _InString[T](value + "'", quote_type)
                        case "\\":
                            self.state = _InString[T](value + "\\", quote_type)
                        case _:
                            raise ValueError(
                                f"Unexpected character after backslash: {characters[0]}"
                            )
                case (_InString(value, quote_type), c):
                    self.state = _InString[T](value + c, quote_type)
                case (state, c):
                    raise ValueError(f"Unexpected character: {c} in state {state}")
        raise ValueError("Unexpected end of input")


_Initial = Literal["initial"]


@dataclass
class _InList(Generic[T]):
    values: list[T] = field(default_factory=list)


@dataclass
class _InDigits(Generic[T]):
    """
    After some seuence of integer digits.
    """

    value: str


@dataclass
class _InDecimal(Generic[T]):
    """
    After a decimal point.
    """

    value: str


@dataclass
class _InString(Generic[T]):
    """
    After a quote.
    """

    value: str
    quote_type: Literal["'", '"']


@dataclass
class _InSymbol(Generic[T]):
    """
    After a symbol character.
    """

    value: str


_State = (
    _Initial | _InList[T] | _InDigits[T] | _InDecimal[T] | _InString[T] | _InSymbol[T]
)
