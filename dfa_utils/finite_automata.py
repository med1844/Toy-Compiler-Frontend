from typing import Callable, Deque, Dict, Set, Tuple, List, Self, Iterable
from copy import copy, deepcopy
from .regex_operation import RegexOperation
from .finite_automata_node import (
    CharTransition,
    FiniteAutomataNode,
    Transition,
    EpsilonTransition,
)
from collections import deque


class FANodeClosure:
    # a simple helper class that implements __hash__ so that if the closure has been visited or not could be easily tracked
    def __init__(self, s: Set[FiniteAutomataNode] = set()) -> None:
        self.closure: Set[FiniteAutomataNode] = s

    def __hash__(self) -> int:
        # could also use bitmasks, but too expensive?
        return hash(tuple(sorted((node for node in self.closure), key=id)))

    def __eq__(self, other: Self) -> bool:
        return self.closure == other.closure  # that's the same set of nodes, simply compare the set equivalence


class FiniteAutomata:

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

        def assign_id_dfs(
            cur_node: FiniteAutomataNode,
        ):
            nonlocal counter
            node_id[cur_node] = counter
            counter += 1
            for _, nxt_node in cur_node.successors:
                if nxt_node not in node_id:
                    assign_id_dfs(nxt_node)

        def dfs(
            cur_node: FiniteAutomataNode,
            action: Callable[[FiniteAutomataNode], None],
            visited: Set[FiniteAutomataNode],
        ):
            visited.add(cur_node)
            action(cur_node)
            for _, nxt_node in cur_node.successors:
                if nxt_node not in visited:
                    dfs(nxt_node, action, visited)


        buffer = []
        assign_id_dfs(self.start_node)
        dfs(self.start_node, lambda node: buffer.append(format_node(node)), set())
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
                    if nxt not in visited and isinstance(cond, EpsilonTransition):
                        que.append(nxt)
            return FANodeClosure(visited)

        start_closure = epsilon_closure([self.start_node])
        que: Deque[FANodeClosure] = deque([start_closure])
        visited: Set[FANodeClosure] = set()
        closure_to_node: Dict[FANodeClosure, FiniteAutomataNode] = {
            start_closure: FiniteAutomataNode()
        }
        contains_accept_state = lambda fa_closure: any(node in self.accept_states for node in fa_closure.closure)
        accept_states = set()
        if contains_accept_state(start_closure):
            accept_states.add(start_closure)

        while que:
            cur = que.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            cur_node = closure_to_node[cur]  # would be used to add edges

            # for all possible outcoming edges in all nodes...
            # since nfa could have same transition condition pointing to different nodes, we have to group first before proceed
            group_by_edge: Dict[Transition, List[FiniteAutomataNode]] = {}
            for cond, nxt in ((cond, nxt) for node in cur.closure for cond, nxt in node.successors if not isinstance(cond, EpsilonTransition)):
                group_by_edge.setdefault(cond, list()).append(nxt)

            for cond, nxts in group_by_edge.items():
                nxt_closure = epsilon_closure(nxts)
                if nxt_closure not in closure_to_node:
                    closure_to_node[nxt_closure] = FiniteAutomataNode()
                    que.append(nxt_closure)
                    if contains_accept_state(nxt_closure):
                        accept_states.add(nxt_closure)
                nxt_node = closure_to_node[nxt_closure]
                cur_node.add_edge(cond, nxt_node)
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
    def from_string(cls, regex: str, minimize=False) -> Self:
        nfa = parse(deque(regex), NFANodeRegexOperation())
        assert isinstance(nfa, FiniteAutomata)
        if minimize:
            rev_dfa = nfa.reverse_edge().determinize()
            min_dfa = rev_dfa.reverse_edge().determinize()
            return min_dfa
        else:
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
                        id(prv_cond) * node_hash[cur_node]
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
            start = 0x20
            for r in ranges:
                compl_ranges.append(range(start, r.start))
                start = r.stop
            compl_ranges.append(range(start, 0x7f))
            ranges = tuple(compl_ranges)
        return cls.or_(*(cls.make_nfa(chr(i)) for r in ranges for i in r))

    @classmethod
    def make_dot_nfa(cls) -> FiniteAutomata:
        # only match printable ascii characters, i.e. no unicode support
        return cls.make_inverse_nfa("\n")  # 0x7f is not printable thus doesn't include it

    @classmethod
    def make_inverse_nfa(cls, s: str) -> FiniteAutomata:
        return cls.make_range_nfa(range(0x20, ord(s)), range(ord(s) + 1, 0x7f))

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


