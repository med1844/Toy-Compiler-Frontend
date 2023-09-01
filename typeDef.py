from typing import Optional, Dict, List, Tuple, Self


class TypeDefinition:

    r"""
    To create type definition, use TypeDefinition.load(fileName).

    For each line, the type definition should contain three elements, 
    divided by space:
        1. name that will be used in program
        2. regular expression
        3. (optional) display name
    
    For example:
        minus \-{1} -
        int_constant \b(-?)(0|[1-9]\d*)\b int_const
        int \bint\b int
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
        for line in string.split('\n'):
            a, b, *rest = line.strip().split(' ')
            assert len(rest) <= 1
            td.add_definition(a, b, *rest)
        return td

    def __init__(self):
        self.regex: List[Tuple[str, str, Optional[str]]] = []
        self.__name_to_id = {}  # map name to integer id
        self.__display_name_to_id = {}  # map display name to integer
        self.re = None

    def __str__(self):
        return str(self.regex) + "\n" + str(self.__name_to_id)
    
    def add_definition(self, name: str, expression: str, displayName: Optional[str]=None):
        self.regex.append((name, expression, displayName))

        # in order to take less memory and have faster process speed, 
        # map string to int.
        if name not in self.__name_to_id:
            cur_id = len(self.__name_to_id)
            self.__name_to_id[name] = cur_id
            if displayName is not None:
                self.__display_name_to_id[displayName] = cur_id
    
    def get_re_compatible_regex(self):
        if self.re is None:
            self.re = '|'.join('(?P<%s>%s)' % (k, v)
                               for (k, v, _) in self.regex)
        return self.re

    def get_name_n_regex(self):
        return self.regex

    def get_id_by_name(self, name: str) -> int:
        assert name in self.__name_to_id
        return self.__name_to_id[name]
    
    def get_id_by_display_name(self, display_name: str) -> int:
        assert display_name in self.__display_name_to_id
        return self.__display_name_to_id[display_name]
    
    def get_name_by_id(self, id_: int) -> str:
        return self.regex[id_][0]
    
    def get_display_name_by_id(self, id_) -> str:
        res = self.regex[id_][-1]
        if res is None:
            res = ""
        return res
