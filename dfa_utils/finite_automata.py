from bisect import bisect_right
from typing import Callable, Deque, Dict, Set, Tuple, List, Self, Iterable, Any
from copy import copy, deepcopy
from .regex_operation import RegexOperation
from .finite_automata_node import (
    CharTransition,
    FiniteAutomataNode,
    Transition,
    EpsilonTransition,
)
from collections import deque
from io_utils.to_json import ToJson


class FANodeClosure:
    # a simple helper class that implements __hash__ so that if the closure has been visited or not could be easily tracked
    def __init__(self, s: Set[FiniteAutomataNode] = set()) -> None:
        self.closure: Set[FiniteAutomataNode] = s

    def __hash__(self) -> int:
        # could also use bitmasks, but too expensive?
        return hash(tuple(sorted((node for node in self.closure), key=id)))

    def __eq__(self, other: Self) -> bool:
        return self.closure == other.closure  # that's the same set of nodes, simply compare the set equivalence


class FiniteAutomata(ToJson):

    def __init__(self, start_node: FiniteAutomataNode, accept_states: Set[FiniteAutomataNode] = set()) -> None:
        self.start_node = start_node
        self.accept_states = accept_states

    def __repr__(self) -> str:
        # iterate through all FA Nodes, in dfs fashion?
        node_id: Dict[FiniteAutomataNode, int] = {}
        counter = 0
        format_node: Callable[[FiniteAutomataNode], str] = lambda node: "\n".join(
            "%s %r %s"
            % (
                ("(%d)" if node in self.accept_states else "%d") % node_id[node],
                cond,
                ("(%d)" if nxt in self.accept_states else "%d") % node_id[nxt],
            )
            for cond, nxt in node.successors
        )

        def update_counter(
            cur_node: FiniteAutomataNode,
        ):
            nonlocal counter
            node_id[cur_node] = counter
            counter += 1

        self.start_node.dfs(update_counter, set())

        buffer = []
        self.start_node.dfs(lambda node: buffer.append(format_node(node)), set())
        return "\n".join(buffer)

    def unify_accept(self):
        if len(self.accept_states) > 1:
            new_accept_state = FiniteAutomataNode()
            for state in self.accept_states:
                state.add_edge(EpsilonTransition(), new_accept_state)
            self.accept_states.clear()
            self.accept_states.add(new_accept_state)

    @property
    def end_node(self) -> FiniteAutomataNode:
        return next(iter(self.accept_states))

    @staticmethod
    def split_by(rn: range, splits: List[int]) -> List[range]:
        result_ranges: List[range] = []
        l, r = rn.start, rn.stop
        while True:
            i = bisect_right(splits, l)
            if i < len(splits) and r > splits[i]:
                result_ranges.append(range(l, splits[i]))
                l = splits[i]
            else:
                if l < r:
                    result_ranges.append(range(l, r))
                break
        return result_ranges

    def determinize(self) -> Self:
        def epsilon_closure(n: Iterable[FiniteAutomataNode]) -> FANodeClosure:
            # the ϵ closure for a set of nodes
            visited: Set[FiniteAutomataNode] = set()
            que: Deque[FiniteAutomataNode] = deque(n)
            while que:
                cur = que.popleft()
                if cur in visited:
                    continue
                visited.add(cur)
                for cond, nxt in cur.successors:
                    if nxt not in visited and not cond.ranges:
                        que.append(nxt)
            return FANodeClosure(visited)

        start_closure = epsilon_closure([self.start_node])
        que: Deque[FANodeClosure] = deque([start_closure])
        visited: Set[FANodeClosure] = set()

        closure_to_node: Dict[FANodeClosure, FiniteAutomataNode] = {
            start_closure: FiniteAutomataNode()
        }
        # now we have to consider how to merge accept actions
        contains_accept_state = lambda fa_closure: any(node in self.accept_states for node in fa_closure.closure)
        accept_states = set()
        if contains_accept_state(start_closure):
            accept_states.add(start_closure)

        while que:
            cur = que.popleft()
            if cur in visited:
                continue
            visited.add(cur)

            # use scan line algo to generate the correct range to the set of reachable nodes mapping
            # please take a look at test_finite_automata.py:test_determinize_split_by_0 for more information
            all_ranges: List[Tuple[range, FiniteAutomataNode]] = [(r, nxt_node) for cur_node in cur.closure for t, nxt_node in cur_node.successors for r in t.ranges]
            all_ranges.sort(key=lambda k: (k[0].start, k[0].stop))
            range_to_nodes: Dict[range, List[FiniteAutomataNode]] = {}
            splits = sorted(set(map(lambda k: k[0].start, all_ranges)) | set(map(lambda k: k[0].stop, all_ranges)))
            for r, n in all_ranges:
                for sub_r in self.split_by(r, splits):
                    range_to_nodes.setdefault(sub_r, list()).append(n)

            # aggregate transitions that points to the same finite automata node sets
            nodes_to_ranges: Dict[Tuple[FiniteAutomataNode, ...], List[range]] = {}
            for range_, nxts in range_to_nodes.items():
                nodes_to_ranges.setdefault(tuple(sorted(nxts, key=id)), list()).append(range_)

            for nxts, ranges in nodes_to_ranges.items():
                cond = Transition(*ranges)
                nxt_closure = epsilon_closure(nxts)
                if nxt_closure not in closure_to_node:
                    closure_to_node[nxt_closure] = FiniteAutomataNode()
                    que.append(nxt_closure)
                    if contains_accept_state(nxt_closure):
                        accept_states.add(nxt_closure)
                closure_to_node[cur].add_edge(cond, closure_to_node[nxt_closure])
        return type(self)(closure_to_node[start_closure], {closure_to_node[c] for c in accept_states})

    def reverse_edge(self) -> Self:
        # create a new FiniteAutomata with all edges reversed.
        accept_states = copy(self.accept_states)
        edges: Dict[
            FiniteAutomataNode, List[Tuple[Transition, FiniteAutomataNode]]
        ] = {}
        visit_order: Dict[
            FiniteAutomataNode, int
        ] = {}  # would help determine back edges & sink nodes
        counter = 0
        first_pass_que = deque([self.start_node])
        while first_pass_que:
            cur_node = first_pass_que.popleft()
            if cur_node in edges:
                continue
            edges[cur_node] = cur_node.successors
            visit_order[cur_node] = counter
            counter += 1
            for _, nxt_node in cur_node.successors:
                if nxt_node not in edges:
                    first_pass_que.append(nxt_node)

        # from old nodes to new nodes in the new edge reversed NFA
        node_map: Dict[FiniteAutomataNode, FiniteAutomataNode] = {old_node: FiniteAutomataNode() for old_node in edges.keys()}
        for src_node, successors in edges.items():
            for cond, nxt_node in successors:
                node_map[nxt_node].add_edge(cond, node_map[src_node])

        # start_nodes would be all accept states
        if len(accept_states) > 1:
            rev_start_node = FiniteAutomataNode()
            for r in accept_states:
                rev_start_node.add_edge(EpsilonTransition(), node_map[r])
        else:
            rev_start_node = node_map[accept_states.pop()]

        return type(self)(rev_start_node, {node_map[self.start_node]})

    def minimize(self) -> Self:
        return self.reverse_edge().determinize().reverse_edge().determinize()

    def __deepcopy__(self, memo=None) -> Self:
        def dfs(cur_node: FiniteAutomataNode, node_mapping: Dict[FiniteAutomataNode, FiniteAutomataNode], visited: Set[FiniteAutomataNode]):
            if cur_node in visited:
                return
            visited.add(cur_node)
            for cond, nxt_node in cur_node.successors:
                if nxt_node not in node_mapping:
                    node_mapping[nxt_node] = FiniteAutomataNode()
                node_mapping[cur_node].add_edge(cond, node_mapping[nxt_node])
                if nxt_node not in visited:
                    dfs(nxt_node, node_mapping, visited)

        mappings = {self.start_node: FiniteAutomataNode()}
        dfs(self.start_node, mappings, set())
        return type(self)(mappings[self.start_node], {mappings[node] for node in self.accept_states})

    @classmethod
    def from_string(cls, regex: str, determinize=False, minimize=False) -> Self:
        # WARNING:
        # by default, this function would return an NFA.
        # currently, match_first method only accepts DFA.
        # so please make sure you passed minimize=True when initialize FA objects, if you want to match something
        # NOTE:
        # minimize would include determinize (Min-DFA must be DFA),
        # so determinize=False, minimize=True would still produce a DFA
        nfa = parse(deque(regex), NFANodeRegexOperation())
        if minimize:
            nfa = nfa.minimize()
        if not minimize and determinize:
            nfa = nfa.determinize()
        return nfa

    def __eq__(self, other: Self) -> bool:
        # TODO: implement a graph isomorphism algorithm to compare structure identity, e.g. Weisfeiler-Lehman Kernel
        raise NotImplementedError()

    def __hash__(self) -> int:
        # requirements:
        # - back edges must contribute to the result
        # - the order we visit the out coming edges doesn't change results i.e. the hash must use operator with communitativity
        # get edges first, then bfs in reversed order
        #
        # NOTE: it turns out to be the problem of graph isomorphism...?
        # https://www.jmlr.org/papers/volume12/shervashidze11a/shervashidze11a.pdf
        # Or if there's a way to calc SCC's hash mathematically, then we could convert it into DAG hashing?
        # SCC's hash might be done by gaussian elimination or something, requires further investigation
        edges: Dict[
            FiniteAutomataNode, List[Tuple[Transition, FiniteAutomataNode]]
        ] = {}
        visit_order: Dict[
            FiniteAutomataNode, int
        ] = {}  # would help determine back edges & sink nodes
        counter = 0
        first_pass_que = deque([self.start_node])
        while first_pass_que:
            cur_node = first_pass_que.popleft()
            if cur_node in edges:
                continue
            edges[cur_node] = cur_node.successors
            visit_order[cur_node] = counter
            counter += 1
            for _, nxt_node in cur_node.successors:
                if nxt_node not in edges:
                    first_pass_que.append(nxt_node)

        rev_edges: Dict[
            FiniteAutomataNode, List[Tuple[Transition, FiniteAutomataNode]]
        ] = {node: list() for node in edges.keys()}
        for cur_node, v in edges.items():
            for nxt_cond, nxt_node in v:
                rev_edges[nxt_node].append((nxt_cond, cur_node))

        second_pass_que: Deque[FiniteAutomataNode] = deque()
        for node, edge in edges.items():
            if node in self.accept_states and all(visit_order[nxt_node] <= visit_order[node] for _, nxt_node in edge):
                second_pass_que.append(
                    node
                )  # current node is a sink node: no out edge, or all out edges are back edges

        node_hash: Dict[FiniteAutomataNode, int] = {
            node: len(node.successors) + (10000 * (node in self.accept_states))
            for node in edges.keys()
        }
        visited: Set[FiniteAutomataNode] = set()
        while second_pass_que:
            cur_node = second_pass_que.popleft()
            if cur_node in visited:
                continue
            visited.add(cur_node)
            x = node_hash[cur_node]
            x = ((x >> 16) ^ x) * 0x45D9F3B
            x = ((x >> 16) ^ x) * 0x45D9F3B
            node_hash[cur_node] = x
            for prv_cond, prv_node in rev_edges[cur_node]:
                if prv_node not in visited:
                    node_hash[prv_node] ^= (
                        hash(prv_cond) * node_hash[cur_node]
                    ) & 0xFFFFFFFFFFFFFFFF
                    second_pass_que.append(prv_node)

        return node_hash[self.start_node]

    def match_first(self, s: Iterable[str]) -> str:
        # TODO this is SO UGLY, think about more elegant implementation
        cur_node = self.start_node
        buffer = []
        accepted_buffer = []
        for c in s:
            any_hit = False
            if cur_node in self.accept_states:
                accepted_buffer.extend(buffer)
                buffer.clear()
            for cond, nxt_node in cur_node.successors:
                if cond(c):
                    buffer.append(c)
                    cur_node = nxt_node
                    any_hit = True
                    break
            if not any_hit:
                break
        if cur_node in self.accept_states:
            accepted_buffer.extend(buffer)
            buffer.clear()
        if accepted_buffer:
            return "".join(accepted_buffer)
        return ""

    def to_json(self):
        # returns the amount of nodes, and edges.
        node_id: Dict[FiniteAutomataNode, int] = {}
        counter = 0

        def update_counter(
            cur_node: FiniteAutomataNode,
        ):
            nonlocal counter
            node_id[cur_node] = counter
            counter += 1

        self.start_node.dfs(update_counter, set())

        # {src: [(condition, dst), ...]}
        edges: Dict[int, List[Tuple[Any, int]]] = {}

        def update_edges(
            cur_node: FiniteAutomataNode,
        ):
            nonlocal node_id, edges
            for (cond, nxt_node) in cur_node.successors:
                edges.setdefault(node_id[cur_node], list()).append((cond.to_json(), node_id[nxt_node]))

        self.start_node.dfs(update_edges, set())

        return {
            "num_node": len(node_id),
            "start_node": node_id[self.start_node],
            "accept_states": sorted(map(lambda node: node_id[node], self.accept_states)),
            "edges": edges
        }


