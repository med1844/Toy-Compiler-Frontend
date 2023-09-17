from typing import Optional, Dict, List, Tuple, Self

from dfa_utils.finite_automata import FiniteAutomata


class TypeDefinition:
    r"""
    To create type definition, use TypeDefinition.load(fileName).

    For each line, the type definition should contain three elements,
    divided by space:
        1. display name
        2. regular expression

    For example:
        int_const (-?)(0|[1-9][0-9]*)
        int int
        < <
    """

    @staticmethod
    def from_filename(filename: str):
        """
        Load type definition from given file.
        """
        with open(filename, "r") as f:
            src = f.read().strip()
        return TypeDefinition.from_string(src)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """
        Load type definition from given string.
        """
        td = cls()
        for line in string.split("\n"):
            a, b = line.strip().split(" ")
            td.add_definition(a, b)
        return td

    def __init__(self):
        self.regex: List[Tuple[str, str]] = []
        self.__name_to_id = {}  # map name to integer id
        self.re = None

    def __str__(self):
        return str(self.regex) + "\n" + str(self.__name_to_id)

    def add_definition(self, display_name: str, expression: str):
        self.regex.append((display_name, expression))

        # in order to take less memory and have faster process speed,
        # map string to int.
        if display_name not in self.__name_to_id:
            cur_id = len(self.__name_to_id)
            self.__name_to_id[display_name] = cur_id

    def get_dfa_list(self) -> List[FiniteAutomata]:
        return list(
            map(
                lambda r: FiniteAutomata.from_string(r[1], minimize=True),
                self.regex,
            )
        )

    def get_name_n_regex(self):
        return self.regex

    def get_id_by_name(self, name: str) -> int:
        assert name in self.__name_to_id
        return self.__name_to_id[name]

    def get_name_by_id(self, id_: int) -> str:
        return self.regex[id_][0]
