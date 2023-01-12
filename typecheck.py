import operator
import types
from typing import Callable

from parse import Callbacks, parse

NodeValue = type | Callable


def typecheck_lisp(e: str) -> NodeValue:
    """
    Evaluate a lisp expression.
    """
    return parse(e, TypecheckCallback())


def test_eval_lisp():
    assert typecheck_lisp("(add 1 1)") == int
    assert typecheck_lisp("(nth (list 1 (add 2 3) 9) 1)") == int
    assert typecheck_lisp("(list 's')") == list[str]
    typecheck_lisp("(list 'd' 2 3)")


class TypecheckCallback(Callbacks[NodeValue]):
    """
    Callbacks which eval the expressions eagerly.
    """

    def on_integer(self, value: int) -> NodeValue:
        return int

    def on_float(self, value: float) -> NodeValue:
        return float

    def on_boolean(self, value: bool) -> NodeValue:
        return bool

    def on_string(self, value: str) -> NodeValue:
        return str

    def on_symbol(self, value: str) -> NodeValue:
        if value not in SYMBOL_TABLE:
            raise ValueError(f"Unknown symbol: {value}")
        return SYMBOL_TABLE[value] #type: ignore

    def on_list(self, values: list[NodeValue]) -> NodeValue:
        fn, *args = values
        return fn(*args)  # type: ignore


def add_type(a, b):
    assert a == int
    assert b == int
    return int


def nth_type(lst, index):
    assert index == int
    assert isinstance(lst, types.GenericAlias)
    assert lst.__origin__ == list
    return lst.__args__[0]


def list_type(*args):
    assert len(set(args)) == 1
    return list[args[0]]


SYMBOL_TABLE = {
    "list": list_type,
    "add": add_type,
    "nth": nth_type,
}
