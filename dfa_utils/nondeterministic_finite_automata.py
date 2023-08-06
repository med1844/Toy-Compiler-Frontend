from typing import List, Tuple, Dict, Callable, Iterable, TypeVar, Deque
from finite_automata_node import FiniteAutomataNode
from collections import namedtuple, deque


T = TypeVar("T")


class NondeterministicFiniteAutomata(object):

    def __init__(self, start_node: FiniteAutomataNode, end_node: FiniteAutomataNode) -> None:
        self.start_node = start_node
        self.end_node = end_node

    @staticmethod
    def tokenize_regex(r: str) -> Iterable[str]:
        """
        Tokenize the regex for easier process...

        - `a|b*abb` -> `["a", "|", "b", "*", "abb"]`
        - `(abb|cdd)` -> `["(", "abb", "|", "cdd", ")"]`
        """
        i = 0
        special_chars = {"(", ")", "*", "|", "ϵ"}
        while i < len(r):
            # we are dealing with r[l:]; try to find one word
            if r[i] in special_chars:
                yield r[i]
                i += 1
            else:
                l = i
                while i < len(r) and r[i] not in special_chars:
                    i += 1
                yield r[l:i]

    # @classmethod
    # def parse(cls, r: List[str]) -> str:
    #     if r[-1] == "*":
    #         return "(*%s)" % cls.parse(r[:-1])

    #     def get_last_operand(r: List[str]) -> Tuple[str, int]:
    #         if r[-1] == ")":
    #             lvl = 0
    #             i = len(r) - 1
    #             while 0 <= i:
    #                 if r[i] == ")":
    #                     lvl += 1
    #                 if r[i] == "(":
    #                     lvl -= 1
    #                 if lvl == 0:
    #                     return (cls.parse(r[i + 1:-1]), i)
    #                 i -= 1
    #         if r[-1] not in {"*", "|"}:
    #             return (r[-1], len(r) - 1)
    #         raise ValueError("r just end with ')' or word: %s is not valid" % r[-1])

    #     operand, new_i = get_last_operand(r)
    #     if new_i > 0:
    #         if r[new_i - 1] == "|":
    #             return "(%s|%s)" % (cls.parse(r[:new_i - 1]), operand)
    #         else:
    #             return "(%s+%s)" % (cls.parse(r[:new_i - 1]), operand)
    #     else:
    #         return operand


    @classmethod
    def from_string(cls, r: str) -> "NondeterministicFiniteAutomata":

        def is_word(c: str):
            return c not in "|*()+"

        def build(start_node: FiniteAutomataNode, r: Deque[str]):
            # r -> s
            # r -> sr
            # r -> s|r
            # r -> (r)
            # r -> s*r
            # r -> s+r
            # r -> ϵ
            # s -> char

            s = r.popleft()
            if is_word(s):
                

        # """
        # - Build the postfix: a b * abb + |

        # - `a|b*abb` -> `a b * abb + |`
        # - `(a|b)*abb(ϵ|a|b)*` -> `a b | * abb ϵ a b | | * + +`
        # - `(abb|cdd)` -> `abb cdd |`
        # - `a*|b*` -> `a * b * |`
        # - `((a|b)*(cc|dd))*ee` -> `a b | * cc dd | + * ee +`
        # - `(ab*(c|d)*)|(e|(f*g))` -> `ab * c d | * + e f * g + | |`
        # - `abb(a|b)` -> `abb a b | +`
        # - `(a|b*)c` -> `a b * | c +`
        # """
        # # print(r)

        # op_pri = {
        #     "*": 3,
        #     "+": 2,
        #     "|": 1
        # }

        # op_stack: List[str] = []
        # operands: List[str] = []

        # def add_operator(op: str):
        #     while op_stack and op_stack[-1] != "(" and op_pri[op_stack[-1]] > 

        # for c in reversed(list(cls.tokenize_regex(r))):
        #     if c == ")":
        #         op_stack.append(c)
        #     elif c == "(":
        #         temp_operands = []
        #         while op_stack and op_stack[-1] != "(":
        #             rr, ll = operands.pop(), operands.pop()
        #             temp_operands.append("(%s%s%s)" % (ll, op_stack.pop(), rr))
        #         op_stack.pop()
        #         while len(temp_operands) > 1:
        #             rr, ll = temp_operands.pop(), temp_operands.pop()
        #             temp_operands.append("(%s+%s)" % (ll, rr))
        #         if temp_operands:
        #             operands.append(temp_operands.pop())
        #     elif c in "|":
        #         op_stack.append(c)
        #     elif c in "*":
        #         op_stack.append(c)
        #     else:
        #         operands.append(c)
        #     print("0. op stack:", op_stack)
        #     print("1. operands:", operands)

        # while op_stack:
        #     rr, ll = operands.pop(), operands.pop()
        #     operands.append("(%s%s%s)" % (ll, op_stack.pop(), rr))

        # print("0. op stack:", op_stack)
        # print("1. operands:", operands)

        # while len(operands) > 1:
        #     rr, ll = operands.pop(), operands.pop()
        #     operands.append("(%s+%s)" % (ll, rr))

        # return eval_postfix(operands)


