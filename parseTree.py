from typing import Callable, Dict, Tuple
from cfg import ContextFreeGrammar
from io_utils.to_json import ToJson
from tree import TreeNode, Tree
import inspect
import itertools


class PTNode(TreeNode):
    def __init__(self, content, prodID=-1):
        # content may be either Token or Str
        super().__init__(content)
        super().setAttribute("__prodID", prodID)

    def getGrammarID(self) -> int:
        return super().getAttribute("__prodID")

    def __eq__(self, other):
        if isinstance(other, str):
            return self.getContent() == other
        elif isinstance(other, PTNode):
            return self.getContent() == other.getContent()

    def __getitem__(self, key):
        return self.getAttributes()[key]

    def __setitem__(self, key, value):
        self.getAttributes()[key] = value

    def reverse(self):
        self.getChilds().reverse()


class ParseTreeActionRegister(ToJson):
    def __init__(self, cfg: ContextFreeGrammar):
        self.__productionToAction: Dict[int, Tuple[int, str, Callable]] = {}
        self.__cfg = cfg

    def production(self, *productions: str):
        """
        register a function to run at some position in the production

        @tree.production('E -> E "+" T')
        def foo(e, e1, plus, t):
            return "bar"
        """

        def decorate(function: Callable):
            for prod in productions:
                prod_id = self.__cfg.raw_grammar_to_id[prod]
                non_terminal, seq = self.__cfg.get_production(prod_id)
                self.__productionToAction[prod_id] = (
                    sum(map(lambda *_: 1, filter(lambda x: x != "''", seq))),
                    non_terminal,
                    function,
                )
            return function

        return decorate

    def getProductionMapping(self):
        return self.__productionToAction

    @staticmethod
    def preprocess_fn(fn: Callable) -> str:
        fn_src_lines = inspect.getsource(fn).split("\n")
        indent = min(
            sum(1 for _ in itertools.takewhile(str.isspace, line))
            for line in fn_src_lines
            if line
        )
        return "\n".join(
            filter(
                lambda x: not x.startswith("@"), map(lambda x: x[indent:], fn_src_lines)
            )
        )

    def to_json(self) -> Dict[int, Tuple[int, str, Tuple[str, str]]]:
        return {
            k: (
                nargs,
                non_terminal,
                (
                    fn.__name__,
                    self.preprocess_fn(fn),
                ),
            )
            for k, (nargs, non_terminal, fn) in self.__productionToAction.items()
        }


class ParseTree(Tree):
    def __init__(self, root):
        super().__init__(root)

    def evaluate(self, ar, currentNode=None):
        """
        evaluate the attributes according to the rules registered in ParseTreeActionRegister
        """
        productionToAction = ar.getProductionMapping()
        if currentNode is None:
            currentNode = self.getRoot()
        prodID = currentNode.getGrammarID()
        if prodID in productionToAction:
            for i, child in enumerate(currentNode.getChilds()):
                if prodID != -1 and i in productionToAction[prodID]:
                    productionToAction[prodID][i](currentNode, *currentNode.getChilds())
                self.evaluate(ar, currentNode=child)
            if prodID != -1 and -1 in productionToAction[prodID]:
                productionToAction[prodID][-1](currentNode, *currentNode.getChilds())


if __name__ == "__main__":
    node = PTNode("456")
    node.name = "123"
    print(node.name)
