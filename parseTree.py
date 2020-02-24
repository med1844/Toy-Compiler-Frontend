from tree import TreeNode, Tree


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


class ParseTreeActionRegister:

    def __init__(self, cfg):
        self.__productionToAction = {}
        self.__cfg = cfg

    def production(self, *productions, index=-1):
        """
        register a function to run at some position in the production

        @tree.production('E -> E "+" T')
        def foo(e, e1, plus, t):
            return "bar"
        """
        def decorate(function):
            for prod in productions:
                self.__productionToAction.\
                    setdefault(self.__cfg.rawGrammarToID[prod], {})\
                        [index] = function
            return function
        return decorate
    
    def getProductionMapping(self):
        return self.__productionToAction
    

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