from dfa_utils.finite_automata_node import FiniteAutomataNode, CharTransition, EpsilonTransition, Transition
from dfa_utils.finite_automata import FiniteAutomata
from copy import deepcopy


def test_nfa_hash_0():
    # test if a back edge causes difference in the hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    e0.add_edge(EpsilonTransition(), s0)
    nfa_0 = FiniteAutomata(s0, {e0})

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = FiniteAutomata(s1, {e1})

    assert hash(nfa_0) != hash(nfa_1)


def test_nfa_hash_1():
    # make sure that the order we add edges doesn't effect hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    s0.add_edge(CharTransition("b"), e0)
    nfa_0 = FiniteAutomata(s0, {e0})

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("b"), e1)
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = FiniteAutomata(s1, {e1})

    assert hash(nfa_0) == hash(nfa_1)


def test_nfa_deepcopy_0():
    for regex in (
        "a*bcc|c*dee",
        "((a|b)*(cc|dd))*ee",
        "ac(bc|de)|ff",
        "a*",
        "a",
    ):
        a = FiniteAutomata.from_string(regex)
        b = deepcopy(a)
        assert hash(a) == hash(b)


def test_parsing_nfa_0():
    constructed_nfa = FiniteAutomata.from_string("a")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s.add_edge(CharTransition("a"), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_1():
    constructed_nfa = FiniteAutomata.from_string("a|b")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sb = FiniteAutomataNode()
    eb = FiniteAutomataNode()
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), sb)
    sa.add_edge(CharTransition("a"), ea)
    sb.add_edge(CharTransition("b"), eb)
    ea.add_edge(EpsilonTransition(), e)
    eb.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_2():
    constructed_nfa = FiniteAutomata.from_string("ab")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(CharTransition("b"), n3)
    expected_nfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_3():
    constructed_nfa = FiniteAutomata.from_string("a*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), sa)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_4():
    constructed_nfa = FiniteAutomata.from_string("a?")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_5():
    constructed_nfa = FiniteAutomata.from_string("(c|d)*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    sc = FiniteAutomataNode()
    ec = FiniteAutomataNode()
    sd = FiniteAutomataNode()
    ed = FiniteAutomataNode()

    sc.add_edge(CharTransition("c"), ec)
    sd.add_edge(CharTransition("d"), ed)

    s0.add_edge(EpsilonTransition(), sc)
    s0.add_edge(EpsilonTransition(), sd)

    ec.add_edge(EpsilonTransition(), e0)
    ed.add_edge(EpsilonTransition(), e0)

    e0.add_edge(EpsilonTransition(), s0)

    s.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), s0)

    e0.add_edge(EpsilonTransition(), e)

    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)

