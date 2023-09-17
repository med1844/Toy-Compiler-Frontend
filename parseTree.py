from typing import Callable, Dict, Tuple
from cfg import ContextFreeGrammar
from io_utils.to_json import ToJson
from tree import TreeNode, Tree
import inspect


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
        self.__productionToAction: Dict[int, Dict[int, Callable]] = {}
        self.__prod_nargs: Dict[int, int] = {}  # will be used during cfg parsing
        self.__cfg = cfg

    def production(self, *productions, index=-1):
        """
        register a function to run at some position in the production

        @tree.production('E -> E "+" T')
        def foo(e, e1, plus, t):
            return "bar"
        """
        def decorate(function: Callable):
            for prod in productions:
                prod_id = self.__cfg.raw_grammar_to_id[prod]
                self.__productionToAction.\
                    setdefault(prod_id, {})\
                [index] = function
                _, seq = self.__cfg.get_production(prod_id)
                self.__prod_nargs[prod_id] = len(seq)
            return function
        return decorate
    
    def getProductionMapping(self):
        return self.__productionToAction
    
    def to_json(self) -> Dict[int, Tuple[int, Dict[int, Tuple[str, str]]]]:
        return {k: (self.__prod_nargs[k], {kk: (vv.__name__, "\n".join(filter(lambda x: not x.startswith("@"), inspect.getsource(vv).split("\n")))) for kk, vv in v.items()}) for k, v in self.__productionToAction.items()}


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