class NFANodeRegexOperation(RegexOperation):
    # impl RegexOperation<NFA>
    @staticmethod
    def make_nfa(c: str) -> FiniteAutomata:
        assert len(c) == 1
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        s.add_edge(CharTransition(c) if c != "ϵ" else EpsilonTransition(), e)
        return FiniteAutomata(s, {e})

    @classmethod
    def make_range_nfa(cls, *ranges: range, complementary=False) -> FiniteAutomata:
        if complementary:
            compl_ranges: List[range] = []
            start = cls.START
            for r in ranges:
                compl_ranges.append(range(start, r.start))
                start = r.stop
            compl_ranges.append(range(start, 0x7f))
            ranges = tuple(compl_ranges)
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        s.add_edge(Transition(*ranges), e)
        return FiniteAutomata(s, {e})

    @classmethod
    def make_dot_nfa(cls) -> FiniteAutomata:
        # only match printable ascii characters, i.e. no unicode support
        return cls.make_inverse_nfa("\n")  # 0x7f is not printable thus doesn't include it

    @classmethod
    def make_inverse_nfa(cls, s: str) -> FiniteAutomata:
        return cls.make_range_nfa(range(cls.START, ord(s)), range(ord(s) + 1, 0x7f))

    @classmethod
    def kleene_star(cls, r: FiniteAutomata) -> FiniteAutomata:
        # s ->               ϵ                 -> e
        #   \                                /
        #   r.start_node -> ... -> r.end_node
        #               \         /
        #                 <- ϵ <-
        r.end_node.add_edge(EpsilonTransition(), r.start_node)
        return cls.optional(r)

    @staticmethod
    def or_(*ops: FiniteAutomata) -> FiniteAutomata:
        #     -> l ->
        #   /    .    \
        # s   -> . ->   e
        #   \    .    /
        #     -> r ->
        if len(ops) == 1:
            return ops[0]
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        for op in ops:
            s.add_edge(EpsilonTransition(), op.start_node)
            op.end_node.add_edge(EpsilonTransition(), e)
        return FiniteAutomata(s, {e})

    @staticmethod
    def concat(l: FiniteAutomata, r: FiniteAutomata) -> FiniteAutomata:
        l.end_node.add_edge(EpsilonTransition(), r.start_node)
        return FiniteAutomata(l.start_node, {r.end_node})

    @classmethod
    def plus(cls, r: FiniteAutomata) -> FiniteAutomata:
        s = deepcopy(r)
        t = cls.kleene_star(r)
        s.end_node.add_edge(EpsilonTransition(), t.start_node)
        return FiniteAutomata(s.start_node, {t.end_node})

    @staticmethod
    def optional(r: FiniteAutomata) -> FiniteAutomata:
        # s -> ϵ -> e
        #  \       /
        #   -> r ->
        s = FiniteAutomataNode()
        e = FiniteAutomataNode()
        s.add_edge(EpsilonTransition(), e)
        s.add_edge(EpsilonTransition(), r.start_node)
        r.end_node.add_edge(EpsilonTransition(), e)
        return FiniteAutomata(s, {e})


