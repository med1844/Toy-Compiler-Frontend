from typing import Dict, List, Tuple
from cfg import ContextFreeGrammar, gen_action_todo, LangPrinter, LRItemSet


def test_lr1_table_0():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> A
        A -> A B | ''
        B -> "a" B | "b"
        """
    )
    dump_dst: List[Tuple[Dict[LRItemSet, int], Dict[int, Tuple[str | int, int]]]] = []
    action, goto = gen_action_todo(cfg, dump_dst)
    item_set_to_id, edges = dump_dst.pop()
    print(edges)
    lp = LangPrinter(cfg)
    for item_set, i in item_set_to_id.items():
        print(i)
        print(lp.to_string(item_set))
    assert False

