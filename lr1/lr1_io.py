from collections import deque
from typing import Iterable, Union

from cfg_utils.type_def import TypeDefinition
from cfg_utils.cfg import ContextFreeGrammar
from .lr1_item import LRItem
from .lr1_itemset import LRItemSet


class SymbolPrinter:
    @staticmethod
    def to_string(typedef: TypeDefinition, sym: str | int) -> str:
        match sym:
            case str():
                return sym if sym != ContextFreeGrammar.EMPTY else "''"
            case int():
                return typedef.get_pattern(sym) if sym != -1 else "$"


class LRItemPrinter:
    @staticmethod
    def to_string(cfg: ContextFreeGrammar, item: LRItem) -> str:
        non, seq = cfg.get_production(item.production_id)
        seqStr = (
            " ".join(
                SymbolPrinter.to_string(cfg.typedef, _) for _ in seq[: item.dot_pos]
            )
            + " ◦ "
            + " ".join(
                SymbolPrinter.to_string(cfg.typedef, _) for _ in seq[item.dot_pos :]
            )
        )
        lfStr = "%s" % "/".join(
            sorted(SymbolPrinter.to_string(cfg.typedef, _) for _ in item.look_forward)
        )
        return "%s -> %s, %s" % (non, seqStr, lfStr)


class LRItemSetPrinter:
    @staticmethod
    def to_string(cfg: ContextFreeGrammar, item_set: LRItemSet) -> str:
        return "\n".join(
            sorted(LRItemPrinter.to_string(cfg, item) for item in item_set.items)
        )


class LRPrinter:
    def __init__(self, cfg: ContextFreeGrammar) -> None:
        self.cfg = cfg

    def to_string(self, val: Union[str, int] | LRItem | LRItemSet) -> str:
        match val:
            case str() | int():
                return SymbolPrinter.to_string(self.cfg.typedef, val)
            case LRItem():
                return LRItemPrinter.to_string(self.cfg, val)
            case LRItemSet():
                return LRItemSetPrinter.to_string(self.cfg, val)


class SymbolParser:
    @staticmethod
    def from_string(cfg: ContextFreeGrammar, s: str) -> str | int:
        if s in cfg.non_terminals:
            return s
        else:
            if s == "''":
                return ContextFreeGrammar.EMPTY
            if s == "$":
                return -1
            return cfg.typedef.get_pattern_id(cfg.parse_terminal(s)[0])


# impl From<&str> for LRItem
class LRItemParser:
    @staticmethod
    def look_forward_tokenizer(look_forward: str) -> Iterable[str]:
        # since there might be "/", we can't use simple split("/")...
        que = deque(look_forward)
        while que:
            c = que.popleft()
            match c:
                case "r" | '"':
                    res_buffer = [c]
                    if c == "r":
                        res_buffer.append(que.popleft())
                    while que:
                        c = que.popleft()
                        res_buffer.append(c)
                        if c == '"':
                            break
                        if c == "\\":
                            res_buffer.append(que.popleft())
                    yield "".join(res_buffer)
                case "$":
                    yield c
                case " " | "\t" | "\n" | "/" | _:
                    continue

    @classmethod
    def from_string(cls, cfg: ContextFreeGrammar, s: str) -> LRItem:
        non, rest = s.strip().split(" -> ")
        dot_seq, look_forward = rest.split(", ")
        seq_l, seq_r = dot_seq.split(" ◦ ")
        dot_pos = 0 if seq_l.split(" ") == [""] else len(seq_l.split(" "))
        seq = tuple(
            SymbolParser.from_string(cfg, sym)
            for sym in " ".join((seq_l, seq_r)).strip().split(" ")
        )
        return LRItem(
            cfg.grammar_to_id[(non, seq)],
            set(
                SymbolParser.from_string(cfg, sym)
                for sym in cls.look_forward_tokenizer(look_forward)
            ),
            dot_pos,
        )


# impl From<&str> for LRItemSet
class LRItemSetParser:
    @staticmethod
    def from_string(cfg: ContextFreeGrammar, s: str) -> LRItemSet:
        item_set = LRItemSet()
        for line in map(lambda s: s.strip(), s.split("\n")):
            if line:
                item_set.add_lr_item(LRItemParser.from_string(cfg, line))
        return item_set
