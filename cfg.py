from typing import Deque, Iterable, Optional, Self, Set, List, Tuple, Dict, Any
from typeDef import TypeDefinition
from collections import deque
from io_utils.to_json import ToJson
import json


class ContextFreeGrammar:

    """
    production:
        nonTerminal -> sequence | sequence | ...

    The cfg parser will first split input to python tuples,
    record both nonTerminals and all symbols, and give ID to each production.
    Then using terminals = allSymbols - nonTerminals, we can get terminals.
    """

    SUBSTITUTE = "_"
    EOF = -1
    EMPTY = ""

    @classmethod
    def load(cls, typedef: TypeDefinition, filename: str) -> Self:
        """
        Given type definition and fileName, create and return a CFG object.
        """
        assert isinstance(typedef, TypeDefinition)
        with open(filename, "r") as f:
            src = f.read()
        return cls.from_string(typedef, src)

    @classmethod
    def from_string(cls, typedef: TypeDefinition, string: str) -> Self:
        """
        Given type definition and CFG string, create and return a CFG object.
        """
        assert isinstance(typedef, TypeDefinition)
        non_terminals: Set[str] = set()
        all_symbol: Set[str] = set()
        grammar_to_id: Dict[Tuple[str, Tuple[str | int, ...]], int] = {}
        raw_grammar_to_id: Dict[str, int] = {}
        start_symbol = None

        temp: List[Tuple[str, List[str]]] = []

        for line in string.split("\n"):
            line = line.strip()
            if not line:
                continue
            non_terminal, seqs = line.split(" -> ")

            if start_symbol is None:
                start_symbol = non_terminal
            non_terminals.add(non_terminal)
            all_symbol.add(non_terminal)

            for seq in seqs.split(" | "):
                symbols = seq.split(" ")
                temp.append((non_terminal, symbols))
                raw_grammar_to_id["%s -> %s" % (non_terminal, seq)] = len(
                    raw_grammar_to_id
                )
                for symbol in seq.split(" "):
                    all_symbol.add(symbol)
        assert start_symbol is not None

        for i, (non_terminal, symbols) in enumerate(temp):
            symbols = tuple(
                ""
                if sym == "''"
                else typedef.get_id_by_name(sym)
                if sym not in non_terminals
                else sym
                for sym in symbols
            )
            grammar_to_id[(non_terminal, symbols)] = i

        terminals = {
            typedef.get_id_by_name(_) for _ in all_symbol - non_terminals if _ != "''"
        }

        return cls(
            terminals, non_terminals, start_symbol, grammar_to_id, raw_grammar_to_id
        )

    def __init__(
        self,
        terminals: Set[int],
        non_terminals: Set[str],
        start_symbol: str,
        grammar_to_id: Dict[Tuple[str, Tuple[str | int, ...]], int],
        raw_grammar_to_id: Dict[str, int],
    ):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.start_symbol = start_symbol
        self.grammar_to_id = grammar_to_id
        self.raw_grammar_to_id = raw_grammar_to_id
        self.id_to_grammar = {v: k for k, v in self.grammar_to_id.items()}
        self.non_terminal_to_prod_id: Dict[str, List[int]] = {}

        for k, v in grammar_to_id.items():
            self.non_terminal_to_prod_id.setdefault(k[0], list()).append(v)

    def __str__(self):
        return str(self.grammar_to_id)

    def get_symbol_in_prod(
        self, production_id: int, dot_pos: int, offset=0
    ) -> Optional[str | int]:
        """
        Given a production id, and the dot position, return the symbol at that
        position.

        eg:
            (E, (E, +, T)): 6
            calling get(6, 1) would return +.

        if dotPos + offset is out of bound, it would return None.
        """
        if dot_pos + offset >= len(self.id_to_grammar[production_id][1]):
            return None
        return self.id_to_grammar[production_id][1][dot_pos + offset]

    def get_production(self, prod_id: int) -> Tuple[str, Tuple[str | int, ...]]:
        """
        Return the sequence of a given production.

        eg:
            (E, (E, +, T)): 6
            calling getProduction(6) would return (E, (E, +, T))
        """
        return self.id_to_grammar[prod_id]

    @property
    def prod_id_to_nargs_and_non_terminal(self) -> Dict[str, Tuple[int, str]]:
        """A helper function solely for LangDef"""
        return {
            str(k): (sum(map(lambda *_: 1, filter(lambda x: x != "''", seq))), non_terminal)
            for k, (non_terminal, seq) in self.id_to_grammar.items()
        }

    def is_non_terminal(self, op: Any):
        return op in self.non_terminals

    def is_terminal(self, op: Any):
        return op in self.terminals

    def get_productions(self, non_terminal: str) -> List[int]:
        """
        Return list of production ids that the nonTerminal can lead to.
        WARNING: DO NOT MODIFY THE RETURN VALUE.
        """
        return self.non_terminal_to_prod_id[non_terminal]

    def is_left_recursive(self):
        for non_terminal, ids in self.non_terminal_to_prod_id.items():
            for id_ in ids:
                if non_terminal == self.get_production(id_)[1][0]:
                    return True
        return False

    def __get_left_recursion_free_production(self, nonTerminal, ids):
        subNonTerminal = nonTerminal + self.SUBSTITUTE
        grammarList, subGrammarList = [], []
        for id_ in ids:
            grammar = self.get_production(id_)[1]
            if nonTerminal == grammar[0]:
                subGrammarList.append(grammar[1:] + (subNonTerminal,))
            else:
                grammarList.append(grammar + (subNonTerminal,))
        return (nonTerminal, tuple(grammarList)), (
            subNonTerminal,
            tuple(subGrammarList),
        )

    def remove_left_recursion(self):
        """
        Return a new ContextFreeGrammar object, containing no left recursion.
        if:
            A -> A a1 | A a2 | A a3 | ... | b1 | b2 | b3 | ...
        then change to:
            A -> b1 A_ | b2 A_ | b3 A_ | ...
            A_ -> a1 A_ | a2 A_ | a3 A_ | ...
        """
        result_grammar_to_id = {}
        result_non_terminals = set(self.non_terminals)
        for non_terminal, ids in self.non_terminal_to_prod_id.items():
            is_recursive = False
            for id_ in ids:
                if non_terminal == self.get_production(id_)[1][0]:  # left recursive
                    is_recursive = True
                    break
            if is_recursive:
                (new_non_terminal, new_production), (
                    new_sub_non_terminal,
                    new_sub_production,
                ) = self.__get_left_recursion_free_production(non_terminal, ids)
                result_non_terminals.add(new_sub_non_terminal)
                for prod in new_production:
                    result_grammar_to_id[(new_non_terminal, prod)] = len(
                        result_grammar_to_id
                    )
                for prod in new_sub_production:
                    result_grammar_to_id[(new_sub_non_terminal, prod)] = len(
                        result_grammar_to_id
                    )
            else:
                for id_ in ids:
                    result_grammar_to_id[self.get_production(id_)] = len(
                        result_grammar_to_id
                    )
        return ContextFreeGrammar(
            self.terminals,
            result_non_terminals,
            self.start_symbol,
            result_grammar_to_id,
            self.raw_grammar_to_id,
        )

    def is_EOF(self, sym):
        return sym == -1

    def gen_first_set_of_symbol(self, result, symbol: str, firstDict=None) -> bool:
        """
        Calculate the first set of given symbol, and write the
        result into the reference of set "result".

        Return bool value, indicating whether the first of this
        symbol contains EMPTY or not.
        """
        if firstDict is not None:
            return firstDict[symbol]
        hasEmpty = False
        for production_id in self.get_productions(symbol):
            hasEmpty |= self.gen_first_set_of_sequence(
                result, self.get_production(production_id)[1], firstDict
            )
        return hasEmpty

    def gen_first_set_of_sequence(
        self, result, sequence: Iterable[str | int], first_dict=None
    ) -> bool:
        """
        Calculate the first set of given sequence and cfg.

        Use reference of set "result" to avoid newing temp sets
        to accelerate.
        """
        has_empty = False
        has_non_terminal = False
        all_non_terminal_has_empty = True
        for sym in sequence:
            if self.is_terminal(sym) or self.is_EOF(sym):
                result.add(sym)
                break
            elif self.is_non_terminal(sym):
                assert isinstance(sym, str)
                has_non_terminal = True
                if first_dict is not None:
                    result |= first_dict[sym]
                    all_non_terminal_has_empty &= self.EMPTY in first_dict[sym]
                else:
                    all_non_terminal_has_empty &= self.gen_first_set_of_symbol(
                        result, sym, first_dict
                    )
                if not all_non_terminal_has_empty:
                    break
            elif sym == self.EMPTY:
                result.add(self.EMPTY)
                has_empty = True
                break
        has_empty |= has_non_terminal and all_non_terminal_has_empty
        if not has_empty:
            result.discard(self.EMPTY)
        return has_empty

    def update_non_terminal_first_set(
        self, result: Dict[str, Set[str | int]], non_terminal: str
    ) -> bool:
        nt_has_empty = False
        for id_ in self.get_productions(non_terminal):
            has_non_terminal = False
            all_non_terminal_has_empty = True
            for sym in self.get_production(id_)[1]:
                if self.is_terminal(sym):
                    result[non_terminal].add(sym)
                    break
                elif self.is_non_terminal(sym):
                    assert isinstance(sym, str)
                    has_non_terminal = True
                    all_non_terminal_has_empty &= self.update_non_terminal_first_set(
                        result, sym
                    )
                    result[non_terminal] |= result[sym]
                    if not all_non_terminal_has_empty:
                        break
                elif sym == self.EMPTY:
                    nt_has_empty = True
                    break
            nt_has_empty |= has_non_terminal and all_non_terminal_has_empty
        if nt_has_empty:
            result[non_terminal].add(self.EMPTY)
        else:
            result[non_terminal].discard(self.EMPTY)
        return nt_has_empty

    def first(self) -> dict:
        """
        Calculate the first set of a given cfg
        """
        result = {k: set() for k in self.non_terminals}
        for non, _ in self.non_terminal_to_prod_id.items():
            if not result[non]:
                self.update_non_terminal_first_set(result, non)
        return result


