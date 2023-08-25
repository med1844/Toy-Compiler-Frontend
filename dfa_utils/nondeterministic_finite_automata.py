from copy import deepcopy
from typing import TypeVar, Deque, Dict, Self, Set
from finite_automata import FiniteAutomata
from finite_automata_node import FiniteAutomataNode, EpsilonTransition, CharTransition
from collections import deque
from abc import ABC


class NondeterministicFiniteAutomata(FiniteAutomata):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        super().__init__(start_node)
        self.end_node = end_node

    # impl Copy for NondetermFiniteAutomata
    def __deepcopy__(self, memo=None) -> Self:
        # now that node id has been removed, we could recursively copy things
        def dfs(cur_node: FiniteAutomataNode, node_mapping: Dict[FiniteAutomataNode, FiniteAutomataNode], visited: Set[FiniteAutomataNode]):
            if cur_node in visited:
                return
            visited.add(cur_node)
            for cond, nxt_node in cur_node.successors:
                if nxt_node not in node_mapping:
                    node_mapping[nxt_node] = FiniteAutomataNode()
                node_mapping[cur_node].add_edge(cond, node_mapping[nxt_node])
                if nxt_node not in visited:
                    dfs(nxt_node, node_mapping, visited)

        mappings = {self.start_node: FiniteAutomataNode()}
        dfs(self.start_node, mappings, set())
        return NondeterministicFiniteAutomata(mappings[self.start_node], mappings[self.end_node])

    @classmethod
    def from_string(cls, regex: str) -> "NondeterministicFiniteAutomata":
        return parse(deque(regex), NFANodeRegexOperation())


T = TypeVar("T")


# consider this as a trait... why there's no trait in python
class RegexOperation(ABC):

    @staticmethod
    def make_nfa(s: str) -> T:
        raise NotImplementedError()

    @staticmethod
    def make_range_nfa(*ranges: range) -> T:
        raise NotImplementedError()

    @staticmethod
    def make_dot_nfa() -> T:
        # TODO I actually start feeling this super dirty... is there any good way to refactor this
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
    def make_range_nfa(cls, *ranges: range) -> str:
        return cls.or_(*(cls.make_nfa(chr(i)) for r in ranges for i in r))

    @classmethod
    def make_dot_nfa(cls) -> str:
        # only match printable ascii characters, i.e. no unicode support
        return cls.make_range_nfa(range(0x20, 0x7f))  # 0x7f is not printable thus doesn't include it

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
    def make_range_nfa(cls, *ranges: range) -> NondeterministicFiniteAutomata:
        return cls.or_(*(cls.make_nfa(chr(i)) for r in ranges for i in r))

    @classmethod
    def make_dot_nfa(cls) -> NondeterministicFiniteAutomata:
        # only match printable ascii characters, i.e. no unicode support
        return cls.make_range_nfa(range(0x20, 0x7f))  # 0x7f is not printable thus doesn't include it

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

    @classmethod
    def plus(cls, r: NondeterministicFiniteAutomata) -> NondeterministicFiniteAutomata:
        s = deepcopy(r)
        t = cls.kleene_star(r)
        s.end_node.add_edge(EpsilonTransition(), t.start_node)
        return NondeterministicFiniteAutomata(s.start_node, t.end_node)

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
        elif s == "[":
            ranges = []
            while True:
                s = r.popleft()
                _ = r.popleft()
                e = r.popleft()
                ranges.append(range(ord(s), ord(e) + 1))
                if r[0] == "]":
                    r.popleft()
                    break
            ops.append(regex_operation.make_range_nfa(*ranges))
        elif s == ".":
            ops.append(regex_operation.make_dot_nfa())
        elif len(s) == 1:
            if s == "\\":
                s = r.popleft()
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
        ("0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*", "(0|(1|2|3|4|5|6|7|8|9)->((0|1|2|3|4|5|6|7|8|9)*))"),
        ("0|[1-9][0-9]*", "(0|(1|2|3|4|5|6|7|8|9)->((0|1|2|3|4|5|6|7|8|9)*))"),
    ):
        assert parse(deque(regex), op) == expected_output


def test_nfa_hash_0():
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


def test_nfa_hash_1():
    # make sure that the order we add edges doesn't effect hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    s0.add_edge(CharTransition("b"), e0)
    nfa_0 = NondeterministicFiniteAutomata(s0, e0)

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("b"), e1)
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = NondeterministicFiniteAutomata(s1, e1)

    assert hash(nfa_0) == hash(nfa_1)


def test_nfa_deepcopy_0():
    for regex in (
        "a*bcc|c*dee",
        "((a|b)*(cc|dd))*ee",
        "ac(bc|de)|ff",
        "a*",
        "a",
    ):
        a = NondeterministicFiniteAutomata.from_string(regex)
        b = deepcopy(a)
        assert hash(a) == hash(b)


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