def test_parsing_nfa_6():
    constructed_nfa = FiniteAutomata.from_string("(ab*(c|d)*)|(e|(f*g))")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)

    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(EpsilonTransition(), n2)

    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n4.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n2)
    n3.add_edge(EpsilonTransition(), n5)

    n1.add_edge(EpsilonTransition(), n4)

    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n6.add_edge(CharTransition("c"), n7)

    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()
    n8.add_edge(CharTransition("d"), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()

    n10.add_edge(EpsilonTransition(), n6)
    n10.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n11)
    n9.add_edge(EpsilonTransition(), n11)

    n11.add_edge(EpsilonTransition(), n10)

    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n12.add_edge(EpsilonTransition(), n10)
    n12.add_edge(EpsilonTransition(), n13)
    n11.add_edge(EpsilonTransition(), n13)

    n5.add_edge(EpsilonTransition(), n12)

    n14 = FiniteAutomataNode()

    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n15.add_edge(CharTransition("e"), n16)

    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n17.add_edge(CharTransition("f"), n18)
    n18.add_edge(EpsilonTransition(), n17)

    n19 = FiniteAutomataNode()
    n20 = FiniteAutomataNode()
    n19.add_edge(EpsilonTransition(), n20)
    n19.add_edge(EpsilonTransition(), n17)
    n18.add_edge(EpsilonTransition(), n20)

    n14.add_edge(EpsilonTransition(), n15)
    n14.add_edge(EpsilonTransition(), n19)

    n21 = FiniteAutomataNode()
    n22 = FiniteAutomataNode()
    n21.add_edge(CharTransition("g"), n22)
    n20.add_edge(EpsilonTransition(), n21)

    n23 = FiniteAutomataNode()
    n16.add_edge(EpsilonTransition(), n23)
    n22.add_edge(EpsilonTransition(), n23)

    n24 = FiniteAutomataNode()
    n25 = FiniteAutomataNode()

    n24.add_edge(EpsilonTransition(), n0)
    n24.add_edge(EpsilonTransition(), n14)
    n13.add_edge(EpsilonTransition(), n25)
    n23.add_edge(EpsilonTransition(), n25)

    expected_nfa = FiniteAutomata(n24, {n25})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_7():
    constructed_nfa = FiniteAutomata.from_string("a+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n4.add_edge(CharTransition("a"), n5)
    n5.add_edge(EpsilonTransition(), n3)
    n5.add_edge(EpsilonTransition(), n4)

    expected_nfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_8():
    constructed_nfa = FiniteAutomata.from_string("(0|1|2|3)+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()

    n1.add_edge(CharTransition("0"), n2)
    n3.add_edge(CharTransition("1"), n4)
    n5.add_edge(CharTransition("2"), n6)
    n7.add_edge(CharTransition("3"), n8)

    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n3)
    n0.add_edge(EpsilonTransition(), n5)
    n0.add_edge(EpsilonTransition(), n7)
    n2.add_edge(EpsilonTransition(), n9)
    n4.add_edge(EpsilonTransition(), n9)
    n6.add_edge(EpsilonTransition(), n9)
    n8.add_edge(EpsilonTransition(), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n14 = FiniteAutomataNode()
    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n19 = FiniteAutomataNode()

    n11.add_edge(CharTransition("0"), n12)
    n13.add_edge(CharTransition("1"), n14)
    n15.add_edge(CharTransition("2"), n16)
    n17.add_edge(CharTransition("3"), n18)

    n10.add_edge(EpsilonTransition(), n11)
    n10.add_edge(EpsilonTransition(), n13)
    n10.add_edge(EpsilonTransition(), n15)
    n10.add_edge(EpsilonTransition(), n17)
    n12.add_edge(EpsilonTransition(), n19)
    n14.add_edge(EpsilonTransition(), n19)
    n16.add_edge(EpsilonTransition(), n19)
    n18.add_edge(EpsilonTransition(), n19)

    n19.add_edge(EpsilonTransition(), n10)

    n20 = FiniteAutomataNode()
    n21 = FiniteAutomataNode()

    n20.add_edge(EpsilonTransition(), n21)
    n20.add_edge(EpsilonTransition(), n10)
    n19.add_edge(EpsilonTransition(), n21)

    n9.add_edge(EpsilonTransition(), n20)

    expected_nfa = FiniteAutomata(n0, {n21})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_10():
    # test if ϵ is correctly handled
    constructed_nfa = FiniteAutomata.from_string("ϵ|a")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n0.add_edge(EpsilonTransition(), n1)
    n1.add_edge(EpsilonTransition(), n2)

    n0.add_edge(EpsilonTransition(), n3)
    n3.add_edge(CharTransition("a"), n4)

    n2.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n5)

    expected_nfa = FiniteAutomata(n0, {n5})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_11():
    constructed_nfa = FiniteAutomata.from_string("d(ϵ|ab)")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n0.add_edge(CharTransition("d"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n3.add_edge(EpsilonTransition(), n5)
    n4.add_edge(CharTransition("a"), n6)
    n6.add_edge(EpsilonTransition(), n11)
    n11.add_edge(CharTransition("b"), n7)
    n5.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n8)

    expected_nfa = FiniteAutomata(n0, {n8})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_12():
    # test \, they should help recognize *, (, ), [, ], |, +, ?, etc
    for regex in (
        "*", "(", ")", "[", "]", "|", "+", "?", "."
    ):
        constructed_nfa = FiniteAutomata.from_string("\\" + regex)
        n0 = FiniteAutomataNode()
        n1 = FiniteAutomataNode()
        n0.add_edge(CharTransition(regex), n1)
        expected_nfa = FiniteAutomata(n0, {n1})
        assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_13():
    constructed_nfa = FiniteAutomata.from_string("[0-3]+")
    expected_nfa = FiniteAutomata.from_string("(0|1|2|3)+")
    assert hash(constructed_nfa) != hash(expected_nfa)  # now it's based on ranges


def test_parsing_nfa_14():
    constructed_nfa = FiniteAutomata.from_string("'[^b]*'")
    expected_nfa = FiniteAutomata.from_string("'[ -ac-~]*'")
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_15():
    constructed_nfa = FiniteAutomata.from_string(r"'[^\']*'")
    expected_nfa = FiniteAutomata.from_string(r"'[ -&(-~]*'")
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_16():
    constructed_nfa = FiniteAutomata.from_string(r"[a-zA-Z0-9]")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(Transition(range(ord("a"), ord("z") + 1), range(ord("A"), ord("Z") + 1), range(ord("0"), ord("9") + 1)), n1)
    expected_nfa = FiniteAutomata(n0, {n1})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_fa_rev_edge_0():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n0)
    fa = FiniteAutomata(n0, {n1})
    constructed_fa_rev = fa.reverse_edge()

    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n2.add_edge(EpsilonTransition(), n3)
    n3.add_edge(CharTransition("a"), n2)
    expected_fa_rev = FiniteAutomata(n3, {n2})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_fa_rev_edge_1():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)

    fa = FiniteAutomata(n0, {n2})
    constructed_fa_rev = fa.reverse_edge()

    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n5.add_edge(CharTransition("b"), n4)
    n4.add_edge(CharTransition("a"), n3)

    expected_fa_rev = FiniteAutomata(n5, {n3})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_fa_hash_0():
    # try attack hash function
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n2)
    n1.add_edge(CharTransition("a"), n2)
    n2.add_edge(CharTransition("b"), n1)

    m0 = FiniteAutomataNode()
    m1 = FiniteAutomataNode()
    m2 = FiniteAutomataNode()
    m0.add_edge(EpsilonTransition(), m2)
    m0.add_edge(EpsilonTransition(), m1)
    m1.add_edge(CharTransition("a"), m2)
    m2.add_edge(CharTransition("b"), m1)

    assert hash(FiniteAutomata(n0)) == hash(FiniteAutomata(m0))


