from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition
from typing import Dict, Any


global d
d = {}

typedef = TypeDefinition.from_filename("simpleCalc/typedef")
cfg = ContextFreeGrammar.load(typedef, "simpleCalc/CFG4")
action, goto = gen_action_todo(cfg)

ld = LangDef(
    list(map(lambda x: x.to_json(), typedef.get_dfa_list())),
    cfg.raw_grammar_to_id,
    cfg.prod_id_to_nargs_and_non_terminal,
    action.to_json(),
    goto.to_json(),
)


@ld.production("E -> E + T")
def __e0(_c, e: int, _: str, t: int):
    return e + t


@ld.production("E -> E - T")
def __e1(_c, e: int, _: str, t: int):
    return e - t


@ld.production("E -> T", "T -> F", "F -> G", "Statement -> Assignment", "Statement -> E")
def __e2(_c, b):
    return b


@ld.production("E -> - T")
def __e3(_c, _: str, t: int):
    return -t


@ld.production("T -> T * F")
def __t0(_c, t: int, _: str, f: int):
    return t * f


@ld.production("T -> T / F")
def __t1(_c, t: int, _: str, f: int):
    return t // f


@ld.production("T -> T % F")
def __t2(_c, t: int, _: str, f: int):
    return t % f


@ld.production("F -> F ** G")
def __f0(_c, f: int, _, g: int):
    return f**g


@ld.production("G -> ( E )")
def __g0(_, _leftPar: str, e: int, _rightPar: str):
    return e


@ld.production("G -> int_const")
def __g1(_, int_const: str):
    return int(int_const)


@ld.production("G -> id")
def __g2(context: Dict[str, Any], id_: str) -> int:
    return context[id_]


@ld.production("Assignment -> id = E")
def __assign(context: Dict[str, Any], id_: str, _: str, e: int):
    context[id_] = e
    return e


while True:
    try:
        inputString = input(">>> ")
        print(ld.eval(inputString, {}))
    except EOFError:
        break
