from dfa_utils.finite_automata_node import EpsilonTransition, CharTransition, Transition


def test_epsilon_transition():
    a = EpsilonTransition()
    b = EpsilonTransition()
    assert a == b

    for i in range(0, 1000):
        assert a(chr(i)) == True


def test_char_transition():
    a = CharTransition("a")
    b = CharTransition("a")
    assert a == b
    c = CharTransition("b")
    d = CharTransition("b")
    assert c == d
    assert a != c
    e = CharTransition("a")
    assert a == e


def test_make_unique():
    a = Transition(range(1, 2), range(1, 10), range(11, 12), range(12, 14), range(30, 35), range(28, 32))
    assert a.ranges == ((range(1, 10), range(11, 14), range(28, 35)))


def test_transition_partial_ord():
    for a, b in (
        (Transition(range(5, 6)), Transition(range(5, 6))),
        (Transition(range(5, 6)), Transition(range(5, 7))),
        (Transition(range(5, 6)), Transition(range(4, 6))),
        (Transition(range(5, 8)), Transition(range(3, 6), range(6, 10))),
        (Transition(range(5, 8), range(6, 12), range(37, 50), range(99, 125)), Transition(range(128)))
    ):
        assert a <= b

