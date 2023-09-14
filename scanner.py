from collections import deque
import re
from typing import Deque, List, Tuple
from dfa_utils.finite_automata import FiniteAutomata
from typeDef import TypeDefinition


def parse_by_dfa(dfa_list: List[FiniteAutomata], s: str) -> List[Tuple[int, str]]:
    # parser would try dfa one by one. returns result with maximum match length.
    # if there're multiple dfas that return max match length, use the foremost one (id smallest one)
    def parse_one_word(
        dfa_list: List[FiniteAutomata], s: Deque[str]
    ) -> Tuple[int, str]:
        return max(
            enumerate(dfa.match_first(s) for dfa in dfa_list), key=lambda x: x[1]
        )

    tokens = []
    deque_s = deque(s)
    while deque_s:
        (id, word) = parse_one_word(dfa_list, deque_s)
        tokens.append((id, word))
        for _ in range(len(word)):
            deque_s.popleft()
        while deque_s and deque_s[0] in {" ", "\t", "\n"}:
            deque_s.popleft()
    tokens.append((-1, "$"))
    return tokens


if __name__ == "__main__":
    typedef = TypeDefinition.from_filename("simpleJava/typedef")
    with open("simpleJava/simple.sjava", "r") as f:
        src_code = f.read()
    print(
        parse_by_dfa(
            typedef.get_dfa_list(),
            src_code,
        )
    )
