from typing import Set, Iterable
from dfa_utils.finite_automata import FiniteAutomata
from dfa_utils.finite_automata_node import EpsilonTransition, FiniteAutomataNode
from io_utils.to_json import ToJson


class FiniteAutomataSet(ToJson):
    def __init__(self, fa_set: Iterable[FiniteAutomata]):
        # merge into one mega dfa
        start = FiniteAutomataNode()
        accept_states = set()
        for i, fa in enumerate(fa_set):
            start.add_edge(EpsilonTransition(), fa.start_node)
            for accept_state in fa.accept_states:
                accept_state.fa_id = i
                accept_states.add(accept_state)
        self.fa = FiniteAutomata(start, accept_states).determinize()

    def match_one(self, s: Iterable[str]) -> str:
        return self.fa.match_first(s)

    def to_json(self):
        return self.fa.to_json()
