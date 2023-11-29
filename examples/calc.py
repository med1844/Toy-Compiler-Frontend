import sys
import os
from lang_def_builder import LangDefBuilder


sys.path.append(os.path.dirname(os.path.dirname(__file__)))


ld = LangDefBuilder.new(
    """
    START -> E
    E -> E "+" T | E "-" T | T
    T -> T "*" F | F
    F -> "(" E ")" | int_const
    int_const -> r"0|(-?)[1-9][0-9]*"
    """
)


@ld.production("E -> T", "T -> F", "F -> int_const")
def __identity(_, e: int) -> int:
    return e


@ld.production('E -> E "+" T')
def __add(_, e: int, _p: str, t: int) -> int:
    return e + t


@ld.production('E -> E "-" T')
def __sub(_, e: int, _m: str, t: int) -> int:
    return e - t


@ld.production('T -> T "*" F')
def __mul(_, t: int, _m: str, f: int) -> int:
    return t * f


@ld.production('F -> "(" E ")"')
def __par(_, _l, e: int, _r) -> int:
    return e


@ld.production('int_const -> r"0|(-?)[1-9][0-9]*"')
def __int(_, int_const: str) -> int:
    return int(int_const)


while True:
    try:
        print(ld.eval(input(">>> "), {}))
    except EOFError:
        break
