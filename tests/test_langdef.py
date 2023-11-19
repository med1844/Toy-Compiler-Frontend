from dataclasses import dataclass
import json
from typing import Optional
from lang_def import LangDef
from lang_def_builder import LangDefBuilder
from cfg_utils.type_def import TypeDefinition
from cfg_utils.cfg import ContextFreeGrammar
import pytest
from random import randint, shuffle
from operator import add, sub, mul


def test_ld_scanner_0():
    # test match priority
    typedef = TypeDefinition()
    typedef.add_definition("mut")
    typedef.add_definition("([a-zA-Z]|_)([0-9a-zA-Z]|_)*", True)
    ld = LangDef(typedef.get_dfa_set().to_json(), {}, {}, {}, {})
    assert ld.scan("mut") == [(0, "mut"), (-1, "$")]


def test_ld_scanner_1():
    typedef = TypeDefinition()
    typedef.add_definition("'([a-zA-Z]|_)([0-9a-zA-Z]|_)*", True)
    typedef.add_definition("'.'", True)
    ld = LangDef(typedef.get_dfa_set().to_json(), {}, {}, {}, {})
    assert ld.scan("'a '5' 'b 'c'") == [
        (0, "'a"),
        (1, "'5'"),
        (0, "'b"),
        (1, "'c'"),
        (-1, "$"),
    ]


def test_ld_scanner_2():
    typedef = TypeDefinition()
    typedef.add_definition("select")
    typedef.add_definition("from")
    typedef.add_definition("where")
    typedef.add_definition("and")
    typedef.add_definition("or")
    typedef.add_definition(",")
    typedef.add_definition(".")
    typedef.add_definition("*")
    typedef.add_definition("==")
    typedef.add_definition("!=")
    typedef.add_definition("<")
    typedef.add_definition(">")
    typedef.add_definition("(")
    typedef.add_definition(")")
    typedef.add_definition(r"\"[^\"]*\"", True)
    typedef.add_definition("(-?)(0|[1-9][0-9]*)", True)
    typedef.add_definition("([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*", True)

    ld = LangDef(typedef.get_dfa_set().to_json(), {}, {}, {}, {})
    for in_, out in (
        (
            'select * from whatever where column1 != column2 and (column4 == "some literal" or column3 < 5)',
            [
                (0, "select"),
                (7, "*"),
                (1, "from"),
                (16, "whatever"),
                (2, "where"),
                (16, "column1"),
                (9, "!="),
                (16, "column2"),
                (3, "and"),
                (12, "("),
                (16, "column4"),
                (8, "=="),
                (14, '"some literal"'),
                (4, "or"),
                (16, "column3"),
                (10, "<"),
                (15, "5"),
                (13, ")"),
                (-1, "$"),
            ],
        ),
        (
            "select c.a, d.b from c, d where c.key == d.foreign_key",
            [
                (0, "select"),
                (16, "c"),
                (6, "."),
                (16, "a"),
                (5, ","),
                (16, "d"),
                (6, "."),
                (16, "b"),
                (1, "from"),
                (16, "c"),
                (5, ","),
                (16, "d"),
                (2, "where"),
                (16, "c"),
                (6, "."),
                (16, "key"),
                (8, "=="),
                (16, "d"),
                (6, "."),
                (16, "foreign_key"),
                (-1, "$"),
            ],
        ),
    ):
        assert ld.scan(in_) == out


