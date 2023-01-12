import operator

from parse import Callbacks, parse

NodeValue = object


def eval_lisp(e: str) -> NodeValue:
    """
    Evaluate a lisp expression.
    """
    return parse(e, EvalCallback())


def test_eval_lisp():
    assert eval_lisp("(add 1 1)") == 2
    assert eval_lisp("(nth (list 1 (+ 2 3) 9) 1)") == 5


class EvalCallback(Callbacks[NodeValue]):
    """
    Callbacks which eval the expressions eagerly.
    """

    def on_integer(self, value: int) -> NodeValue:
        return value

    def on_float(self, value: float) -> NodeValue:
        return value

    def on_boolean(self, value: bool) -> NodeValue:
        return value

    def on_string(self, value: str) -> NodeValue:
        return value

    def on_symbol(self, value: str) -> NodeValue:
        if value not in SYMBOL_TABLE:
            raise ValueError(f"Unknown symbol: {value}")
        return SYMBOL_TABLE[value]

    def on_list(self, values: list[NodeValue]) -> NodeValue:
        fn, *args = values
        return fn(*args)  # type: ignore


SYMBOL_TABLE = {
    "list": lambda *args: list(args),
    "add": operator.add,
    "nth": operator.getitem,
    "+": operator.add,
}
