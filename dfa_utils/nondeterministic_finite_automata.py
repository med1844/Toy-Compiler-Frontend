from os import EX_USAGE
from typing import List, Tuple, Dict, Callable, Iterable, TypeVar, Deque
from finite_automata_node import FiniteAutomataNode
from collections import namedtuple, deque
from functools import reduce
from abc import ABC


T = TypeVar("T")


# consider this as a trait... why there's no trait in python
class RegexOperation(ABC):

    @staticmethod
    def kleene_star(r: T) -> T:
        raise NotImplementedError()
        
    @staticmethod
    def or_(l: T, r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def plus(r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def concat(l: T, r: T) -> T:
        raise NotImplementedError()


class StringRegexOperation(RegexOperation):
    # impl RegexOperation for StringRegexOperation
    # @override
    @staticmethod
    def kleene_star(r: str) -> str:
        return "(%s*)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

    @staticmethod
    def or_(l: str, r: str) -> str:
        return "(%s|%s)" % (l, r)

    @staticmethod
    def plus(r: str) -> str:
        return "(%s+)" % r

    @staticmethod
    def concat(l: str, r: str) -> str:
        return "%s->%s" % (l, r)


class NFARegexOperation(RegexOperation):
    # impl RegexOperation for NFARegexOperation
    pass


def parse(r: Deque[str], regex_operation: RegexOperation):
    ops = deque()
    or_ops = deque()

    def reduce_concat():
        l = ops.popleft()
        while ops:
            c = ops.popleft()
            l = regex_operation.concat(l, c)
        return l

    while r:
        s = r.popleft()
        if s == "(":
            ops.append(parse(r, regex_operation))
        elif s == ")":
            break
        elif s == "*":
            ops.append(regex_operation.kleene_star(ops.pop()))
        elif s == "+":
            ops.append(regex_operation.plus(ops.pop()))
        elif s == "|":
            or_ops.append(reduce_concat())
        elif len(s) == 1:
            ops.append(s)
    if ops:
        or_ops.append(reduce_concat())
    l = or_ops.popleft()
    while or_ops:
        l = regex_operation.or_(l, or_ops.popleft())
    return l


class NondeterministicFiniteAutomata(object):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        self.start_node = start_node
        self.end_node = end_node




    @classmethod
    def from_string(cls, r: str) -> "NondeterministicFiniteAutomata":
        pass


def test_parsing():
    op = StringRegexOperation()

    for regex, expected_output in (
        ("(c|d)*", "((c|d)*)"),
        ("(ab*(c|d)*)|(e|(f*g))", "(a->(b*)->((c|d)*)|(e|(f*)->g))"),
        ("a*bcc|c*dee", "((a*)->b->c->c|(c*)->d->e->e)"),
        ("ab", "a->b"),
        ("a|b", "(a|b)"),
        ("ab|cd", "(a->b|c->d)"),
        ("ab*|cd", "(a->(b*)|c->d)"),
        ("a|b*", "(a|(b*))"),
        ("((a|b)*(cc|dd))*ee", "(((a|b)*)->(c->c|d->d)*)->e->e"),
        ("ab|cd|ef", "((a->b|c->d)|e->f)"),
        ("abc|cde", "(a->b->c|c->d->e)"),
        ("ac(bc|de)|ff", "(a->c->(b->c|d->e)|f->f)")
    ):
        assert parse(deque(regex), op) == expected_output

