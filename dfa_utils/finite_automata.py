from collections import deque
from typing import Callable, Deque, Dict, Set, Tuple, List, Self
from finite_automata_node import (
    CharTransition,
    FiniteAutomataNode,
    Transition,
    EpsilonTransition,
)


class FiniteAutomata:
    def __init__(self, start_node: FiniteAutomataNode) -> None:
        self.start_node = start_node

    def __repr__(self) -> str:
        # iterate through all FA Nodes, in dfs fashion?
        node_id: Dict[FiniteAutomataNode, int] = {}
        counter = 0
        format_node: Callable[[FiniteAutomataNode], str] = lambda node: "\n".join(
            "%s %r %s"
            % (
                ("(%d)" if node.is_accept else "%d") % node_id[node],
                cond,
                ("(%d)" if nxt.is_accept else "%d") % node_id[nxt],
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
            if node.is_accept and all(visit_order[nxt_node] <= visit_order[node] for _, nxt_node in edge):
                second_pass_que.append(
                    node
                )  # current node is a sink node: no out edge, or all out edges are back edges

        node_hash: Dict[FiniteAutomataNode, int] = {
            node: len(node.successors) + (10000 * node.is_accept)
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
