from typing import Set, Dict, Tuple, Self
from cfg_utils.cfg import ContextFreeGrammar
from .lr1_item import LRItem
from collections import deque


class LRItemSet:

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

    def __repr__(self) -> str:
        return repr(self.items)

    def add_lr_item(self, item: LRItem):
        if item not in self.items:
            self.items.add(item)
            self.__recalc_hash_flag = True

    def get_next(self, cfg: ContextFreeGrammar) -> Set[int | str]:
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

    def calc_closure(self, cfg: ContextFreeGrammar, first_dict: Dict, seq_to_first_cache: Dict[Tuple[str | int, ...], Set[int]] = dict()) -> Self:
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
                non_terminal = cfg.get_production(cur.production_id)[0]
                prod = cfg.get_production(cur.production_id)[1][cur.dot_pos + 1 :]
                new_prods = (
                    prod + (lookForwardSym,) for lookForwardSym in cur.look_forward
                )  # precalc to accelerate

                for new_prod in new_prods:
                    if new_prod not in seq_to_first_cache:
                        first_set = set()
                        cfg.gen_first_set_of_sequence(first_set, non_terminal, new_prod, first_dict)
                        seq_to_first_cache[new_prod] = first_set
                    first_set = seq_to_first_cache[new_prod]
                    for production_id in cfg.get_productions(cur_symbol):
                        new_id_dot_pair = (production_id, 0)
                        if new_id_dot_pair not in record or not first_set.issubset(
                            record[new_id_dot_pair]
                        ):
                            que.append(LRItem(production_id, first_set, 0))

        result = LRItemSet()
        for (prod_id, dot_pos), v in record.items():
            result.add_lr_item(LRItem(prod_id, {val for val in v if val != ''}, dot_pos))
        return result
