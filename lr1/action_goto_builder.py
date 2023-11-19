from typing import Tuple

from cfg_utils.cfg import ContextFreeGrammar
from .lr1_itemset_automata import LRItemSetAutomata
from .action import Action
from .goto import Goto


class ActionGotoBuilder:
    @staticmethod
    def new(
        cfg: ContextFreeGrammar, lr_item_set_automata: LRItemSetAutomata
    ) -> Tuple[Action, Goto]:
        action, goto = Action(cfg, len(lr_item_set_automata.item_set_to_id)), Goto(
            cfg, len(lr_item_set_automata.item_set_to_id)
        )
        for src, v in lr_item_set_automata.edges.items():
            for step, dst in v:
                # src, step, dst forms a full edge. note that src and dst are int.
                if cfg.is_terminal(step):
                    action[src][str(step)] = (0, dst)  # 0 means Shift
                elif cfg.is_non_terminal(step):
                    goto[src][step] = dst

        for k, v in lr_item_set_automata.item_set_to_id.items():
            for item in k.items:
                if item.at_end(cfg):
                    for sym in item.look_forward:
                        if item.production_id:
                            action[v][str(sym)] = (
                                1,
                                item.production_id,
                            )  # 1 means Reduce
                        else:
                            action[v][str(sym)] = (2, None)  # 2 means Accept
        return action, goto
