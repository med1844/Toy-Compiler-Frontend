from cfg_utils.cfg import ContextFreeGrammar
from typing import Set, Optional, Self


class LRItem:
    """
    Is in fact a tri-tuple (production id, look forward, dot position)
    lookForward is a set, containing a set of id of terminals.
    """

    def __init__(self, production_id: int, look_forward: Set[int], dot_pos: int = 0):
        self.production_id = production_id
        self.dot_pos = dot_pos
        self.look_forward = look_forward  # WARNING: REFERENCE IS SHARED FOR
        # PERFORMANCE. AVOID EDITING THIS.
        self.__hash_val: Optional[int] = None

    def __eq__(self, other: Self):
        return (
            self.production_id == other.production_id
            and self.dot_pos == other.dot_pos
            and self.look_forward == other.look_forward
        )

    def __hash__(self) -> int:
        if self.__hash_val is None:
            self.__hash_val = hash(
                (
                    self.production_id,
                    self.dot_pos,
                    hash(tuple(sorted(list(self.look_forward), key=str))),
                )
            )
        return self.__hash_val

    def __str__(self):
        return "(%s, %r, %s)" % (self.production_id, self.look_forward, self.dot_pos)

    def __repr__(self):
        return repr(str(self))

    def __lt__(self, other: Self):
        """
        LRItemSet would need static order of LRItem to calculate hash.
        """
        if self.production_id == other.production_id:
            if self.dot_pos == other.dot_pos:
                return hash(self) < hash(other)
            return self.dot_pos < other.dot_pos
        return self.production_id < other.production_id

    def get(self, cfg: ContextFreeGrammar, offset=0) -> Optional[str | int]:
        return cfg.get_symbol_in_prod(self.production_id, self.dot_pos, offset)

    def move_dot_forward(self):
        return LRItem(self.production_id, self.look_forward, self.dot_pos + 1)

    def at_end(self, cfg: ContextFreeGrammar) -> bool:
        prod = cfg.get_production(self.production_id)[1]
        return len(prod) == self.dot_pos or prod == ("",)