def test_fa_hash_1():
    # test if hash function captures self-loop (edge that goes to itself...)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("a"), n0)

    m0 = FiniteAutomataNode()
    m1 = FiniteAutomataNode()
    m0.add_edge(CharTransition("a"), m1)

    assert hash(FiniteAutomata(n0)) != hash(FiniteAutomata(m0))


def test_fa_repr():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    fa = FiniteAutomata(n0)
    r = repr(fa)
    assert r.strip() == "0 -a> 1"


def test_dfa_0():
    constructed_dfa = FiniteAutomata.from_string("a").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_1():
    constructed_dfa = FiniteAutomata.from_string("a|b").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n2)
    expected_dfa = FiniteAutomata(n0, {n1, n2})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_2():
    constructed_dfa = FiniteAutomata.from_string("a*").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_3():
    constructed_dfa = FiniteAutomata.from_string("a?").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_4():
    constructed_dfa = FiniteAutomata.from_string("abc").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_5():
    constructed_dfa = FiniteAutomata.from_string("pub|pri").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n0.add_edge(CharTransition("p"), n1)
    n1.add_edge(CharTransition("u"), n2)
    n1.add_edge(CharTransition("r"), n4)
    n2.add_edge(CharTransition("b"), n3)
    n4.add_edge(CharTransition("i"), n5)
    expected_dfa = FiniteAutomata(n0, {n3, n5})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_6():
    # test if middle accepts are recognized
    constructed_dfa = FiniteAutomata.from_string("a|abc").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = FiniteAutomata(n0, {n1, n3})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_7():
    constructed_dfa = FiniteAutomata.from_string("a+").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)  # {0}
    n1.add_edge(CharTransition("a"), n2)  # {1, 2, 4, 3}
    n2.add_edge(CharTransition("a"), n2)  # {5, 4, 3}
    expected_dfa = FiniteAutomata(n0, {n1, n2})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_8():
    constructed_dfa = FiniteAutomata.from_string(".*").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(Transition(range(ord("\n")), range(ord("\n") + 1, 0x7f)), n1)
    n1.add_edge(Transition(range(ord("\n")), range(ord("\n") + 1, 0x7f)), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_min_dfa_0():
    # the result of (a|b)+ could be further simplified by DFA minimization
    constructed_dfa = FiniteAutomata.from_string("abb(a|b)+", minimize=True)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(Transition(range(ord("a"), ord("b") + 1)), n4)
    n4.add_edge(Transition(range(ord("a"), ord("b") + 1)), n4)

    expected_dfa = FiniteAutomata(n0, {n4})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_min_dfa_1():
    # NOTE: this is NOT MINIMAL, but almost.
    # it's caused by manually added start_node that connects to all accept states.
    # e.g. consider DFA (0) -ab> (1), (1) -ab> (1). The reversed NFA would be
    # 2 -ϵ> 1, 2 -ϵ> (0), 1 -ab> 1, 1 -ab> (0).
    # Thus the ϵ-closure would be {2, 1, 0} -ab> {1, 0}, {1, 0} -ab> {1, 0},
    # which corresponds to n0 & n1 down there.
    # TODO: Try to find a way to eliminate that redundant node, e.g. remove start_node from closure?
    constructed_dfa = FiniteAutomata.from_string("((ϵ|a)b*)*", minimize=True)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(Transition(range(ord("a"), ord("b") + 1)), n1)
    n1.add_edge(Transition(range(ord("a"), ord("b") + 1)), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_iter_0():
    dfa = FiniteAutomata.from_string("a*", minimize=True)
    for target, expected in (
        ("aabaaabba", "aa"),
        ("baaaa", "")
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_1():
    dfa = FiniteAutomata.from_string("0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*", minimize=True)
    for target, expected in (
        ("10872865 168505", "10872865"),
        ("010101", "0"),
        ("7950X3D", "7950")
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_2():
    dfa = FiniteAutomata.from_string("([a-zA-Z]|_)([a-zA-Z0-9]|_)*", minimize=True)
    for target, expected in (
        ("FiniteAutomata.from_string('a*')", "FiniteAutomata"),
        ("__init__(self)", "__init__"),
        ("n7.add_edge(CharTransition('b'), n7)", "n7"),
        ("1 + 2", "")
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_3():
    dfa = FiniteAutomata.from_string(r"/\*.*\*/", minimize=True)

    for target, expected in (
        ("/* ([a-zA-Z]|_)([a-zA-Z0-9]|_)* */", "/* ([a-zA-Z]|_)([a-zA-Z0-9]|_)* */"),
        ("/*comment*/?ok", "/*comment*/"),
        ("int i = 0; /* initialize index var */", "")
    ):
        assert dfa.match_first(target) == expected


def test_dfa_rev_edge_0():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("a"), n1)
    n2.add_edge(CharTransition("b"), n2)

    fa = FiniteAutomata(n0, {n1})
    constructed_fa_rev = fa.reverse_edge()

    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n4.add_edge(CharTransition("a"), n3)
    n4.add_edge(CharTransition("a"), n5)
    n5.add_edge(CharTransition("b"), n5)
    n5.add_edge(CharTransition("b"), n3)

    expected_fa_rev = FiniteAutomata(n4, {n3})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_dfa_rev_edge_1():
    constructed_fa_rev = FiniteAutomata.from_string("a|b*").determinize().reverse_edge()

    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n1.add_edge(CharTransition("a"), n0)
    n2.add_edge(CharTransition("b"), n0)
    n2.add_edge(CharTransition("b"), n2)
    n3.add_edge(EpsilonTransition(), n0)
    n3.add_edge(EpsilonTransition(), n1)
    n3.add_edge(EpsilonTransition(), n2)

    expected_fa_rev = FiniteAutomata(n3, {n0})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_split_by():
    assert FiniteAutomata.split_by(range(1, 100), [5, 6, 10, 14, 20, 50, 98]) == [range(1, 5), range(5, 6), range(6, 10), range(10, 14), range(14, 20), range(20, 50), range(50, 98), range(98, 100)]


def test_determinize_split_by_0():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()

    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n3)
    n0.add_edge(EpsilonTransition(), n5)

    n1.add_edge(Transition(range(ord("c"), ord("e") + 1)), n2)
    n3.add_edge(Transition(range(ord("b"), ord("c") + 1), range(ord("e"), ord("e") + 1)), n4)
    n5.add_edge(Transition(range(ord("c"), ord("c") + 1), range(ord("f"), ord("f") + 1)), n6)

    n2.add_edge(EpsilonTransition(), n7)
    n4.add_edge(EpsilonTransition(), n7)
    n6.add_edge(EpsilonTransition(), n7)

    constructed_dfa = FiniteAutomata(n0, {n7}).determinize()

    n0135 = FiniteAutomataNode()
    n27 = FiniteAutomataNode()
    n47 = FiniteAutomataNode()
    n247 = FiniteAutomataNode()
    n67 = FiniteAutomataNode()
    n2467 = FiniteAutomataNode()

    n0135.add_edge(CharTransition("d"), n27)
    n0135.add_edge(CharTransition("b"), n47)
    n0135.add_edge(CharTransition("e"), n247)
    n0135.add_edge(CharTransition("f"), n67)
    n0135.add_edge(CharTransition("c"), n2467)

    expected_dfa = FiniteAutomata(n0135, {n27, n47, n247, n67, n2467})

    assert hash(constructed_dfa) == hash(expected_dfa)

