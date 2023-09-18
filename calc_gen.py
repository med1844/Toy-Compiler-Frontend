from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition
from production_fn_register import ProductionFnRegister
from typing import Dict, Any
import json


global d
d = {}

typedef = TypeDefinition.from_filename("simpleCalc/typedef")
cfg = ContextFreeGrammar.load(typedef, "simpleCalc/CFG4")
action, goto = gen_action_todo(cfg)
ar = ProductionFnRegister(cfg)


@ar.production("Statement -> E", "Statement -> Assignment")
def __stmt(_c, eval_result: int) -> int:
    return eval_result


@ar.production("E -> E + T")
def __e0(_c, e: int, _: str, t: int):
    return e + t


@ar.production("E -> E - T")
def __e1(_c, e: int, _: str, t: int):
    return e - t


@ar.production("E -> T", "T -> F", "F -> G")
def __e2(_c, b):
    return b


@ar.production("E -> - T")
def __e3(_c, _: str, t: int):
    return -t


@ar.production("T -> T * F")
def __t0(_c, t: int, _: str, f: int):
    return t * f


@ar.production("T -> T / F")
def __t1(_c, t: int, _: str, f: int):
    return t // f


@ar.production("T -> T % F")
def __t2(_c, t: int, _: str, f: int):
    return t % f


@ar.production("F -> F ** G")
def __f0(_c, f: int, _, g: int):
    return f**g


@ar.production("G -> ( E )")
def __g0(_, _leftPar: str, e: int, _rightPar: str):
    return e


@ar.production("G -> int_const")
def __g1(_, int_const: str):
    return int(int_const)


@ar.production("G -> id")
def __g2(context: Dict[str, Any], id_: str) -> int:
    return context[id_]


@ar.production("Assignment -> id = E")
def __assign(context: Dict[str, Any], id_: str, _: str, e: int):
    context[id_] = e
    return e


# action = Action.load(cfg, "simpleCalc/calc_action")
# goto = Goto.load(cfg, "simpleCalc/calc_goto")

ld = LangDef(
    list(map(lambda x: x.to_json(), typedef.get_dfa_list())),
    action.to_json(),
    goto.to_json(),
    ar.to_json(),
)

calc_ld_json = ld.to_json()
json.dump(calc_ld_json, open("calc.json", "w"))

# d = {}
#
# while True:
#     try:
#         inputString = input(">>> ")
#         print(ld.parse(ld.scan(inputString), d))
#         # pt = parser.parse(tokenList, typedef, cfg, action, goto)
#         # pt.evaluate(ar)
#
#     except EOFError:
#         break