def test_nfa_hash_0():
    # test if a back edge causes difference in the hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    e0.add_edge(EpsilonTransition(), s0)
    nfa_0 = FiniteAutomata(s0, {e0})

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = FiniteAutomata(s1, {e1})

    assert hash(nfa_0) != hash(nfa_1)


def test_nfa_hash_1():
    # make sure that the order we add edges doesn't effect hash result
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    s0.add_edge(CharTransition("a"), e0)
    s0.add_edge(CharTransition("b"), e0)
    nfa_0 = FiniteAutomata(s0, {e0})

    s1 = FiniteAutomataNode()
    e1 = FiniteAutomataNode()
    s1.add_edge(CharTransition("b"), e1)
    s1.add_edge(CharTransition("a"), e1)
    nfa_1 = FiniteAutomata(s1, {e1})

    assert hash(nfa_0) == hash(nfa_1)


def test_nfa_deepcopy_0():
    for regex in (
        "a*bcc|c*dee",
        "((a|b)*(cc|dd))*ee",
        "ac(bc|de)|ff",
        "a*",
        "a",
    ):
        a = FiniteAutomata.from_string(regex)
        b = deepcopy(a)
        assert hash(a) == hash(b)


def test_parsing_nfa_0():
    constructed_nfa = FiniteAutomata.from_string("a")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s.add_edge(CharTransition("a"), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_1():
    constructed_nfa = FiniteAutomata.from_string("a|b")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sb = FiniteAutomataNode()
    eb = FiniteAutomataNode()
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), sb)
    sa.add_edge(CharTransition("a"), ea)
    sb.add_edge(CharTransition("b"), eb)
    ea.add_edge(EpsilonTransition(), e)
    eb.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_2():
    constructed_nfa = FiniteAutomata.from_string("ab")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(CharTransition("b"), n3)
    expected_nfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_3():
    constructed_nfa = FiniteAutomata.from_string("a*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), sa)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_4():
    constructed_nfa = FiniteAutomata.from_string("a?")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    sa = FiniteAutomataNode()
    ea = FiniteAutomataNode()
    sa.add_edge(CharTransition("a"), ea)
    ea.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), sa)
    s.add_edge(EpsilonTransition(), e)
    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_5():
    constructed_nfa = FiniteAutomata.from_string("(c|d)*")
    s = FiniteAutomataNode()
    e = FiniteAutomataNode()
    s0 = FiniteAutomataNode()
    e0 = FiniteAutomataNode()
    sc = FiniteAutomataNode()
    ec = FiniteAutomataNode()
    sd = FiniteAutomataNode()
    ed = FiniteAutomataNode()

    sc.add_edge(CharTransition("c"), ec)
    sd.add_edge(CharTransition("d"), ed)

    s0.add_edge(EpsilonTransition(), sc)
    s0.add_edge(EpsilonTransition(), sd)

    ec.add_edge(EpsilonTransition(), e0)
    ed.add_edge(EpsilonTransition(), e0)

    e0.add_edge(EpsilonTransition(), s0)

    s.add_edge(EpsilonTransition(), e)
    s.add_edge(EpsilonTransition(), s0)

    e0.add_edge(EpsilonTransition(), e)

    expected_nfa = FiniteAutomata(s, {e})
    assert hash(constructed_nfa) == hash(expected_nfa)

