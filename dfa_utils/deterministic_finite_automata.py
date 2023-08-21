from collections import deque
from typing import Deque, Set, Dict, Self, Iterable, List
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


class FANodeClosure:
    # a simple helper class that implements __hash__ so that if the closure has been visited or not could be easily tracked
    def __init__(self, s: Set[FiniteAutomataNode] = set()) -> None:
        self.closure: Set[FiniteAutomataNode] = s

    def __hash__(self) -> int:
        # could also use bitmasks, but too expensive?
        return hash(tuple(sorted(node.id for node in self.closure)))

    def __eq__(self, other: Self) -> bool:
        return set(node.id for node in self.closure) == set(node.id for node in other.closure)


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
        nfa = NondeterministicFiniteAutomata.from_string(regex)
        dfa = NFA_to_DFA(nfa)
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
    constructed_dfa = NFA_to_DFA(NondeterministicFiniteAutomata.from_string("a*"))
    n0 = FiniteAutomataNode(is_accept=True)
    n1 = FiniteAutomataNode(is_accept=True)
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("a"), n1)
    expected_dfa = DeterminsticFiniteAutomata(n0)
    assert hash(constructed_dfa) == hash(expected_dfa)