def test_ld_scanner_3():
    typedef = TypeDefinition()
    typedef.add_definition("fn")
    typedef.add_definition("(")
    typedef.add_definition(")")
    typedef.add_definition("[")
    typedef.add_definition("]")
    typedef.add_definition("{")
    typedef.add_definition("}")
    typedef.add_definition("&")
    typedef.add_definition("|=")
    typedef.add_definition("|")
    typedef.add_definition("mut")
    typedef.add_definition("let")
    typedef.add_definition("for")
    typedef.add_definition("in")
    typedef.add_definition("::")
    typedef.add_definition(":")
    typedef.add_definition(";")
    typedef.add_definition("..")
    typedef.add_definition(".")
    typedef.add_definition(",")
    typedef.add_definition("<<")
    typedef.add_definition("<<=")
    typedef.add_definition(">>")
    typedef.add_definition(">>=")
    typedef.add_definition("<")
    typedef.add_definition(">")
    typedef.add_definition("(-?)(0|[1-9][0-9]*)", True)
    typedef.add_definition("([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*", True)

    ld = LangDef(typedef.get_dfa_set().to_json(), {}, {}, {}, {})

    assert (
        ld.scan(
            """fn game_of_life(board: &mut Vec<Vec<i32>>) {
        for i in 0..board.len() {
            for j in 0..board.get(0).unwrap().len() {
                board[i][j] |= Self::get_cell_next_state(
                    board[i][j],
                    Self::get_live_neighbor_num(board, i, j),
                ) << 1;
            }
        }
        for i in 0..board.len() {
            for j in 0..board.get(0).unwrap().len() {
                board[i][j] >>= 1;
            }
        }
    }
    """
        )
        == [
            (0, "fn"),
            (27, "game_of_life"),
            (1, "("),
            (27, "board"),
            (15, ":"),
            (7, "&"),
            (10, "mut"),
            (27, "Vec"),
            (24, "<"),
            (27, "Vec"),
            (24, "<"),
            (27, "i32"),
            (22, ">>"),  # i know this is problematic...
            (2, ")"),
            (5, "{"),
            (12, "for"),
            (27, "i"),
            (13, "in"),
            (26, "0"),
            (17, ".."),
            (27, "board"),
            (18, "."),
            (27, "len"),
            (1, "("),
            (2, ")"),
            (5, "{"),
            (12, "for"),
            (27, "j"),
            (13, "in"),
            (26, "0"),
            (17, ".."),
            (27, "board"),
            (18, "."),
            (27, "get"),
            (1, "("),
            (26, "0"),
            (2, ")"),
            (18, "."),
            (27, "unwrap"),
            (1, "("),
            (2, ")"),
            (18, "."),
            (27, "len"),
            (1, "("),
            (2, ")"),
            (5, "{"),
            (27, "board"),
            (3, "["),
            (27, "i"),
            (4, "]"),
            (3, "["),
            (27, "j"),
            (4, "]"),
            (8, "|="),
            (27, "Self"),
            (14, "::"),
            (27, "get_cell_next_state"),
            (1, "("),
            (27, "board"),
            (3, "["),
            (27, "i"),
            (4, "]"),
            (3, "["),
            (27, "j"),
            (4, "]"),
            (19, ","),
            (27, "Self"),
            (14, "::"),
            (27, "get_live_neighbor_num"),
            (1, "("),
            (27, "board"),
            (19, ","),
            (27, "i"),
            (19, ","),
            (27, "j"),
            (2, ")"),
            (19, ","),
            (2, ")"),
            (20, "<<"),
            (26, "1"),
            (16, ";"),
            (6, "}"),
            (6, "}"),
            (12, "for"),
            (27, "i"),
            (13, "in"),
            (26, "0"),
            (17, ".."),
            (27, "board"),
            (18, "."),
            (27, "len"),
            (1, "("),
            (2, ")"),
            (5, "{"),
            (12, "for"),
            (27, "j"),
            (13, "in"),
            (26, "0"),
            (17, ".."),
            (27, "board"),
            (18, "."),
            (27, "get"),
            (1, "("),
            (26, "0"),
            (2, ")"),
            (18, "."),
            (27, "unwrap"),
            (1, "("),
            (2, ")"),
            (18, "."),
            (27, "len"),
            (1, "("),
            (2, ")"),
            (5, "{"),
            (27, "board"),
            (3, "["),
            (27, "i"),
            (4, "]"),
            (3, "["),
            (27, "j"),
            (4, "]"),
            (23, ">>="),
            (26, "1"),
            (16, ";"),
            (6, "}"),
            (6, "}"),
            (6, "}"),
            (-1, "$"),
        ]
    )


@pytest.fixture
def gen_calc():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> E
        E -> E "+" T | E "-" T | T
        T -> T "*" F | F
        F -> "(" E ")" | int_const
        int_const -> r"0|(-?)[1-9][0-9]*"
        """,
    )
    ld = LangDefBuilder.new(cfg)

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

    yield ld


def test_lang_to_from_json(gen_calc: LangDef):
    reconstructed_ld = LangDef.from_json(json.loads(json.dumps(gen_calc.to_json())))

    @reconstructed_ld.production("E -> T", "T -> F", "F -> int_const")
    def __identity(_, e: int) -> int:
        return e

    @reconstructed_ld.production('E -> E "+" T')
    def __add(_, e: int, _p: str, t: int) -> int:
        return e + t

    @reconstructed_ld.production('E -> E "-" T')
    def __sub(_, e: int, _m: str, t: int) -> int:
        return e - t

    @reconstructed_ld.production('T -> T "*" F')
    def __mul(_, t: int, _m: str, f: int) -> int:
        return t * f

    @reconstructed_ld.production('F -> "(" E ")"')
    def __par(_, _l, e: int, _r) -> int:
        return e

    @reconstructed_ld.production('int_const -> r"0|(-?)[1-9][0-9]*"')
    def __int(_, int_const: str) -> int:
        return int(int_const)

    l = [randint(0, 10) for _ in range(50)]
    in_ = " + ".join(map(str, l))
    assert gen_calc.eval(in_) == reconstructed_ld.eval(in_) == sum(l)


def test_calc(gen_calc: LangDef):
    @dataclass
    class ExpNode:
        l: Optional["ExpNode"]
        r: Optional["ExpNode"]
        val: int

    leaves = [ExpNode(None, None, randint(-15, 15)) for _ in range(50)]
    while len(leaves) >= 2:
        r, l = leaves.pop(), leaves.pop()
        par = ExpNode(l, r, randint(1000, 1002))
        leaves.append(par)
        shuffle(leaves)

    def gen_exp(node: Optional[ExpNode]) -> str:
        match node:
            case None:
                return ""
            case ExpNode():
                if node.l is None and node.r is None:
                    return "%d" % node.val
                else:
                    return "(%s %s %s)" % (
                        gen_exp(node.l),
                        "+-*"[node.val - 1000],
                        gen_exp(node.r),
                    )

    def eval_node(node: ExpNode) -> int:
        if node.l is not None and node.r is not None:
            return (add, sub, mul)[node.val - 1000](
                eval_node(node.l), eval_node(node.r)
            )
        else:
            return node.val

    root = leaves.pop()
    exp = gen_exp(root)
    val = eval_node(root)
    assert gen_calc.eval(exp) == val