class LRItem:

    """
    Is in fact a tri-tuple (production id, look forward, dot position)
    lookForward is a set, containing a set of id of terminals.
    """

    def __init__(self, production_id: int, look_forward: Set[int], dot_pos: int = 0):
        self.production_id = production_id
        self.dot_pos = dot_pos
        self.look_forward = look_forward  # WARNING: REFERENCE IS SHARED FOR
        # PERFORMANCE. AVOID EDITING THIS.
        self.__hash_val: Optional[int] = None

    def __eq__(self, other: Self):
        return (
            self.production_id == other.production_id
            and self.dot_pos == other.dot_pos
            and self.look_forward == other.look_forward
        )

    def __hash__(self) -> int:
        if self.__hash_val is None:
            self.__hash_val = hash(
                (
                    self.production_id,
                    self.dot_pos,
                    hash(tuple(sorted(list(self.look_forward), key=str))),
                )
            )
        return self.__hash_val

    def __str__(self):
        return "(%s, %r, %s)" % (self.production_id, self.look_forward, self.dot_pos)

    def __repr__(self):
        return repr(str(self))

    def __lt__(self, other: Self):
        """
        LRItemSet would need static order of LRItem to calculate hash.
        """
        if self.production_id == other.production_id:
            if self.dot_pos == other.dot_pos:
                return hash(self) < hash(other)
            return self.dot_pos < other.dot_pos
        return self.production_id < other.production_id

    def get(self, cfg: ContextFreeGrammar, offset=0):
        return cfg.get_symbol_in_prod(self.production_id, self.dot_pos, offset)

    def move_dot_forward(self):
        return LRItem(self.production_id, self.look_forward, self.dot_pos + 1)

    def at_end(self, cfg: ContextFreeGrammar) -> bool:
        prod = cfg.get_production(self.production_id)[1]
        return len(prod) == self.dot_pos or prod == ("",)