def test_parsing_nfa_6():
    constructed_nfa = FiniteAutomata.from_string("(ab*(c|d)*)|(e|(f*g))")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)

    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(EpsilonTransition(), n2)

    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n4.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n2)
    n3.add_edge(EpsilonTransition(), n5)

    n1.add_edge(EpsilonTransition(), n4)

    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n6.add_edge(CharTransition("c"), n7)

    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()
    n8.add_edge(CharTransition("d"), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()

    n10.add_edge(EpsilonTransition(), n6)
    n10.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n11)
    n9.add_edge(EpsilonTransition(), n11)

    n11.add_edge(EpsilonTransition(), n10)

    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n12.add_edge(EpsilonTransition(), n10)
    n12.add_edge(EpsilonTransition(), n13)
    n11.add_edge(EpsilonTransition(), n13)

    n5.add_edge(EpsilonTransition(), n12)

    n14 = FiniteAutomataNode()

    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n15.add_edge(CharTransition("e"), n16)

    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n17.add_edge(CharTransition("f"), n18)
    n18.add_edge(EpsilonTransition(), n17)

    n19 = FiniteAutomataNode()
    n20 = FiniteAutomataNode()
    n19.add_edge(EpsilonTransition(), n20)
    n19.add_edge(EpsilonTransition(), n17)
    n18.add_edge(EpsilonTransition(), n20)

    n14.add_edge(EpsilonTransition(), n15)
    n14.add_edge(EpsilonTransition(), n19)

    n21 = FiniteAutomataNode()
    n22 = FiniteAutomataNode()
    n21.add_edge(CharTransition("g"), n22)
    n20.add_edge(EpsilonTransition(), n21)

    n23 = FiniteAutomataNode()
    n16.add_edge(EpsilonTransition(), n23)
    n22.add_edge(EpsilonTransition(), n23)

    n24 = FiniteAutomataNode()
    n25 = FiniteAutomataNode()

    n24.add_edge(EpsilonTransition(), n0)
    n24.add_edge(EpsilonTransition(), n14)
    n13.add_edge(EpsilonTransition(), n25)
    n23.add_edge(EpsilonTransition(), n25)

    expected_nfa = FiniteAutomata(n24, {n25})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_7():
    constructed_nfa = FiniteAutomata.from_string("a+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n4.add_edge(CharTransition("a"), n5)
    n5.add_edge(EpsilonTransition(), n3)
    n5.add_edge(EpsilonTransition(), n4)

    expected_nfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_8():
    constructed_nfa = FiniteAutomata.from_string("(0|1|2|3)+")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n9 = FiniteAutomataNode()

    n1.add_edge(CharTransition("0"), n2)
    n3.add_edge(CharTransition("1"), n4)
    n5.add_edge(CharTransition("2"), n6)
    n7.add_edge(CharTransition("3"), n8)

    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n3)
    n0.add_edge(EpsilonTransition(), n5)
    n0.add_edge(EpsilonTransition(), n7)
    n2.add_edge(EpsilonTransition(), n9)
    n4.add_edge(EpsilonTransition(), n9)
    n6.add_edge(EpsilonTransition(), n9)
    n8.add_edge(EpsilonTransition(), n9)

    n10 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n12 = FiniteAutomataNode()
    n13 = FiniteAutomataNode()
    n14 = FiniteAutomataNode()
    n15 = FiniteAutomataNode()
    n16 = FiniteAutomataNode()
    n17 = FiniteAutomataNode()
    n18 = FiniteAutomataNode()
    n19 = FiniteAutomataNode()

    n11.add_edge(CharTransition("0"), n12)
    n13.add_edge(CharTransition("1"), n14)
    n15.add_edge(CharTransition("2"), n16)
    n17.add_edge(CharTransition("3"), n18)

    n10.add_edge(EpsilonTransition(), n11)
    n10.add_edge(EpsilonTransition(), n13)
    n10.add_edge(EpsilonTransition(), n15)
    n10.add_edge(EpsilonTransition(), n17)
    n12.add_edge(EpsilonTransition(), n19)
    n14.add_edge(EpsilonTransition(), n19)
    n16.add_edge(EpsilonTransition(), n19)
    n18.add_edge(EpsilonTransition(), n19)

    n19.add_edge(EpsilonTransition(), n10)

    n20 = FiniteAutomataNode()
    n21 = FiniteAutomataNode()

    n20.add_edge(EpsilonTransition(), n21)
    n20.add_edge(EpsilonTransition(), n10)
    n19.add_edge(EpsilonTransition(), n21)

    n9.add_edge(EpsilonTransition(), n20)

    expected_nfa = FiniteAutomata(n0, {n21})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_10():
    # test if ϵ is correctly handled
    constructed_nfa = FiniteAutomata.from_string("ϵ|a")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n0.add_edge(EpsilonTransition(), n1)
    n1.add_edge(EpsilonTransition(), n2)

    n0.add_edge(EpsilonTransition(), n3)
    n3.add_edge(CharTransition("a"), n4)

    n2.add_edge(EpsilonTransition(), n5)
    n4.add_edge(EpsilonTransition(), n5)

    expected_nfa = FiniteAutomata(n0, {n5})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_11():
    constructed_nfa = FiniteAutomata.from_string("d(ϵ|ab)")
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n6 = FiniteAutomataNode()
    n7 = FiniteAutomataNode()
    n8 = FiniteAutomataNode()
    n11 = FiniteAutomataNode()
    n0.add_edge(CharTransition("d"), n1)
    n1.add_edge(EpsilonTransition(), n2)
    n2.add_edge(EpsilonTransition(), n3)
    n2.add_edge(EpsilonTransition(), n4)
    n3.add_edge(EpsilonTransition(), n5)
    n4.add_edge(CharTransition("a"), n6)
    n6.add_edge(EpsilonTransition(), n11)
    n11.add_edge(CharTransition("b"), n7)
    n5.add_edge(EpsilonTransition(), n8)
    n7.add_edge(EpsilonTransition(), n8)

    expected_nfa = FiniteAutomata(n0, {n8})
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_12():
    # test \, they should help recognize *, (, ), [, ], |, +, ?, etc
    for regex in (
        "*", "(", ")", "[", "]", "|", "+", "?", "."
    ):
        constructed_nfa = FiniteAutomata.from_string("\\" + regex)
        n0 = FiniteAutomataNode()
        n1 = FiniteAutomataNode()
        n0.add_edge(CharTransition(regex), n1)
        expected_nfa = FiniteAutomata(n0, {n1})
        assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_13():
    constructed_nfa = FiniteAutomata.from_string("[0-3]+")
    expected_nfa = FiniteAutomata.from_string("(0|1|2|3)+")
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_14():
    constructed_nfa = FiniteAutomata.from_string("'[^b]*'")
    expected_nfa = FiniteAutomata.from_string("'[ -ac-~]*'")
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_parsing_nfa_15():
    constructed_nfa = FiniteAutomata.from_string(r"'[^\']*'")
    expected_nfa = FiniteAutomata.from_string(r"'[ -&(-~]*'")
    assert hash(constructed_nfa) == hash(expected_nfa)


