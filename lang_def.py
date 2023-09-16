from collections.abc import Iterable
from typing import List, Dict, Set, Tuple, Deque
from collections import deque


class LangDef:
    """
    A class that captures everything that's required by a compiler front-end, with no dependency.
    This allows things to be portable, i.e. copy json files or embed them, and copy this class.
    Use this class to load these json files, and you should be good to go.

    By splitting generation code with the actual parsing code, we manage to reduce the amount of code
    that must be copied / ported. We also increase runtime performance, as generating these tables
    could be time-consuming.

    Both TypeDef and ContextFreeGrammar class should have implemented the ToJson trait.
    When build from scratch, put typedef.to_json(), action.to_json(), and goto.to_json() here.
    """

    def __init__(self, dfa_list_json: List[Dict], action_json: Dict, goto_json: Dict):
        self.dfa_list_json = dfa_list_json
        self.action_json = action_json
        self.goto_json = goto_json

    def __match_first(self, dfa: Dict, s: Iterable[str]) -> str:
        cur_node: int = dfa["start_node"]
        accept_states: Set[int] = set(dfa["accept_states"])
        buffer = []
        accepted_buffer = []
        for c in s:
            any_hit = False
            if cur_node in accept_states:
                accepted_buffer.extend(buffer)
                buffer.clear()
            if cur_node in dfa["edges"]:
                for cond, nxt_node in dfa["edges"][cur_node]:
                    # cond: List[Tuple[int, int]]
                    # nxt_node: int
                    if not cond or any(l <= ord(c) < r for l, r in cond):
                        buffer.append(c)
                        cur_node = nxt_node
                        any_hit = True
                        break
            if not any_hit:
                break
        if cur_node in accept_states:
            accepted_buffer.extend(buffer)
            buffer.clear()
        if accepted_buffer:
            return "".join(accepted_buffer)
        return ""

    def scan(self, s: str) -> List[Tuple[int, str]]:
        def parse_one_word(
            dfa_list: List[Dict], s: Deque[str]
        ) -> Tuple[int, str]:
            return max(
                enumerate(self.__match_first(dfa, s) for dfa in dfa_list), key=lambda x: x[1]
            )

        tokens = []
        deque_s = deque(s)
        while deque_s:
            (id, word) = parse_one_word(self.dfa_list_json, deque_s)
            tokens.append((id, word))
            for _ in range(len(word)):
                deque_s.popleft()
            while deque_s and deque_s[0] in {" ", "\t", "\n"}:
                deque_s.popleft()
        tokens.append((-1, "$"))
        return tokens

