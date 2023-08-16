from typing import Callable, TypeVar, Deque, Set
from finite_automata_node import FiniteAutomataNode, EpsilonTransition, CharTransition
from collections import deque
from abc import ABC


class NondeterministicFiniteAutomata(object):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        self.start_node = start_node
        self.end_node = end_node

    def __repr__(self) -> str:
        # iterate through all FA Nodes, in dfs fashion?
        def dfs(cur_node: FiniteAutomataNode, action: Callable[[FiniteAutomataNode], None], visited: Set[int]):
            visited.add(cur_node.id)
            action(cur_node)
            for _, nxt_node in cur_node.successors:
                if nxt_node.id not in visited:
                    dfs(nxt_node, action, visited)
        buffer = []
        dfs(self.start_node, lambda node: buffer.append(repr(node)), set())
        return "\n".join(buffer)


T = TypeVar("T")


# consider this as a trait... why there's no trait in python
class RegexOperation(ABC):

    @staticmethod
    def make_nfa(s: str) -> T:
        raise NotImplementedError()

    @classmethod
    def kleene_star(cls, r: T) -> T:
        raise NotImplementedError()
        
    @staticmethod
    def or_(*ops: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def concat(l: T, r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def plus(r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def optional(r: T) -> T:
        raise NotImplementedError()


class StringRegexOperation(RegexOperation):
    # impl RegexOperation<String>
    @staticmethod
    def make_nfa(s: str) -> str:
        return s

    @classmethod
    def kleene_star(cls, r: str) -> str:
        return "(%s*)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

    @staticmethod
    def or_(*ops: str) -> str:
        return "(%s)" % "|".join(ops) if len(ops) > 1 else ops[0]

    @staticmethod
    def concat(l: str, r: str) -> str:
        return "%s->%s" % (l, r)

    @staticmethod
    def plus(r: str) -> str:
        return "(%s+)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

    @staticmethod
    def optional(r: str) -> str:
        return "(%s?)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r


class NFANodeRegexOperation(RegexOperation):
    # impl RegexOperation<NFA>
    @staticmethod
    def make_nfa(c: str) -> NondeterministicFiniteAutomata:
        assert len(c) == 1
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        s.add_edge(CharTransition(c) if c != "ϵ" else EpsilonTransition(), e)
        return NondeterministicFiniteAutomata(s, e)

    @classmethod
    def kleene_star(cls, r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        # s ->               ϵ                 -> e
        #   \                                /
        #   r.start_node -> ... -> r.end_node
        #               \         /
        #                 <- ϵ <-
        r.end_node.add_edge(EpsilonTransition(), r.start_node)
        return cls.optional(r)

    @staticmethod
    def or_(*ops: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        #     -> l ->
        #   /    .    \
        # s   -> . ->   e
        #   \    .    /
        #     -> r ->
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        for op in ops:
            s.add_edge(EpsilonTransition(), op.start_node)
            op.end_node.add_edge(EpsilonTransition(), e)
        return NondeterministicFiniteAutomata(s, e)

    @staticmethod
    def concat(l: NondeterministicFiniteAutomata, r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        # end_node must have no successors and start_node must have no predecessors
        # thus simply merge l.end_node with r.start_node
        l.end_node.successors = r.start_node.successors
        return NondeterministicFiniteAutomata(l.start_node, r.end_node)

    @staticmethod
    def plus(r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        # TODO implement NFA recursive copy
        raise NotImplementedError()

    @staticmethod
    def optional(r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        # s -> ϵ -> e
        #  \       /
        #   -> r ->
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        s.add_edge(EpsilonTransition(), e)
        s.add_edge(EpsilonTransition(), r.start_node)
        r.end_node.add_edge(EpsilonTransition(), e)
        return NondeterministicFiniteAutomata(s, e)


def parse(r: Deque[str], regex_operation: RegexOperation):
    # op priority: {*, +} > concat > or
    ops = deque()  # operands, but doesn't consider "|" operators. We must first concatenate everything before "|" them
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
            ops.append(regex_operation.make_nfa(s))
    if ops:
        or_ops.append(reduce_concat())
    l = regex_operation.or_(*or_ops)
    return l


def test_parsing_str():
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
        ("ab|cd|ef", "(a->b|c->d|e->f)"),
        ("abc|cde", "(a->b->c|c->d->e)"),
        ("ac(bc|de)|ff", "(a->c->(b->c|d->e)|f->f)"),
        ("public|fn|trait|i8|i16|i32|i64|isize|impl|for|->", "(p->u->b->l->i->c|f->n|t->r->a->i->t|i->8|i->1->6|i->3->2|i->6->4|i->s->i->z->e|i->m->p->l|f->o->r|-->>)"),
        ("0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*", "(0|(1|2|3|4|5|6|7|8|9)->((0|1|2|3|4|5|6|7|8|9)*))")
    ):
        assert parse(deque(regex), op) == expected_output


def test_parsing_nfa():
    op = NFANodeRegexOperation()
    for regex in (
        "a",
        "a|b",
        "a*",
        "ab|cd|ef"
        "public|fn|trait|i8|i16|i32|i64|isize|impl|for|->",
        "0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*"
    ):
        FiniteAutomataNode.reset_counter()
        print(regex, parse(deque(regex), op))

if __name__ == "__main__":
    test_parsing_nfa()
