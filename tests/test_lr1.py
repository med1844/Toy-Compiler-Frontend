from typing import List, Tuple
from cfg_utils.cfg import ContextFreeGrammar
from lr1.lr1_itemset_automata import LRItemSetAutomata
from lr1.lr1_io import LRItemSetPrinter, LRItemSetParser, LRItemParser, SymbolParser


def test_lr1_io_split_lookforward():
    assert list(
        LRItemParser.look_forward_tokenizer(r'"("/"*"/$/r"\"[^\"]*\""/r"\'[^\']\'"')
    ) == ['"("', '"*"', "$", r'r"\"[^\"]*\""', r'r"\'[^\']\'"']
    assert list(
        LRItemParser.look_forward_tokenizer(
            r'","/"."/r"([a-zA-Z]|\_)([a-zA-Z]|[0-9]|\_)*"/r"\"[^\"]*\""/r"\'[^\']*\'"'
        )
    ) == [
        '","',
        '"."',
        r'r"([a-zA-Z]|\_)([a-zA-Z]|[0-9]|\_)*"',
        r'r"\"[^\"]*\""',
        r'r"\'[^\']*\'"',
    ]


def test_lr1_io_identity_0():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> A
        A -> A B | ''
        B -> "a" B | "b"
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    for item_set in lr_automata.item_set_to_id.keys():
        assert (
            LRItemSetParser.from_string(cfg, LRItemSetPrinter.to_string(cfg, item_set))
            == item_set
        )