def parse(r: Deque[str], regex_operation: RegexOperation):
    # op priority: {*, +} > concat > or
    ops = deque()  # operands, but doesn't consider "|" operators. We must first concatenate everything before "|" them
    or_ops = deque()

    def reduce_concat():
        l = ops.popleft()
        while ops:
            c = ops.popleft()
            l = regex_operation.concat(l, c)
        return l

    while r:
        s = r.popleft()
        if s == "(":
            ops.append(parse(r, regex_operation))
        elif s == ")":
            break
        elif s == "*":
            ops.append(regex_operation.kleene_star(ops.pop()))
        elif s == "?":
            ops.append(regex_operation.optional(ops.pop()))
        elif s == "+":
            ops.append(regex_operation.plus(ops.pop()))
        elif s == "|":
            or_ops.append(reduce_concat())
        elif s == "[":
            complementary = False
            if r[0] == "^":
                complementary = True
                r.popleft()
            ranges = []
            while True:
                if len(r) >= 2 and r[0] != "\\" and r[0] != "]" and r[1] == "-":
                    s = r.popleft()
                    _ = r.popleft()
                    e = r.popleft()
                    ranges.append(range(ord(s), ord(e) + 1))
                else:
                    if r[0] == "\\":
                        r.popleft()
                    s = r.popleft()
                    ranges.append(range(ord(s), ord(s) + 1))
                if r[0] == "]":
                    r.popleft()
                    break
            ops.append(regex_operation.make_range_nfa(*ranges, complementary=complementary))
        elif s == ".":
            ops.append(regex_operation.make_dot_nfa())
        elif len(s) == 1:
            if s == "\\":
                s = r.popleft()
            ops.append(regex_operation.make_nfa(s))
    if ops:
        or_ops.append(reduce_concat())
    l = regex_operation.or_(*or_ops)
    return l

