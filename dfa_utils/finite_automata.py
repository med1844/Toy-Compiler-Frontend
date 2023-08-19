from typing import Callable, Set
from finite_automata_node import FiniteAutomataNode


class FiniteAutomata:

    def __init__(self, start_node: FiniteAutomataNode) -> None:
        self.start_node = start_node

    def __repr__(self) -> str:
        # iterate through all FA Nodes, in dfs fashion?
        def dfs(cur_node: FiniteAutomataNode, action: Callable[[FiniteAutomataNode], None], visited: Set[int]):
            visited.add(cur_node.id)
            action(cur_node)
            for _, nxt_node in cur_node.successors:
                if nxt_node.id not in visited:
                    dfs(nxt_node, action, visited)
        buffer = []
        dfs(self.start_node, lambda node: buffer.append(repr(node)), set())
        return "\n".join(buffer)
