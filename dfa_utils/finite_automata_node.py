from typing import Callable, Dict, List, Optional, Self, Set, Tuple, Any


# modified version of https://stackoverflow.com/a/6798042
class ParameterizedSingleton(type):
    _table: Dict[Tuple, Self] = {}
    def __call__(cls, *args: Any) -> Any:
        if args not in cls._table:
            cls._table[args] = super(ParameterizedSingleton, cls).__call__(*args)
        return cls._table[args]


# Since transitions only stores a function, cache them using singleton pattern could save time & space
class Transition(metaclass=ParameterizedSingleton):
    def __call__(self, *_: Any) -> bool:
        raise NotImplementedError()


# enum Transition {
#   EpsilonTransition,
#   CharTransition(char)
# }
#
# impl Fn<Args> for EpsilonTransition
class EpsilonTransition(Transition):
    def __call__(self, *_: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return "-ϵ>"


# impl Fn<Args> for CharTransition
class CharTransition(Transition):
    def __init__(self, c: str) -> None:
        assert len(c) == 1
        self.c = c

    def __call__(self, c: str, *_: Any) -> bool:
        return self.c == c

    def __repr__(self) -> str:
        return "-%s>" % self.c


class FiniteAutomataNode(object):

    def __init__(self) -> None:
        self.successors: List[Tuple[Transition, "FiniteAutomataNode"]] = []

    def add_edge(self, cond: Transition, other: "FiniteAutomataNode") -> None:
        self.successors.append((cond, other))


def test_epsilon_transition():
    a = EpsilonTransition()
    b = EpsilonTransition()
    assert a is b


def test_char_transition():
    a = CharTransition("a")
    b = CharTransition("a")
    assert a is b
    c = CharTransition("b")
    d = CharTransition("b")
    assert c is d
    assert a is not c
    e = CharTransition("a")
    assert a is e

