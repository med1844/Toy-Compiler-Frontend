from collections import deque
from typing import Deque, Optional, Set, Dict, Self, Iterable, List
from nondeterministic_finite_automata import NondeterministicFiniteAutomata
from finite_automata import FiniteAutomata
from finite_automata_node import CharTransition, FiniteAutomataNode, EpsilonTransition, Transition


class DeterminsticFiniteAutomata(FiniteAutomata):
    def __init__(self, start_node: FiniteAutomataNode) -> None:
        super().__init__(start_node)

    @classmethod
    def from_string(cls, regex: str) -> Self:
        return cls.from_nfa(NondeterministicFiniteAutomata.from_string(regex))

    @classmethod
    def from_nfa(cls, nfa: NondeterministicFiniteAutomata) -> Self:
        return NFA_to_DFA(nfa)

    def match_first(self, s: str) -> Optional[str]:
        # TODO this is SO UGLY, think about more elegant implementation
        cur_node = self.start_node
        buffer = []
        accepted_buffer = []
        for c in s:
            any_hit = False
            if cur_node.is_accept:
                accepted_buffer.extend(buffer)
                buffer.clear()
            for cond, nxt_node in cur_node.successors:
                if cond(c):
                    buffer.append(c)
                    cur_node = nxt_node
                    any_hit = True
                    break
            if not any_hit:
                break
        if cur_node.is_accept:
            accepted_buffer.extend(buffer)
            buffer.clear()
        if accepted_buffer:
            return "".join(accepted_buffer)
        return None


class FANodeClosure:
    # a simple helper class that implements __hash__ so that if the closure has been visited or not could be easily tracked
    def __init__(self, s: Set[FiniteAutomataNode] = set()) -> None:
        self.closure: Set[FiniteAutomataNode] = s

    def __hash__(self) -> int:
        # could also use bitmasks, but too expensive?
        return hash(tuple(sorted((node for node in self.closure), key=id)))

    def __eq__(self, other: Self) -> bool:
        return self.closure == other.closure  # that's the same set of nodes, simply compare the set equivalence


def epsilon_closure(n: Iterable[FiniteAutomataNode]) -> FANodeClosure:
    # the ϵ closure for a set of nodes
    visited: Set[FiniteAutomataNode] = set()
    que: Deque[FiniteAutomataNode] = deque(n)
    while que:
        cur = que.popleft()
        if cur in visited:
            continue
        visited.add(cur)
        for cond, nxt in cur.successors:
            if nxt not in visited and isinstance(cond, EpsilonTransition):
                que.append(nxt)
    return FANodeClosure(visited)


def NFA_to_DFA(nfa: NondeterministicFiniteAutomata) -> DeterminsticFiniteAutomata:
    # each ϵ-closure corresponds to a node in DFA
    nfa.end_node.is_accept = True  # should this be automatic?
    start_closure = epsilon_closure([nfa.start_node])
    que: Deque[FANodeClosure] = deque([start_closure])
    visited: Set[FANodeClosure] = set()
    closure_to_node: Dict[FANodeClosure, FiniteAutomataNode] = {
        start_closure: FiniteAutomataNode(any(node.is_accept for node in start_closure.closure))
    }

    while que:
        cur = que.popleft()
        if cur in visited:
            continue
        visited.add(cur)
        cur_node = closure_to_node[cur]  # would be used to add edges

        # for all possible outcoming edges in all nodes...
        # since nfa could have same transition condition pointing to different nodes, we have to group first before proceed
        group_by_edge: Dict[Transition, List[FiniteAutomataNode]] = {}
        for cond, nxt in ((cond, nxt) for node in cur.closure for cond, nxt in node.successors if not isinstance(cond, EpsilonTransition)):
            group_by_edge.setdefault(cond, list()).append(nxt)

        for cond, nxts in group_by_edge.items():
            nxt_closure = epsilon_closure(nxts)
            if nxt_closure not in closure_to_node:
                closure_to_node[nxt_closure] = FiniteAutomataNode(any(node.is_accept for node in nxt_closure.closure))
                que.append(nxt_closure)
            nxt_node = closure_to_node[nxt_closure]
            cur_node.add_edge(cond, nxt_node)
    
    return DeterminsticFiniteAutomata(closure_to_node[start_closure])


def test_dfa():
    for regex in (
        "a",
        "a|b",
        "a*",
        "a?",
        "abc",
        "public|private",
        "c(a|b)?d",
        "(a|b)*abb(a|b)*",
    ):
        dfa = DeterminsticFiniteAutomata.from_string(regex)
        print("%s\n%s:\n%s\n%s" % ("=" * 50, regex, dfa, "=" * 50))


def test_dfa_0():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_1():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a|b")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode(is_accept=True)
    n2 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n2)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_2():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a*")
    n0 = FiniteAutomataNode(is_accept=True)
    n1 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("a"), n1)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_3():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a?")
    n0 = FiniteAutomataNode(is_accept=True)
    n1 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_4():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("abc")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_5():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("pub|pri")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode(is_accept=True)
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("p"), n1)
    n1.add_edge(CharTransition("u"), n2)
    n1.add_edge(CharTransition("r"), n4)
    n2.add_edge(CharTransition("b"), n3)
    n4.add_edge(CharTransition("i"), n5)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_6():
    # test if middle accepts are recognized
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a|abc")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode(is_accept=True)
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_7():
    constructed_dfa = DeterminsticFiniteAutomata.from_string("a+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("a"), n1)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_8():
    # the result of (a|b)+ could be further simplified by DFA minimization
    constructed_dfa = DeterminsticFiniteAutomata.from_string("abb(a|b)+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(CharTransition("a"), n4)
    n3.add_edge(CharTransition("b"), n5)
    n4.add_edge(CharTransition("a"), n6)
    n4.add_edge(CharTransition("b"), n7)
    n5.add_edge(CharTransition("a"), n6)
    n5.add_edge(CharTransition("b"), n7)
    n6.add_edge(CharTransition("a"), n6)
    n6.add_edge(CharTransition("b"), n7)
    n7.add_edge(CharTransition("a"), n6)
    n7.add_edge(CharTransition("b"), n7)

    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_iter_0():
    dfa = DeterminsticFiniteAutomata.from_string("a*")
    for target, expected in (
        ("aabaaabba", "aa"),
        ("baaaa", None)
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_1():
    dfa = DeterminsticFiniteAutomata.from_string("0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*")
    for target, expected in (
        ("10872865 168505", "10872865"),
        ("010101", "0"),
        ("7950X3D", "7950")
    ):
        assert dfa.match_first(target) == expected