def test_fa_rev_edge_0():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(EpsilonTransition(), n0)
    fa = FiniteAutomata(n0, {n1})
    constructed_fa_rev = fa.reverse_edge()

    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n2.add_edge(EpsilonTransition(), n3)
    n3.add_edge(CharTransition("a"), n2)
    expected_fa_rev = FiniteAutomata(n3, {n2})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_fa_rev_edge_1():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)

    fa = FiniteAutomata(n0, {n2})
    constructed_fa_rev = fa.reverse_edge()

    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n5.add_edge(CharTransition("b"), n4)
    n4.add_edge(CharTransition("a"), n3)

    expected_fa_rev = FiniteAutomata(n5, {n3})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_fa_hash_0():
    # try attack hash function
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(EpsilonTransition(), n1)
    n0.add_edge(EpsilonTransition(), n2)
    n1.add_edge(CharTransition("a"), n2)
    n2.add_edge(CharTransition("b"), n1)

    m0 = FiniteAutomataNode()
    m1 = FiniteAutomataNode()
    m2 = FiniteAutomataNode()
    m0.add_edge(EpsilonTransition(), m2)
    m0.add_edge(EpsilonTransition(), m1)
    m1.add_edge(CharTransition("a"), m2)
    m2.add_edge(CharTransition("b"), m1)

    assert hash(FiniteAutomata(n0)) == hash(FiniteAutomata(m0))


def test_fa_hash_1():
    # test if hash function captures self-loop (edge that goes to itself...)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("a"), n0)

    m0 = FiniteAutomataNode()
    m1 = FiniteAutomataNode()
    m0.add_edge(CharTransition("a"), m1)

    assert hash(FiniteAutomata(n0)) != hash(FiniteAutomata(m0))


def test_fa_repr():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    fa = FiniteAutomata(n0)
    r = repr(fa)
    assert r.strip() == "0 -a> 1"


