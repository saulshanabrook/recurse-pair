from parse import Callbacks, parse


class MyCallbacks(Callbacks):
    pass


def test():
    parse("1", MyCallbacks())