# code written by new bing:
# class Node:
#     def __init__(self, value):
#         self.value = value
#         self.left = None
#         self.right = None

# def parse_regex(regex):
#     stack = []
#     for char in regex:
#         if char == '(':
#             stack.append(char)
#         elif char == ')':
#             subexpr = ''
#             while stack and stack[-1] != '(':
#                 subexpr = stack.pop() + subexpr
#             if not stack:
#                 raise ValueError('Unbalanced parentheses')
#             stack.pop()
#             node = parse_subexpr(subexpr)
#             stack.append(node)
#         else:
#             stack.append(char)

#     if '(' in stack or ')' in stack:
#         raise ValueError('Unbalanced parentheses')

#     return parse_subexpr(stack)

# def parse_subexpr(subexpr):
#     if not subexpr:
#         return None

#     # Handle concatenation
#     for i in range(len(subexpr)-1, -1, -1):
#         if isinstance(subexpr[i], Node) or (subexpr[i] not in '*|'):
#             node = Node('+')
#             node.left = parse_subexpr(subexpr[:i+1])
#             node.right = parse_subexpr(subexpr[i+1:])
#             return node

#     # Handle alternation
#     for i in range(len(subexpr)-1, -1, -1):
#         if subexpr[i] == '|':
#             node = Node('|')
#             node.left = parse_subexpr(subexpr[:i])
#             node.right = parse_subexpr(subexpr[i+1:])
#             return node

#     # Handle Kleene star
#     if isinstance(subexpr[-1], Node) or (subexpr[-1] != '*'):
#         return parse_subregex_unit(subexpr[-1])
    
#     node = Node('*')
#     node.left = parse_subregex_unit(parse_subregex_unit[:-2])
    
# def parse_subregex_unit(unit):
#     if isinstance(unit, Node):
#         return unit
    
#     return Node(unit)

# # Example usage:

# tree_root_node=parse_regex('(a|b)*abb')


def test_tokenizer():
    for regex, expected_output in (
        ("ab", ["ab"]),
        ("a|b", ["a", "|", "b"]),
        ("ab|cd", ["ab", "|", "cd"]),
        ("a|b*abb", ["a", "|", "b", "*", "abb"]),
        ("(35)*124", ["(", "35", ")", "*", "124"]),
        ("(a|ϵ)*", ["(", "a", "|", "ϵ", ")", "*"])
    ):
        assert list(NondeterministicFiniteAutomata.tokenize_regex(regex)) == expected_output


if __name__ == "__main__":
    def rebuild_infix(p: List[str]) -> str:
        stack = []
        for c in p:
            if c == "*":
                stack.append("(%s*)" % (stack.pop()))
            elif c == "|":
                r = stack.pop()
                l = stack.pop()
                stack.append("(%s|%s)" % (l, r))
            elif c == "+":
                r = stack.pop()
                l = stack.pop()
                stack.append("(%s+%s)" % (l, r))
            else:
                stack.append(c)

        return stack.pop()


    for regex, target_lisp in (
        ("ab", "ab"),
        ("a|b", "(a|b)"),
        ("ab|cd", "(ab|cd)"),
        ("ab*|cd", "((ab*)|cd)"),
        ("a|b*", "(a|(b*))"),
        ("abc|cde", "(abc|cde)"),
        ("a|b*abb", "(a|((b*)+abb)"),
        ("(35)*124", "((35*)+124)"),
        ("(a|b)*abb", "(((a|b)*)abb)"),
        ("(a|b)*abb(ϵ|a|b)*", "((((a|b)*)+abb)+(((ϵ|a)|b)*))"),
        ("(ab*(c|d)*)|(e|(f*g))", "(((ab*)+((c|d)*))|(e|((f*)+g)))"),
        ("a*bcc|c*dee", "(((a*)+bcc)|((c*)+dee))"),
        # [a], [+]
        # [(a*)], [+]
        # [(a*), bcc], [+]
        # [(a*), bcc], [+] -> evaluate ops with higher priority than | -> [((a*)+bcc)], [|]
        # [((a*)+bcc), c], [|, +]
        # [((a*)+bcc), (c*)], [|, +],
        # [((a*)+bcc), (c*), dee], [|, +, +]
        # [((a*)+bcc), ((c*)+dee)], [|]
        # [(((a*)+bcc)+((c*)+dee))]
        ("(a|b)c*d", "((a|b)+(c*)+d)"),
    ):
        print(NondeterministicFiniteAutomata.from_string(regex, rebuild_infix), target_lisp)