class LRItemSet:

    sequence_to_first: Dict[Tuple[str | int, ...], Set[int]] = {}

    def __init__(self):
        self.items: Set[LRItem] = set()
        self.__recalc_hash_flag = True  # lazy tag
        self.__hash_val = None
        self.__map = (
            {}
        )  # Map "step" to a list of item reference, in order to accelerate.

    def __hash__(self):
        if self.__recalc_hash_flag:
            self.__hash_val = hash(tuple(sorted(list(self.items))))  # TIME COSTING
            self.__recalc_hash_flag = False
        return self.__hash_val

    def __eq__(self, other):
        return self.items == other.items

    def __str__(self):
        return str(self.items)

    def add_lr_item(self, item: LRItem):
        if item not in self.items:
            self.items.add(item)
            self.__recalc_hash_flag = True

    def get_next(self, cfg: ContextFreeGrammar) -> Set[LRItem]:
        """
        get all possible out-pointing edges toward other LRItems, which could be later turned into LRItemSets.
        """
        result = set()
        for item in self.items:
            step = item.get(cfg)
            if step is not None and step != "":
                self.__map.setdefault(step, []).append(item)
                result.add(step)
        return result

    def goto(self, step):
        """
        return a new LRItemSet.
        """
        result = LRItemSet()
        for item in self.__map[step]:
            result.add_lr_item(item.move_dot_forward())
        return result

    def calc_closure(self, cfg: ContextFreeGrammar, firstDict: Dict) -> Self:
        """
        Return a new LRItemSet, which is the closure of self.
        """
        que = deque(self.items)
        record: Dict[Tuple[int, int], Set[int]] = {}
        while que:
            cur = que.pop()
            core = (cur.production_id, cur.dot_pos)
            record.setdefault(core, set())
            record[core] |= cur.look_forward

            cur_symbol = cur.get(cfg)  # symbol at current dot position

            if cfg.is_non_terminal(cur_symbol):
                assert isinstance(cur_symbol, str)
                prod = cfg.get_production(cur.production_id)[1][cur.dot_pos + 1 :]
                new_prods = (
                    prod + (lookForwardSym,) for lookForwardSym in cur.look_forward
                )  # precalc to accelerate

                for new_prod in new_prods:
                    if new_prod not in self.sequence_to_first:
                        first_set = set()
                        cfg.gen_first_set_of_sequence(first_set, new_prod, firstDict)
                        self.sequence_to_first[new_prod] = first_set
                    first_set = self.sequence_to_first[new_prod]
                    for production_id in cfg.get_productions(cur_symbol):
                        new_id_dot_pair = (production_id, 0)
                        if new_id_dot_pair not in record or not first_set.issubset(
                            record[new_id_dot_pair]
                        ):
                            que.append(LRItem(production_id, first_set, 0))

        result = LRItemSet()
        for (prod_id, dot_pos), v in record.items():
            result.add_lr_item(LRItem(prod_id, v, dot_pos))
        return result


