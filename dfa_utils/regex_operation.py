from typing import TypeVar, List
from abc import ABC

T = TypeVar("T")


# consider this as a trait... why there's no trait in python
class RegexOperation(ABC):
    START = 0

    @staticmethod
    def make_nfa(s: str) -> T:
        raise NotImplementedError()

    @staticmethod
    def make_range_nfa(*ranges: range, complementary=False) -> T:
        raise NotImplementedError()

    @staticmethod
    def make_dot_nfa() -> T:
        # TODO I actually start feeling this super dirty... is there any good way to refactor this
        raise NotImplementedError()

    @staticmethod
    def make_inverse_nfa(s: str) -> T:
        # inverse only one char? or inverse range?
        raise NotImplementedError()

    @classmethod
    def kleene_star(cls, r: T) -> T:
        raise NotImplementedError()
        
    @staticmethod
    def or_(*ops: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def concat(l: T, r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def plus(r: T) -> T:
        raise NotImplementedError()

    @staticmethod
    def optional(r: T) -> T:
        raise NotImplementedError()


class StringRegexOperation(RegexOperation):
    # impl RegexOperation<String>
    @staticmethod
    def make_nfa(s: str) -> str:
        return s

    @classmethod
    def make_range_nfa(cls, *ranges: range, complementary=False) -> str:
        if complementary:
            compl_ranges: List[range] = []
            start = cls.START
            for r in ranges:
                compl_ranges.append(range(start, r.start))
                start = r.stop
            compl_ranges.append(range(start, 0x7f))
            ranges = tuple(compl_ranges)
        return cls.or_(*(cls.make_nfa(chr(i)) for r in ranges for i in r))

    @classmethod
    def make_dot_nfa(cls) -> str:
        # only match printable ascii characters, i.e. no unicode support
        return cls.make_inverse_nfa("\n")  # 0x7f is not printable thus doesn't include it

    @classmethod
    def make_inverse_nfa(cls, s: str) -> str:
        return cls.make_range_nfa(range(cls.START, ord(s)), range(ord(s) + 1, 0x7f))

    @classmethod
    def kleene_star(cls, r: str) -> str:
        return "(%s*)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

    @staticmethod
    def or_(*ops: str) -> str:
        return "(%s)" % "|".join(ops) if len(ops) > 1 else ops[0]

    @staticmethod
    def concat(l: str, r: str) -> str:
        return "%s->%s" % (l, r)

    @staticmethod
    def plus(r: str) -> str:
        return "(%s+)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

    @staticmethod
    def optional(r: str) -> str:
        return "(%s?)" % r if len(r) == 1 or (r.startswith("(") and r.endswith(")")) else "((%s)*)" % r

