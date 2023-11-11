from typing import Callable, List, Optional, Set, Tuple, Self
from bisect import bisect_right
from io_utils.to_json import ToJson
from io_utils.from_json import FromJson


# range-based transition
class Transition(ToJson, FromJson):
    def __init__(self, *ranges: range) -> None:
        self.ranges = self.__make_no_overlap(ranges)

    def __call__(self, c: str) -> bool:
        return (not self.ranges) or any(ord(c) in r for r in self.ranges)

    def __repr__(self) -> str:
        if not self.ranges:
            return "-ϵ>"
        elif len(self.ranges) == 1 and self.ranges[0].stop - self.ranges[0].start == 1:
            return "-%s>" % chr(self.ranges[0].start)
        else:
            return "-[%s]>" % "".join(
                "%s-%s" % (chr(r.start), chr(r.stop - 1)) for r in self.ranges
            )

    def __hash__(self) -> int:
        return hash(self.ranges)

    def __eq__(self, other: Self) -> bool:
        return self.ranges == other.ranges

    @staticmethod
    def __make_no_overlap(ranges: Tuple[range, ...]) -> Tuple[range, ...]:
        stack: List[range] = []
        for cur in sorted(ranges, key=lambda r: (r.start, r.stop)):
            if not stack:
                stack.append(cur)
            else:
                if stack[-1].stop >= cur.start:
                    stack.append(range(stack.pop().start, cur.stop))
                else:
                    stack.append(cur)
        return tuple(stack)

    @staticmethod
    def __le_range(a: range, b: range):
        return a.start >= b.start and a.stop <= b.stop and a.step == b.step

    def __le__(self, other: Self) -> bool:
        # this type of class satisfies PartialOrd trait... but is there any
        # good structure for high performance grid propagation?
        # to satisfy self <= other, for each range r in self.ranges,
        # it must satisfy that it's subsumed by exactly one range in other.ranges
        # maybe use bisect to do that?
        return all(
            self.__le_range(
                r,
                other.ranges[
                    bisect_right(other.ranges, r.start, key=lambda r: r.start) - 1
                ],
            )
            for r in self.ranges
        )

    def to_json(self):
        return [(r.start, r.stop) for r in self.ranges]

    @classmethod
    def from_json(cls, obj: List[Tuple[int, int]]):
        return cls(*map(lambda a: range(a[0], a[1]), obj))


# enum Transition {
#   EpsilonTransition,
#   CharTransition(char)
# }
#
# impl Fn<Args> for EpsilonTransition
class EpsilonTransition(Transition):
    def __init__(self) -> None:
        super().__init__()


# impl Fn<Args> for CharTransition
class CharTransition(Transition):
    def __init__(self, c: str) -> None:
        assert len(c) == 1
        super().__init__(range(ord(c), ord(c) + 1))


class FiniteAutomataNode(object):
    def __init__(self, fa_id: Optional[int] = None) -> None:
        self.successors: List[Tuple[Transition, "FiniteAutomataNode"]] = []
        self.fa_id = fa_id

    def add_edge(self, cond: Transition, other: "FiniteAutomataNode") -> None:
        self.successors.append((cond, other))

    def dfs(
        self,
        action: Callable[["FiniteAutomataNode"], None],
        visited: Set["FiniteAutomataNode"],
    ):
        visited.add(self)
        action(self)
        for _, nxt_node in self.successors:
            if nxt_node not in visited:
                nxt_node.dfs(action, visited)