def test_lr1_io_identity_1():
    cfg = ContextFreeGrammar.from_string(
        r"""
        START -> Statement
        Statement -> Assignment | E
        E -> E "+" T | E "-" T | "-" T | T
        T -> T "*" F | T "/" F | T "%" F | F
        F -> F "**" G | G
        G -> "(" E ")" | int_const | id
        Assignment -> id "=" E
        int_const -> r"0|-?[1-9][0-9]*"
        id -> r"([a-zA-Z]|\_)([a-zA-Z]|[0-9]|\_)*"
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    for item_set in lr_automata.item_set_to_id.keys():
        assert (
            LRItemSetParser.from_string(cfg, LRItemSetPrinter.to_string(cfg, item_set))
            == item_set
        )


def test_lr1_io_identity_2():
    cfg = ContextFreeGrammar.from_string(
        r"""
        START -> lr_item_set
        lr_item_set -> lr_item lr_item_set | lr_item
        lr_item -> non_terminal "->" sequence "," look_forward
        sequence -> sequence token | token
        token -> non_terminal | terminal | "."
        non_terminal -> r"([a-zA-Z]|\_)([a-zA-Z]|[0-9]|\_)*"
        terminal -> r"\"[^\"]*\"" | r"\'[^\']*\'"
        terminal_or_EOF -> terminal | "$"
        look_forward -> terminal_or_EOF "/" look_forward | terminal_or_EOF
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    for item_set in lr_automata.item_set_to_id.keys():
        assert (
            LRItemSetParser.from_string(cfg, LRItemSetPrinter.to_string(cfg, item_set))
            == item_set
        )


def test_lr1_table_0():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> S
        S -> A
        A -> A B | ''
        B -> "a" B | "b"
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    expected_item_sets = [
        LRItemSetParser.from_string(
            cfg,
            """
            START ->  ◦ S, $
            S ->  ◦ A, $
            A ->  ◦ '', $/"a"/"b"
            A ->  ◦ A B, $/"a"/"b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            START -> S ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            A -> A ◦ B, $/"a"/"b"
            B ->  ◦ "a" B, $/"a"/"b"
            B ->  ◦ "b", $/"a"/"b"
            S -> A ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "b" ◦ , $/"a"/"b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            A -> A B ◦ , $/"a"/"b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "a" ◦ B, $/"a"/"b"
            B ->  ◦ "a" B, $/"a"/"b"
            B ->  ◦ "b", $/"a"/"b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "a" B ◦ , $/"a"/"b"
            """,
        ),
    ]
    assert set(lr_automata.item_set_to_id.keys()) == set(expected_item_sets)
    expected_edges: List[Tuple[int, str, int]] = [
        (0, "S", 1),
        (0, "A", 2),
        (2, '"b"', 3),
        (2, "B", 4),
        (2, '"a"', 5),
        (5, '"a"', 5),
        (5, '"b"', 3),
        (5, "B", 6),
    ]
    for src, edge, dst in expected_edges:
        i = lr_automata.item_set_to_id[expected_item_sets[src]]
        j = lr_automata.item_set_to_id[expected_item_sets[dst]]
        assert (SymbolParser.from_string(cfg, edge), j) in lr_automata.edges[i]
    assert sum(len(v) for v in lr_automata.edges.values()) == len(expected_edges)


def test_lr1_table_1():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> S
        S -> B B
        B -> "b" B | "a"
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    expected_item_sets = [
        LRItemSetParser.from_string(
            cfg,
            """
            START ->  ◦ S, $
            S ->  ◦ B B, $
            B ->  ◦ "b" B, "a"/"b"
            B ->  ◦ "a", "a"/"b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            START -> S ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            S -> B ◦ B, $
            B ->  ◦ "b" B, $
            B ->  ◦ "a", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "b" ◦ B, "b"/"a"
            B ->  ◦ "b" B, "b"/"a"
            B ->  ◦ "a", "b"/"a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "a" ◦ , "b"/"a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            S -> B B ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "b" ◦ B, $
            B ->  ◦ "b" B, $
            B ->  ◦ "a", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "b" B ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "a" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            B -> "b" B ◦ , "b"/"a"
            """,
        ),
    ]
    assert set(lr_automata.item_set_to_id.keys()) == set(expected_item_sets)
    expected_edges: List[Tuple[int, str, int]] = [
        (0, "S", 1),
        (0, "B", 2),
        (0, '"b"', 3),
        (0, '"a"', 4),
        (2, "B", 5),
        (2, '"b"', 6),
        (2, '"a"', 8),
        (3, '"b"', 3),
        (3, '"a"', 4),
        (3, "B", 9),
        (6, '"b"', 6),
        (6, '"a"', 8),
        (6, "B", 7),
    ]
    for src, edge, dst in expected_edges:
        i = lr_automata.item_set_to_id[expected_item_sets[src]]
        j = lr_automata.item_set_to_id[expected_item_sets[dst]]
        assert (SymbolParser.from_string(cfg, edge), j) in lr_automata.edges[i]
    assert sum(len(v) for v in lr_automata.edges.values()) == len(expected_edges)


def test_lr1_table_2():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> Z
        Z -> A "a" | "b" A "c" | "d" "c" | "b" "d" "a"
        A -> "d"
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    expected_item_sets = [
        LRItemSetParser.from_string(
            cfg,
            """
            START ->  ◦ Z, $
            Z ->  ◦ A "a", $
            Z ->  ◦ "b" A "c", $
            Z ->  ◦ "d" "c", $
            Z ->  ◦ "b" "d" "a", $
            A ->  ◦ "d", "a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            START -> Z ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "d" ◦ "c", $
            A -> "d" ◦ , "a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "d" "c" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> A ◦ "a", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> A "a" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "b" ◦ A "c", $
            A ->  ◦ "d", "c"
            Z -> "b" ◦ "d" "a", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            A -> "d" ◦ , "c"
            Z -> "b" "d" ◦ "a", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "b" "d" "a" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "b" A ◦ "c", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            Z -> "b" A "c" ◦ , $
            """,
        ),
    ]
    assert set(lr_automata.item_set_to_id.keys()) == set(expected_item_sets)
    expected_edges: List[Tuple[int, str, int]] = [
        (0, "Z", 1),
        (0, '"d"', 2),
        (0, "A", 4),
        (0, '"b"', 6),
        (2, '"c"', 3),
        (4, '"a"', 5),
        (6, '"d"', 7),
        (6, "A", 9),
        (7, '"a"', 8),
        (9, '"c"', 10),
    ]
    for src, edge, dst in expected_edges:
        i = lr_automata.item_set_to_id[expected_item_sets[src]]
        j = lr_automata.item_set_to_id[expected_item_sets[dst]]
        assert (SymbolParser.from_string(cfg, edge), j) in lr_automata.edges[i]
    assert sum(len(v) for v in lr_automata.edges.values()) == len(expected_edges)


def test_lr1_table_3():
    cfg = ContextFreeGrammar.from_string(
        """
        START -> L
        L -> M L "b" | "a"
        M -> ''
        """
    )
    lr_automata = LRItemSetAutomata.new(cfg)
    expected_item_sets = [
        LRItemSetParser.from_string(
            cfg,
            """
            START ->  ◦ L, $
            L ->  ◦ M L "b", $
            L ->  ◦ "a", $
            M ->  ◦ '', "a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            START -> L ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> "a" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M ◦ L "b", $
            L ->  ◦ M L "b", "b"
            L ->  ◦ "a", "b"
            M ->  ◦ '', "a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M ◦ L "b", "b"
            L ->  ◦ M L "b", "b"
            L ->  ◦ "a", "b"
            M ->  ◦ '', "a"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> "a" ◦ , "b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M L ◦ "b", $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M L "b" ◦ , $
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M L ◦ "b", "b"
            """,
        ),
        LRItemSetParser.from_string(
            cfg,
            """
            L -> M L "b" ◦ , "b"
            """,
        ),
    ]
    assert set(lr_automata.item_set_to_id.keys()) == set(expected_item_sets)
    expected_edges: List[Tuple[int, str, int]] = [
        (0, "L", 1),
        (0, '"a"', 2),
        (0, "M", 3),
        (3, "M", 4),
        (3, '"a"', 5),
        (3, "L", 6),
        (6, '"b"', 7),
        (4, '"a"', 5),
        (4, "M", 4),
        (4, "L", 8),
        (8, '"b"', 9),
    ]
    for src, edge, dst in expected_edges:
        i = lr_automata.item_set_to_id[expected_item_sets[src]]
        j = lr_automata.item_set_to_id[expected_item_sets[dst]]
        assert (SymbolParser.from_string(cfg, edge), j) in lr_automata.edges[i]
    assert sum(len(v) for v in lr_automata.edges.values()) == len(expected_edges)
