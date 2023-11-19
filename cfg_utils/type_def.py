from typing import List, Tuple, Dict

from dfa_utils.finite_automata import FiniteAutomata
from dfa_utils.finite_automata_set import FiniteAutomataSet


class TypeDefinition:
    """
    A helper class that stores patterns / regexes and their corresponding id
    """

    def __init__(self):
        self.patterns: List[Tuple[str, bool]] = [] # (is_regex, pattern)
        self.pattern_to_id: Dict[str, int] = {}  # map name to integer id

    def __str__(self):
        return str(self.patterns) + "\n" + str(self.pattern_to_id)

    def add_definition(self, pattern: str, is_regex: bool = False):
        # in order to take less memory and have faster process speed,
        # map string to int.
        if pattern not in self.pattern_to_id:
            self.pattern_to_id[pattern] = len(self.pattern_to_id)
            self.patterns.append((pattern, is_regex))

    def get_dfa_set(self) -> FiniteAutomataSet:
        return FiniteAutomataSet(
            list(
                map(
                    lambda r: FiniteAutomata.from_string(r[0], minimize=True) if r[1] else FiniteAutomata.from_literal(r[0]),
                    self.patterns,
                )
            )
        )

    def get_pattern_id(self, pattern: str) -> int:
        return self.pattern_to_id[pattern]

    def get_pattern(self, id_: int) -> str:
        pattern, is_regex = self.patterns[id_]
        return ['"%s"', 'r"%s"'][is_regex] % pattern
