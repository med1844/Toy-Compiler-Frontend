import inspect
from typing import Any, List, Dict, Set, Tuple, Deque, Callable, Iterable
from collections import deque
from io_utils.from_json import FromJson
from io_utils.to_json import ToJson


class LangDef(ToJson):
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

    # TODO: further split into things like `trait JsonScanner`, `train JsonParser`, etc
    def __init__(
        self,
        dfa_list_json: List[Dict],
        action_json: Dict,
        goto_json: Dict,
        parse_tree_action_json: Dict[int, Tuple[int, str, Tuple[str, str]]],
    ):
        self.dfa_list_json = dfa_list_json
        self.action_json = action_json
        self.goto_json = goto_json

        # we well have to exec function definitions to make actions callable...
        self.parse_tree_action_json: Dict[
            int, Tuple[int, str, Tuple[str, str]]
        ] = parse_tree_action_json
        self.evaluated_functions: Dict[int, Callable] = {}
        for prod_id, (_, _, (fn_name, fn_src)) in parse_tree_action_json.items():
            exec(fn_src)
            self.evaluated_functions[prod_id] = eval(fn_name)

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
                    if not cond or any(
                        l <= ord(c) < r for l, r in cond
                    ):  # TODO: use bisect_right - 1
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
        def parse_one_word(dfa_list: List[Dict], s: Deque[str]) -> Tuple[int, str]:
            return max(
                enumerate(self.__match_first(dfa, s) for dfa in dfa_list),
                key=lambda x: x[1],
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

    def parse(self, tokens: List[Tuple[int, str]], context: Dict[str, Any] = dict()):
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
                if self.action_json["table"][current_state][token_type] is None:
                    raise ValueError("ERROR: %s, %s" % (current_state, token_type))
                action_type, next_state = self.action_json["table"][current_state][
                    token_type
                ]
                if action_type == 0:  # shift to another state
                    state_stack.append(next_state)
                    node_stack.append(lex_str)
                    break
                elif action_type == 1:
                    prod_id = next_state
                    nargs, non_terminal, _ = self.parse_tree_action_json[prod_id]
                    fn = self.evaluated_functions[prod_id]
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
            "dfa_list_json": self.dfa_list_json,
            "action_json": self.action_json,
            "goto_json": self.goto_json,
            "parse_tree_action_json": self.parse_tree_action_json,
        }

    @classmethod
    def from_json(cls, obj: Dict[str, Any]):
        return cls(
            obj["dfa_list_json"],
            obj["action_json"],
            obj["goto_json"],
            obj["parse_tree_action_json"],
        )
