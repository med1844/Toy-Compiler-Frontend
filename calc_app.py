import json
from lang_def import LangDef

ld = LangDef.from_json(json.load(open("calc_v2.json", "r")))


@ld.production("E -> E + T")
def __e0(_c, e: int, _: str, t: int):
    return e + t


@ld.production("E -> E - T")
def __e1(_c, e: int, _: str, t: int):
    return e - t


@ld.production("E -> T")
def __e2(_c, b):
    return b


@ld.production("E -> - T")
def __e3(_c, _: str, t: int):
    return -t


@ld.production("T -> ( E )")
def __g0(_, _leftPar: str, e: int, _rightPar: str):
    return e


@ld.production("T -> int_const")
def __g1(_, int_const: str):
    return int(int_const)


while True:
    try:
        inputString = input(">>> ")
        print(ld.eval(inputString, {}))
    except EOFError:
        break