def test_parsing_nfa_6():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("(ab*(c|d)*)|(e|(f*g))")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)

    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(EpsilonTransition(), n2)

    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n4.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n2)
    n3.add_edge(EpsilonTransition(), n5)

    n1.add_edge(EpsilonTransition(), n4)

    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n6.add_edge(CharTransition("c"), n7)

    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()
    n8.add_edge(CharTransition("d"), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()

    n10.add_edge(EpsilonTransition(), n6)
    n10.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n11)
    n9.add_edge(EpsilonTransition(), n11)

    n11.add_edge(EpsilonTransition(), n10)

    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n12.add_edge(EpsilonTransition(), n10)
    n12.add_edge(EpsilonTransition(), n13)
    n11.add_edge(EpsilonTransition(), n13)

    n5.add_edge(EpsilonTransition(), n12)

    n14 = FiniteAutomataNode()

    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n15.add_edge(CharTransition("e"), n16)

    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n17.add_edge(CharTransition("f"), n18)
    n18.add_edge(EpsilonTransition(), n17)

    n19 = FiniteAutomataNode()
    n20 = FiniteAutomataNode()
    n19.add_edge(EpsilonTransition(), n20)
    n19.add_edge(EpsilonTransition(), n17)
    n18.add_edge(EpsilonTransition(), n20)

    n14.add_edge(EpsilonTransition(), n15)
    n14.add_edge(EpsilonTransition(), n19)

    n21 = FiniteAutomataNode()
    n22 = FiniteAutomataNode()
    n21.add_edge(CharTransition("g"), n22)
    n20.add_edge(EpsilonTransition(), n21)

    n23 = FiniteAutomataNode()
    n16.add_edge(EpsilonTransition(), n23)
    n22.add_edge(EpsilonTransition(), n23)

    n24 = FiniteAutomataNode()
    n25 = FiniteAutomataNode()

    n24.add_edge(EpsilonTransition(), n0)
    n24.add_edge(EpsilonTransition(), n14)
    n13.add_edge(EpsilonTransition(), n25)
    n23.add_edge(EpsilonTransition(), n25)

    expected_nfa = NondeterministicFiniteAutomata(n24, n25)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_7():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("a+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n4.add_edge(CharTransition("a"), n5)
    n5.add_edge(EpsilonTransition(), n3)
    n5.add_edge(EpsilonTransition(), n4)

    expected_nfa = NondeterministicFiniteAutomata(n0, n3)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_8():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("(0|1|2|3)+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()

    n1.add_edge(CharTransition("0"), n2)
    n3.add_edge(CharTransition("1"), n4)
    n5.add_edge(CharTransition("2"), n6)
    n7.add_edge(CharTransition("3"), n8)

    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n3)
    n0.add_edge(EpsilonTransition(), n5)
    n0.add_edge(EpsilonTransition(), n7)
    n2.add_edge(EpsilonTransition(), n9)
    n4.add_edge(EpsilonTransition(), n9)
    n6.add_edge(EpsilonTransition(), n9)
    n8.add_edge(EpsilonTransition(), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n14 = FiniteAutomataNode()
    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n19 = FiniteAutomataNode()

    n11.add_edge(CharTransition("0"), n12)
    n13.add_edge(CharTransition("1"), n14)
    n15.add_edge(CharTransition("2"), n16)
    n17.add_edge(CharTransition("3"), n18)

    n10.add_edge(EpsilonTransition(), n11)
    n10.add_edge(EpsilonTransition(), n13)
    n10.add_edge(EpsilonTransition(), n15)
    n10.add_edge(EpsilonTransition(), n17)
    n12.add_edge(EpsilonTransition(), n19)
    n14.add_edge(EpsilonTransition(), n19)
    n16.add_edge(EpsilonTransition(), n19)
    n18.add_edge(EpsilonTransition(), n19)

    n19.add_edge(EpsilonTransition(), n10)

    n20 = FiniteAutomataNode()
    n21 = FiniteAutomataNode()

    n20.add_edge(EpsilonTransition(), n21)
    n20.add_edge(EpsilonTransition(), n10)
    n19.add_edge(EpsilonTransition(), n21)

    n9.add_edge(EpsilonTransition(), n20)

    expected_nfa = NondeterministicFiniteAutomata(n0, n3)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_10():

    # test if ϵ is correctly handled
    constructed_nfa = NondeterministicFiniteAutomata.from_string("ϵ|a")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n0.add_edge(EpsilonTransition(), n1)
    n1.add_edge(EpsilonTransition(), n2)

    n0.add_edge(EpsilonTransition(), n3)
    n3.add_edge(CharTransition("a"), n4)

    n2.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n5)

    expected_nfa = NondeterministicFiniteAutomata(n0, n5)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_11():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("d(ϵ|ab)")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n0.add_edge(CharTransition("d"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n3.add_edge(EpsilonTransition(), n5)
    n4.add_edge(CharTransition("a"), n6)
    n6.add_edge(EpsilonTransition(), n11)
    n11.add_edge(CharTransition("b"), n7)
    n5.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n8)

    expected_nfa = NondeterministicFiniteAutomata(n0, n8)
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_12():
    # test \, they should help recognize *, (, ), [, ], |, +, ?, etc
    for regex in (
        "*", "(", ")", "[", "]", "|", "+", "?", "."
    ):
        constructed_nfa = NondeterministicFiniteAutomata.from_string("\\" + regex)
        n0 = FiniteAutomataNode()
        n1 = FiniteAutomataNode()
        n0.add_edge(CharTransition(regex), n1)
        expected_nfa = NondeterministicFiniteAutomata(n0, n1)
        assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_13():
    constructed_nfa = NondeterministicFiniteAutomata.from_string("[0-3]+")
    expected_nfa = NondeterministicFiniteAutomata.from_string("(0|1|2|3)+")
    assert hash(constructed_nfa) == hash(expected_nfa)

