from typing import List, Dict, Set, Tuple, Deque, Callable, Iterable
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

    # TODO: further split into things like `trait JsonScanner`, `train JsonParser`, etc
    def __init__(
        self,
        dfa_list_json: List[Dict],
        action_json: Dict,
        goto_json: Dict,
        parse_tree_action_json: Dict[int, Tuple[int, Dict[int, Tuple[str, str]]]],
    ):
        self.dfa_list_json = dfa_list_json
        self.action_json = action_json
        self.goto_json = goto_json
        # we well have to do something to make actions callable...
        self.parse_tree_action_json = {}
        for prod_id, (n_args, d) in parse_tree_action_json.items():
            evaled_d = {}
            for index, (fn_name, fn_src) in d.items():
                exec(fn_src)
                evaled_d[index] = eval(fn_name)
            self.parse_tree_action_json[prod_id] = (n_args, evaled_d)

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

    def parse(self, tokens: List[Tuple[int, str]], actions: List[Callable]):
        stateStack = [0]
        nodeStack: List[int | str] = [-1]

        # lexStr is the lexical string; token type is int.
        for tokenType, lexStr in tokens:
            currentState = stateStack[-1]
            while True:
                if self.action_json[currentState][tokenType] is None:
                    print("ERROR: %s, %s" % (currentState, tokenType))
                    exit()
                actionType, nextState = self.action_json[currentState][tokenType]
                if actionType == 0:  # shift to another state
                    stateStack.append(nextState)
                    nodeStack.append(lexStr)
                    break
                elif actionType == 1:
                    prodID = nextState
                    nonTerminal, sequence = cfg.get_production(prodID)
                    nonTerminalNode = PTNode(nonTerminal, prodID=prodID)
                    for i in range(len(sequence) - 1, -1, -1):
                        symbol = sequence[i]
                        if symbol == EMPTY:
                            continue
                        currentSymbol = nodeStack.pop()
                        stateStack.pop()
                        assert isinstance(currentSymbol, PTNode)
                        nonTerminalNode.addChild(currentSymbol)
                    nonTerminalNode.reverse()

                    currentState = stateStack[-1]
                    nextState = self.goto_json[currentState][nonTerminal]
                    stateStack.append(nextState)
                    nodeStack.append(nonTerminalNode)
                    currentState = stateStack[-1]
                    continue
                elif actionType == 2:
                    if needLog:
                        log.append((str(stateStack), str(nodeStack), "ACCEPTED"))
                    break
                else:
                    assert False

            # print(stateStack, nodeStack, tokenType, actionType, nextState)
        # print(nodeStack)
        if needLog:
            return ParseTree(nodeStack[-1]), log
        return ParseTree(nodeStack[-1])