def test_dfa_0():
    constructed_dfa = FiniteAutomata.from_string("a").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_1():
    constructed_dfa = FiniteAutomata.from_string("a|b").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n2)
    expected_dfa = FiniteAutomata(n0, {n1, n2})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_2():
    constructed_dfa = FiniteAutomata.from_string("a*").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_3():
    constructed_dfa = FiniteAutomata.from_string("a?").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_4():
    constructed_dfa = FiniteAutomata.from_string("abc").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = FiniteAutomata(n0, {n3})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_5():
    constructed_dfa = FiniteAutomata.from_string("pub|pri").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()
    n0.add_edge(CharTransition("p"), n1)
    n1.add_edge(CharTransition("u"), n2)
    n1.add_edge(CharTransition("r"), n4)
    n2.add_edge(CharTransition("b"), n3)
    n4.add_edge(CharTransition("i"), n5)
    expected_dfa = FiniteAutomata(n0, {n3, n5})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_6():
    # test if middle accepts are recognized
    constructed_dfa = FiniteAutomata.from_string("a|abc").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("c"), n3)
    expected_dfa = FiniteAutomata(n0, {n1, n3})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_7():
    constructed_dfa = FiniteAutomata.from_string("a+").determinize()
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)  # {0}
    n1.add_edge(CharTransition("a"), n2)  # {1, 2, 4, 3}
    n2.add_edge(CharTransition("a"), n2)  # {5, 4, 3}
    expected_dfa = FiniteAutomata(n0, {n1, n2})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_min_dfa_0():
    # the result of (a|b)+ could be further simplified by DFA minimization
    constructed_dfa = FiniteAutomata.from_string("abb(a|b)+", minimize=True)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("b"), n3)
    n3.add_edge(CharTransition("a"), n4)
    n3.add_edge(CharTransition("b"), n4)
    n4.add_edge(CharTransition("a"), n4)
    n4.add_edge(CharTransition("b"), n4)

    expected_dfa = FiniteAutomata(n0, {n4})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_min_dfa_1():
    # NOTE: this is NOT MINIMAL, but almost.
    # it's caused by manually added start_node that connects to all accept states.
    # e.g. consider DFA (0) -ab> (1), (1) -ab> (1). The reversed NFA would be
    # 2 -ϵ> 1, 2 -ϵ> (0), 1 -ab> 1, 1 -ab> (0).
    # Thus the ϵ-closure would be {2, 1, 0} -ab> {1, 0}, {1, 0} -ab> {1, 0},
    # which corresponds to n0 & n1 down there.
    # TODO: Try to find a way to eliminate that redundant node, e.g. remove start_node from closure?
    constructed_dfa = FiniteAutomata.from_string("((ϵ|a)b*)*", minimize=True)
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n1)
    n1.add_edge(CharTransition("a"), n1)
    n1.add_edge(CharTransition("b"), n1)
    expected_dfa = FiniteAutomata(n0, {n0, n1})
    assert hash(constructed_dfa) == hash(expected_dfa)


def test_dfa_iter_0():
    dfa = FiniteAutomata.from_string("a*")
    for target, expected in (
        ("aabaaabba", "aa"),
        ("baaaa", None)
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_1():
    dfa = FiniteAutomata.from_string("0|(1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*")
    for target, expected in (
        ("10872865 168505", "10872865"),
        ("010101", "0"),
        ("7950X3D", "7950")
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_2():
    dfa = FiniteAutomata.from_string("([a-zA-Z]|_)([a-zA-Z0-9]|_)*")
    for target, expected in (
        ("FiniteAutomata.from_string('a*')", "FiniteAutomata"),
        ("__init__(self)", "__init__"),
        ("n7.add_edge(CharTransition('b'), n7)", "n7"),
        ("1 + 2", None)
    ):
        assert dfa.match_first(target) == expected


def test_dfa_iter_3():
    dfa = FiniteAutomata.from_string(r"/\*.*\*/")

    for target, expected in (
        ("/* ([a-zA-Z]|_)([a-zA-Z0-9]|_)* */", "/* ([a-zA-Z]|_)([a-zA-Z0-9]|_)* */"),
        ("/*comment*/?ok", "/*comment*/"),
        ("int i = 0; /* initialize index var */", None)
    ):
        assert dfa.match_first(target) == expected


def test_dfa_rev_edge_0():
    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()

    n0.add_edge(CharTransition("a"), n1)
    n0.add_edge(CharTransition("b"), n2)
    n2.add_edge(CharTransition("a"), n1)
    n2.add_edge(CharTransition("b"), n2)

    fa = FiniteAutomata(n0, {n1})
    constructed_fa_rev = fa.reverse_edge()

    n3 = FiniteAutomataNode()
    n4 = FiniteAutomataNode()
    n5 = FiniteAutomataNode()

    n4.add_edge(CharTransition("a"), n3)
    n4.add_edge(CharTransition("a"), n5)
    n5.add_edge(CharTransition("b"), n5)
    n5.add_edge(CharTransition("b"), n3)

    expected_fa_rev = FiniteAutomata(n4, {n3})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)


def test_dfa_rev_edge_1():
    constructed_fa_rev = FiniteAutomata.from_string("a|b*").determinize().reverse_edge()

    n0 = FiniteAutomataNode()
    n1 = FiniteAutomataNode()
    n2 = FiniteAutomataNode()
    n3 = FiniteAutomataNode()
    n1.add_edge(CharTransition("a"), n0)
    n2.add_edge(CharTransition("b"), n0)
    n2.add_edge(CharTransition("b"), n2)
    n3.add_edge(EpsilonTransition(), n0)
    n3.add_edge(EpsilonTransition(), n1)
    n3.add_edge(EpsilonTransition(), n2)

    expected_fa_rev = FiniteAutomata(n3, {n0})
    assert hash(constructed_fa_rev) == hash(expected_fa_rev)

