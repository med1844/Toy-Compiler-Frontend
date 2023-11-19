from typing import Self, Tuple, Dict, Deque
from collections import deque

from cfg_utils.cfg import ContextFreeGrammar
from .lr1_item import LRItem
from .lr1_itemset import LRItemSet


class LRItemSetAutomata:
    def __init__(self, item_set_to_id: Dict[LRItemSet, int], edges: Dict[int, Tuple[str | int, int]]) -> None:
        self.item_set_to_id = item_set_to_id
        self.edges = edges

    @classmethod
    def new(cls, cfg: ContextFreeGrammar) -> Self:
        cfg_for_first = cfg.remove_left_recursion() if cfg.is_left_recursive() else cfg
        first_dict = cfg_for_first.first()

        init_prod_id = cfg.non_terminal_to_prod_id[cfg.start_symbol][0]
        init_item = LRItem(init_prod_id, {-1}, 0)

        seq_to_first_cache = {}

        init_item_set = LRItemSet()
        init_item_set.add_lr_item(init_item)
        init_item_set = init_item_set.calc_closure(cfg, first_dict, seq_to_first_cache)

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
                        cfg, first_dict, seq_to_first_cache
                    )
                next_item_set = core_to_closure[next_item_set_core]

                if next_item_set not in item_set_to_id:
                    item_set_to_id[next_item_set] = len(item_set_to_id)
                    que.append(next_item_set)
                edges.setdefault(item_set_to_id[cur], []).append(
                    (step, item_set_to_id[next_item_set])
                )

        return cls(item_set_to_id, edges)
