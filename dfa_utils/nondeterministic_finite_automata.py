from typing import TypeVar, Deque
from finite_automata import FiniteAutomata
from finite_automata_node import FiniteAutomataNode, EpsilonTransition, CharTransition
from collections import deque
from abc import ABC


class NondeterministicFiniteAutomata(FiniteAutomata):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        super().__init__(start_node)
        self.end_node = end_node

    @classmethod
    def from_string(cls, regex: str) -> "NondeterministicFiniteAutomata":
        return parse(deque(regex), NFANodeRegexOperation())


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
        if len(ops) == 1:
            return ops[0]
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        for op in ops:
            s.add_edge(EpsilonTransition(), op.start_node)
            op.end_node.add_edge(EpsilonTransition(), e)
        return NondeterministicFiniteAutomata(s, e)

    @staticmethod
    def concat(l: NondeterministicFiniteAutomata, r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        l.end_node.add_edge(EpsilonTransition(), r.start_node)
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
        elif s == "?":
            ops.append(regex_operation.optional(ops.pop()))
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


def test_nfa_hash():
    # test if a back edge causes difference in the hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    e0.add_edge(EpsilonTransition(), s0)
    nfa_0 = NondeterministicFiniteAutomata(s0, e0)

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = NondeterministicFiniteAutomata(s1, e1)

    assert hash(nfa_0) != hash(nfa_1)


def test_parsing_nfa_0():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("a")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s.add_edge(CharTransition("a"), e)
    expected_nfa = NondeterministicFiniteAutomata(s, e)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_1():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("a|b")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sb = FiniteAutomataNode()
    eb = FiniteAutomataNode()
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), sb)
    sa.add_edge(CharTransition("a"), ea)
    sb.add_edge(CharTransition("b"), eb)
    ea.add_edge(EpsilonTransition(), e)
    eb.add_edge(EpsilonTransition(), e)
    expected_nfa = NondeterministicFiniteAutomata(s, e)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_2():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("ab")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(CharTransition("b"), n3)
    expected_nfa = NondeterministicFiniteAutomata(n0, n3)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_3():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("a*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), sa)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = NondeterministicFiniteAutomata(s, e)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_4():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("a?")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = NondeterministicFiniteAutomata(s, e)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_5():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("(c|d)*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    sc = FiniteAutomataNode()
    ec = FiniteAutomataNode()
    sd = FiniteAutomataNode()
    ed = FiniteAutomataNode()

    sc.add_edge(CharTransition("c"), ec)
    sd.add_edge(CharTransition("d"), ed)

    s0.add_edge(EpsilonTransition(), sc)
    s0.add_edge(EpsilonTransition(), sd)

    ec.add_edge(EpsilonTransition(), e0)
    ed.add_edge(EpsilonTransition(), e0)

    e0.add_edge(EpsilonTransition(), s0)

    s.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), s0)

    e0.add_edge(EpsilonTransition(), e)

    expected_nfa = NondeterministicFiniteAutomata(s, e)
    assert hash(constructed_nfa) == hash(expected_nfa)
