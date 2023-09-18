from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition
from typing import Dict, Any
import json


global d
d = {}

typedef = TypeDefinition.from_filename("simpleCalc/typedef")
cfg = ContextFreeGrammar.load(typedef, "simpleCalc/CFG2")
action, goto = gen_action_todo(cfg)

ld = LangDef(
    list(map(lambda x: x.to_json(), typedef.get_dfa_list())),
    cfg.raw_grammar_to_id,
    cfg.prod_id_to_nargs_and_non_terminal,
    action.to_json(),
    goto.to_json(),
)

calc_ld_json = ld.to_json()
json.dump(calc_ld_json, open("calc_v2.json", "w"))

