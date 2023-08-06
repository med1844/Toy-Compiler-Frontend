from typing import List


class FiniteAutomataNode(object):

    __id_counter = -1

    @classmethod
    def __get_id(cls):
        cls.__id_counter += 1
        return cls.__id_counter

    def __init__(self, is_final_state: bool = False) -> None:
        self.is_final_state = is_final_state
        self.successors: List["FiniteAutomataNode"] = []
        self.id = self.__get_id()

    def __repr__(self) -> str:
        return "(%d%s -> %r)" % (self.id, "(END)" if self.is_final_state else "", tuple(c.id for c in self.successors))
