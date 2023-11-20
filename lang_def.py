from typing import Any, Deque, List, Dict, Optional, Set, Tuple, Callable, Iterable
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

    def __init__(
        self,
        dfa_set_json: Dict[str, Any],
        raw_grammar_to_id: Dict[str, int],
        prod_id_to_narg_and_non_terminal: Dict[str, Tuple[int, str]],
        action_json: Dict,
        goto_json: Dict,
    ):
        self.dfa_set_json = dfa_set_json
        self.raw_grammar_to_id = raw_grammar_to_id
        self.prod_id_to_narg_and_non_terminal = prod_id_to_narg_and_non_terminal
        self.action_json = action_json
        self.goto_json = goto_json

        self.prod_id_to_fn: Dict[str, Callable] = {}  # this member won't be exported
        # but still, use same convention that key is str

    def production(self, *productions: str):
        """
        register a function to run at some position in the production

        @tree.production('E -> E "+" T')
        def foo(e, e1, plus, t):
            return "bar"
        """

        def decorate(function: Callable):
            for prod in productions:
                self.prod_id_to_fn[str(self.raw_grammar_to_id[prod])] = function
            return function

        return decorate

    @staticmethod
    def match_one(dfa: Dict[str, Any], s: Deque[str]) -> Tuple[int, str]:
        cur_node: int = dfa["start_node"]
        accept_states: Set[int] = set(dfa["accept_states"])
        fa_id: List[Optional[int]] = dfa["fa_id"]
        buffer = []
        accepted_buffer = []
        last_accept_state_fa_id: Optional[int] = None
        while s:
            c = s.popleft()
            any_hit = False
            if cur_node in accept_states:
                if fa_id[cur_node] is not None:
                    last_accept_state_fa_id = fa_id[cur_node]
                accepted_buffer.extend(buffer)
                buffer.clear()
            for cond, nxt_node in dfa["edges"].get(str(cur_node), ()):
                # cond: List[Tuple[int, int]]
                # nxt_node: int
                if not cond or any(
                    l <= ord(c) < r for l, r in cond
                ):  # TODO: use bisect_right - 1
                    buffer.append(c)
                    cur_node = nxt_node
                    any_hit = True
                    break
            if not any_hit:
                s.appendleft(c)
                break
        if cur_node in accept_states:
            if fa_id[cur_node] is not None:
                last_accept_state_fa_id = fa_id[cur_node]
            accepted_buffer.extend(buffer)
            buffer.clear()
        if accepted_buffer and last_accept_state_fa_id is not None:
            return (last_accept_state_fa_id, "".join(accepted_buffer))
        return (-1, "")

    def scan(self, s: str) -> Iterable[Tuple[int, str]]:
        deque_s = deque(s)
        while deque_s:
            (id, word) = self.match_one(self.dfa_set_json, deque_s)
            if word:
                yield id, word
            else:
                deque_s.popleft()  # if no match, simply move forward, in order to consume all input
            while deque_s and deque_s[0] in {" ", "\t", "\n"}:
                deque_s.popleft()
        yield -1, "$"

    def parse(
        self, tokens: Iterable[Tuple[int, str]], context: Dict[str, Any] = dict()
    ):
        # context stores all things that you wish to transfer between parses
        # examples:
        # - stored variables
        # - function names
        # - etc
        state_stack = [0]
        node_stack: List[str | Any] = [
            -1
        ]  # str -> terminal, Any -> evaluated non_terminal, depends on PT action fn return type

        for token_type, lex_str in tokens:
            current_state = state_stack[-1]
            while True:
                if self.action_json["table"][current_state][str(token_type)] is None:
                    raise ValueError("ERROR: %s, %s" % (current_state, str(token_type)))
                action_type, next_state = self.action_json["table"][current_state][
                    str(token_type)
                ]
                if action_type == 0:  # shift to another state
                    state_stack.append(next_state)
                    node_stack.append(lex_str)
                    break
                elif action_type == 1:
                    prod_id: int = next_state
                    nargs, non_terminal = self.prod_id_to_narg_and_non_terminal[
                        str(prod_id)
                    ]
                    fn = self.prod_id_to_fn[str(prod_id)]
                    args = []
                    for _ in range(nargs):
                        state_stack.pop()
                        args.append(node_stack.pop())
                    args.append(context)
                    args.reverse()

                    current_state = state_stack[-1]
                    next_state = self.goto_json["table"][current_state][non_terminal]
                    state_stack.append(next_state)
                    node_stack.append(fn(*args))
                    current_state = state_stack[-1]
                    continue
                elif action_type == 2:
                    break
                else:
                    assert False

        return node_stack[-1]

    def eval(self, in_: str, context: Dict[str, Any] = dict()) -> Any:
        return self.parse(self.scan(in_), context)

    def to_json(self):
        return {
            "dfa_set_json": self.dfa_set_json,
            "raw_grammar_to_id": self.raw_grammar_to_id,
            "prod_id_to_narg_and_non_terminal": self.prod_id_to_narg_and_non_terminal,
            "action_json": self.action_json,
            "goto_json": self.goto_json,
        }

    @classmethod
    def from_json(cls, obj: Dict[str, Any]):
        return cls(
            obj["dfa_set_json"],
            obj["raw_grammar_to_id"],
            obj["prod_id_to_narg_and_non_terminal"],
            obj["action_json"],
            obj["goto_json"],
        )
