from dfa_utils.finite_automata import FiniteAutomata
from dfa_utils.finite_automata_set import FiniteAutomataSet


def test_fa_set_match_one_0():
    s = FiniteAutomataSet(
        [
            FiniteAutomata.from_string("aa"),
            FiniteAutomata.from_string("a"),
        ]
    )

    assert s.match_one("aaa") == "aa"


def test_fa_set_match_one_1():
    s = FiniteAutomataSet(
        [
            FiniteAutomata.from_string("a"),
            FiniteAutomata.from_string("aa"),
        ]
    )

    assert s.match_one("aaa") == "aa"


def test_fa_set_match_one_2():
    s = FiniteAutomataSet(
        [
            FiniteAutomata.from_string(r"\+"),
            FiniteAutomata.from_string("-"),
            FiniteAutomata.from_string(r"\*"),
            FiniteAutomata.from_string(r"\("),
            FiniteAutomata.from_string(r"\)"),
            FiniteAutomata.from_string(r"0|(-?)[1-9][0-9]*"),
        ]
    )

    assert s.match_one("(5 + 6) * 7") == "("
    assert s.match_one("-35 - 6") == "-35"


def test_fa_set_match_one_3():
    s = FiniteAutomataSet(
        [
            FiniteAutomata.from_string("mut"),
            FiniteAutomata.from_string("([a-zA-Z]|_)([0-9a-zA-Z]|_)*"),
        ]
    )

    assert s.match_one("mut a: Arc<Mutex<i32>>") == "mut"
    assert s.match_one("Arc<Mutex<i32>>") == "Arc"