class Action(ToJson):
    def __init__(self, cfg: ContextFreeGrammar, stateCount: int, table=None):
        self.state_count = stateCount
        self.terminals = cfg.terminals | {cfg.EOF}
        self.table: List[Dict[str, Optional[Tuple[int, int]]]] = (
            [
                {}
                for _ in range(self.state_count)
            ]
            if table is None
            else table
        )

    def __getitem__(self, item):
        return self.table[item]

    def __str__(self):
        terminals = self.terminals
        fmt = [len(str(_)) for _ in terminals]
        for i in range(self.state_count):
            for j, k in enumerate(terminals):
                fmt[j] = max(fmt[j], len(str(self.table[i].get(str(k), None))))
        str_fmt = list(map(lambda v: "%%%ds" % v, fmt))
        result = []
        result.append(
            "\t".join([" "] + [str_fmt[i] % str(k) for i, k in enumerate(terminals)])
        )
        for i in range(self.state_count):
            result.append(
                "\t".join(
                    [str(i)]
                    + [
                        str_fmt[j] % str(self.table[i].get(str(k), None))
                        for j, k in enumerate(terminals)
                    ]
                )
            )
        return "\n".join(result)

    def __contains__(self, item):
        return item in self.table

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.state_count

    def to_json(self):
        return {"state_count": self.state_count, "table": self.table}

    def save(self, fileName):
        with open(fileName, "w") as f:
            json.dump({"state_count": self.state_count, "table": self.table}, f)

    @staticmethod
    def loadFromString(cfg: ContextFreeGrammar, string):
        obj = json.loads(string)
        resultAction = Action(cfg, obj["stateCount"], table=obj["table"])
        return resultAction

    @staticmethod
    def load(cfg, fileName):
        with open(fileName, "r") as f:
            resultAction = Action.loadFromString(cfg, f.read())
        return resultAction


