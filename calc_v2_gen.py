from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition
from production_fn_register import ProductionFnRegister
from typing import Dict, Any
import json


global d
d = {}

typedef = TypeDefinition.from_filename("simpleCalc/typedef")
cfg = ContextFreeGrammar.load(typedef, "simpleCalc/CFG2")
action, goto = gen_action_todo(cfg)
ar = ProductionFnRegister(cfg)


@ar.production("E -> E + T")
def __e0(_c, e: int, _: str, t: int):
    return e + t


@ar.production("E -> E - T")
def __e1(_c, e: int, _: str, t: int):
    return e - t


@ar.production("E -> T")
def __e2(_c, b):
    return b


@ar.production("E -> - T")
def __e3(_c, _: str, t: int):
    return -t


@ar.production("T -> ( E )")
def __g0(_, _leftPar: str, e: int, _rightPar: str):
    return e


@ar.production("T -> int_const")
def __g1(_, int_const: str):
    return int(int_const)


ld = LangDef(
    list(map(lambda x: x.to_json(), typedef.get_dfa_list())),
    action.to_json(),
    goto.to_json(),
    ar.to_json(),
)

calc_ld_json = ld.to_json()
json.dump(calc_ld_json, open("calc_v2.json", "w"))

