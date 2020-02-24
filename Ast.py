from tree import TreeNode, Tree


class ASTNode(TreeNode):

    def __init__(self, content, *childs, actionID=None):
        if actionID is None:
            actionID = content
        super().__init__(content)
        for child in childs:
            super().addChild(child)
        super().setAttribute("__actionID", actionID)
    
    def __str__(self):
        return str(self.getContent())

    def __repr__(self):
        return repr(self.getContent())
    
    def getActionIdentifier(self):
        return super().getAttribute("__actionID")


class ASTActionRegister:
    
    def __init__(self):
        self.__idToAction = {}
        self.__indexIdToAction = {}

    def action(self, *actionIDs, index=-1):
        """
        register a function to run at ASTNodes with certain actionIDs
        if atBegin is True, then the action will be executed before 
        its childs
        """
        def decorate(function):
            for action in actionIDs:
                if index != -1:
                    self.__indexIdToAction.setdefault(str(action), {})\
                        [index] = function
                else:
                    self.__idToAction[str(action)] = function
            return function
        return decorate
    
    def getMapping(self):
        return self.__idToAction
    
    def getIndexMapping(self):
        return self.__indexIdToAction


class AbstractSyntaxTree(Tree):

    def __init__(self, root):
        assert isinstance(root, ASTNode)
        super().__init__(root)

    def evaluate(self, ar, currentNode=None):
        """
        evaluate the attributes according to the rules registered in ASTActionRegister
        """
        index = ar.getIndexMapping()
        m = ar.getMapping()
        if currentNode is None:
            currentNode = self.getRoot()
        actionID = currentNode.getActionIdentifier()
        for i, child in enumerate(currentNode.getChilds()):
            if actionID in index and i in index[actionID]:
                index[actionID][i](currentNode, *currentNode.getChilds())
            self.evaluate(ar, currentNode=child)
        if actionID in m:
            m[actionID](currentNode, *currentNode.getChilds())