class Goto(ToJson):
    def __init__(
        self,
        cfg: ContextFreeGrammar,
        state_count: int,
        table: Optional[List[Dict[str, Any]]] = None,
    ):
        self.state_count = state_count
        self.non_terminals = cfg.non_terminals
        self.table: List[Dict[str, Optional[int]]] = (
            [{} for _ in range(self.state_count)]
            if table is None
            else table
        )

    def __getitem__(self, item: int):
        return self.table[item]

    def __str__(self):
        non_terminals = self.non_terminals
        fmt = [len(str(_)) for _ in non_terminals]
        for i in range(self.state_count):
            for j, k in enumerate(non_terminals):
                fmt[j] = max(fmt[j], len(str(self.table[i].get(k, None))))
        str_fmt = list(map(lambda v: "%%%ds" % v, fmt))
        result = []
        result.append(
            "\t".join(
                [" "] + [str_fmt[i] % str(k) for i, k in enumerate(non_terminals)]
            )
        )
        for i in range(self.state_count):
            result.append(
                "\t".join(
                    [str(i)]
                    + [
                        str_fmt[j] % str(self.table[i].get(k, None))
                        for j, k in enumerate(non_terminals)
                    ]
                )
            )
        return "\n".join(result)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.state_count

    def to_json(self):
        return {"state_count": self.state_count, "table": self.table}

    def save(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.to_json(), f)

    @staticmethod
    def loadFromString(cfg: ContextFreeGrammar, string):
        obj = json.loads(string)
        resultAction = Goto(cfg, obj["state_count"], table=obj["table"])
        return resultAction

    @staticmethod
    def load(cfg: ContextFreeGrammar, fileName):
        with open(fileName, "r") as f:
            resultGoto = Goto.loadFromString(cfg, f.read())
        return resultGoto


def gen_action_todo(cfg: ContextFreeGrammar) -> Tuple[Action, Goto]:
    cfg_for_first = cfg.remove_left_recursion() if cfg.is_left_recursive() else cfg
    first_dict = cfg_for_first.first()

    init_prod_id = cfg.non_terminal_to_prod_id[cfg.start_symbol][0]
    init_item = LRItem(init_prod_id, {-1}, 0)

    init_item_set = LRItemSet()
    init_item_set.add_lr_item(init_item)
    init_item_set = init_item_set.calc_closure(cfg, first_dict)

    que: Deque[LRItemSet] = deque([init_item_set])
    edges = {}

    item_set_to_id: Dict[LRItemSet, int] = {}
    core_to_closure = (
        {}
    )  # calculate closure is time-costing. Thus use a dict to accelerate.
    # NOTE: core means the pair of (production id, dot position)
    while que:
        cur = que.popleft()
        if cur not in item_set_to_id:
            item_set_to_id[cur] = len(item_set_to_id)
        for step in cur.get_next(cfg):
            next_item_set_core = cur.goto(step)  # get the core first

            if next_item_set_core not in core_to_closure:
                core_to_closure[next_item_set_core] = next_item_set_core.calc_closure(
                    cfg, first_dict
                )
            next_item_set = core_to_closure[next_item_set_core]

            if next_item_set not in item_set_to_id:
                item_set_to_id[next_item_set] = len(item_set_to_id)
                que.append(next_item_set)
            edges.setdefault(item_set_to_id[cur], []).append(
                (step, item_set_to_id[next_item_set])
            )

    action, goto = Action(cfg, len(item_set_to_id)), Goto(cfg, len(item_set_to_id))
    for src, v in edges.items():
        for step, dst in v:
            # src, step, dst forms a full edge. note that src and dst are int.
            if cfg.is_terminal(step):
                action[src][str(step)] = (0, dst)  # 0 means Shift
            elif cfg.is_non_terminal(step):
                goto[src][step] = dst

    for k, v in item_set_to_id.items():
        for item in k.items:
            if item.at_end(cfg):
                for sym in item.look_forward:
                    if item.production_id:
                        action[v][str(sym)] = (1, item.production_id)  # 1 means Reduce
                    else:
                        action[v][str(sym)] = (2, None)  # 2 means Accept
    return action, goto


if __name__ == "__main__":
    typedef = TypeDefinition.from_filename("simpleJava/typedef")
    cfg = ContextFreeGrammar.load(typedef, "simpleJava/simpleJavaCFG")
    print(cfg.terminals)
    print(cfg.non_terminals)
    print(cfg.start_symbol)
    print(cfg.grammar_to_id)
    print(cfg.raw_grammar_to_id)
    action, goto = gen_action_todo(cfg)
    print(action)
    print(goto)
