from typing import List, Tuple, Dict, Callable, Iterable, TypeVar, Deque
from finite_automata_node import FiniteAutomataNode
from collections import namedtuple, deque
from functools import reduce


T = TypeVar("T")


# consider this as a trait... why there's no trait in python
class RegexOperation(object):

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


def tokenize_first_layer(r: str) -> Iterable[str]:
    # only tokenize characters or subregexes that are at the highest level.
    # this helps simplifying recurring patterns inside of parentheses
    # see function `test_first_layer_tokenizer` for more examples
    layer = 0
    buffer = []
    for s in r:
        if s == "(":
            layer += 1
        if layer == 0:
            if buffer:
                yield "".join(buffer[1:-1])
                buffer.clear()
            yield s
        else:
            buffer.append(s)
        if s == ")":
            layer -= 1
    assert layer == 0
    if buffer:
        yield "".join(buffer[1:-1])
        buffer.clear()


def parse_first_layer(r: Iterable[str], regex_operation: RegexOperation):
    # regex_operation must have implemented trait RegexOperation
    # the return type also depends on the chosen regex operation...
    # Maybe it's more similar to something like RegexOperation<String>?
    operands = deque()
    # first pass, does not take binary op into consideration
    for s in r:
        if s == "*":
            operands.append(regex_operation.kleene_star(operands.pop()))
        elif s == "+":
            operands.append(regex_operation.plus(operands.pop()))
        elif len(s) == 1:
            operands.append(s)
        else:
            operands.append(parse_first_layer(tokenize_first_layer(s), regex_operation))

    # second pass, deal with or_ operands & concat
    stack = deque()  # stores temporary tokens
    concated_operands = deque()
    while operands:
        s = operands.popleft()
        if s == "|":
            l = reduce(regex_operation.concat, stack, stack.popleft())
            stack.clear()
            concated_operands.append(l)
        else:
            stack.append(s)
    l = reduce(regex_operation.concat, stack, stack.popleft())
    stack.clear()
    concated_operands.append(l)

    assert len(concated_operands) == 1
    return concated_operands.popleft()

class NondeterministicFiniteAutomata(object):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        self.start_node = start_node
        self.end_node = end_node




    @classmethod
    def from_string(cls, r: str) -> "NondeterministicFiniteAutomata":
        pass


def test_first_layer_tokenizer():
    for regex, expected_output in (
        ("ab", ["a", "b"]),
        ("a|b", ["a", "|", "b"]),
        ("ab|cd", ["a", "b", "|", "c", "d"]),
        ("(ab*(c|d)*)|(e|(f*g))", ["ab*(c|d)*", "|", "e|(f*g)"]),
        ("(a|b)*abb(ϵ|a|b)*", ["a|b", "*", "a", "b", "b", "ϵ|a|b", "*"]),
        ("(a|b)c*d", ["a|b", "c", "*", "d"]),
        ("(c|d)*", ["c|d", "*"]),
    ):
        assert list(tokenize_first_layer(regex)) == expected_output


def test_first_layer_parser():
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
        assert parse_first_layer(tokenize_first_layer(regex), op) == expected_output


if __name__ == "__main__":
    test_first_layer_tokenizer()
    test_first_layer_parser()
    # def rebuild_infix(p: List[str]) -> str:
    #     stack = []
    #     for c in p:
    #         if c == "*":
    #             stack.append("(%s*)" % (stack.pop()))
    #         elif c == "|":
    #             r = stack.pop()
    #             l = stack.pop()
    #             stack.append("(%s|%s)" % (l, r))
    #         elif c == "+":
    #             r = stack.pop()
    #             l = stack.pop()
    #             stack.append("(%s+%s)" % (l, r))
    #         else:
    #             stack.append(c)
    #
    #     return stack.pop()
    #
    #
    # for regex, target_lisp in (
    #     ("ab", "ab"),
    #     ("a|b", "(a|b)"),
    #     ("ab|cd", "(ab|cd)"),
    #     ("ab*|cd", "((ab*)|cd)"),
    #     ("a|b*", "(a|(b*))"),
    #     ("abc|cde", "(abc|cde)"),
    #     ("a|b*abb", "(a|((b*)+abb)"),
    #     ("(35)*124", "((35*)+124)"),
    #     ("(a|b)*abb", "(((a|b)*)abb)"),
    #     ("(a|b)*abb(ϵ|a|b)*", "((((a|b)*)+abb)+(((ϵ|a)|b)*))"),
    #     ("(ab*(c|d)*)|(e|(f*g))", "(((ab*)+((c|d)*))|(e|((f*)+g)))"),
    #     ("a*bcc|c*dee", "(((a*)+bcc)|((c*)+dee))"),
    #     # [a], [+]
    #     # [(a*)], [+]
    #     # [(a*), bcc], [+]
    #     # [(a*), bcc], [+] -> evaluate ops with higher priority than | -> [((a*)+bcc)], [|]
    #     # [((a*)+bcc), c], [|, +]
    #     # [((a*)+bcc), (c*)], [|, +],
    #     # [((a*)+bcc), (c*), dee], [|, +, +]
    #     # [((a*)+bcc), ((c*)+dee)], [|]
    #     # [(((a*)+bcc)+((c*)+dee))]
    #     ("(a|b)c*d", "((a|b)+(c*)+d)"),
    # ):
    #     print(NondeterministicFiniteAutomata.from_string(regex, rebuild_infix), target_lisp)
