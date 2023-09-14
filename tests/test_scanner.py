from typeDef import TypeDefinition
from scanner import parse_by_dfa
from dfa_utils.finite_automata import FiniteAutomata


def test_scanner_0():
    # test match priority
    typedef = TypeDefinition()
    typedef.add_definition("mut", "mut")
    typedef.add_definition("identifier", "([a-zA-Z]|_)([0-9a-zA-Z]|_)*")
    assert parse_by_dfa(
        list(
            map(
                lambda r: FiniteAutomata.from_string(r[1], minimize=True), typedef.regex
            )
        ),
        "mut",
    ) == [(0, "mut")]


def test_scanner_1():
    typedef = TypeDefinition()
    typedef.add_definition("lifetime", "'([a-zA-Z]|_)([0-9a-zA-Z]|_)*")
    typedef.add_definition("char", "'.'")
    assert parse_by_dfa(
        list(
            map(
                lambda r: FiniteAutomata.from_string(r[1], minimize=True), typedef.regex
            )
        ),
        "'a '5' 'b 'c'",
    ) == [(0, "'a"), (1, "'5'"), (0, "'b"), (1, "'c'")]


def test_scanner_2():
    typedef = TypeDefinition()
    typedef.add_definition("select", "select")
    typedef.add_definition("from", "from")
    typedef.add_definition("where", "where")
    typedef.add_definition("and", "and")
    typedef.add_definition("or", "or")
    typedef.add_definition(",", ",")
    typedef.add_definition(".", r"\.")
    typedef.add_definition("*", r"\*")
    typedef.add_definition("==", "==")
    typedef.add_definition("!=", "!=")
    typedef.add_definition("<", "<")
    typedef.add_definition(">", ">")
    typedef.add_definition("(", r"\(")
    typedef.add_definition(")", r"\)")
    typedef.add_definition("str_literal", r"\"[^\"]*\"")
    typedef.add_definition("int_const", "(-?)(0|[1-9][0-9]*)")
    typedef.add_definition("id", "([a-zA-Z]|_)([a-zA-Z]|[0-9]|_)*")

    dfa_list = list(
        map(lambda r: FiniteAutomata.from_string(r[1], minimize=True), typedef.regex)
    )
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
            ],
        ),
    ):
        assert parse_by_dfa(dfa_list, in_) == out
