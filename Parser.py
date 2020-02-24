from collections import deque
from typeDef import TypeDefinition
from cfg import ContextFreeGrammar
from action import Action
from goto import Goto
from parseTree import PTNode, ParseTree
import scanner


FOLDER = "simpleJava/"
EMPTY = ""


def firstOfSym(result, cfg, sym, firstDict=None) -> bool:
    """
    Calculate the first set of given symbol, and write the 
    result into the reference of set "result".

    Return bool value, indicating whether the first of this 
    symbol contains EMPTY or not.
    """
    if firstDict is not None:
        return firstDict[sym]
    hasEmpty = False
    for productionID in cfg.getProductions(sym):
        hasEmpty |= firstOfSeq(result, cfg, cfg.getProduction(productionID)[1], firstDict)
    return hasEmpty


def firstOfSeq(result, cfg, sequence, firstDict=None) -> bool:
    """
    Calculate the first set of given sequence and cfg.

    Use reference of set "result" to avoid newing temp sets 
    to accelerate.
    """
    hasEmpty = False
    hasNonTerminal = False
    allNonTerminalHasEmpty = True
    for sym in sequence:
        if cfg.isTerminal(sym) or cfg.isEOF(sym):
            result.add(sym)
            break
        elif cfg.isNonTerminal(sym):
            hasNonTerminal = True
            if firstDict is not None:
                result |= firstDict[sym]
                allNonTerminalHasEmpty &= EMPTY in firstDict[sym]
            else:
                allNonTerminalHasEmpty &= firstOfSym(result, cfg, sym, firstDict)
            if not allNonTerminalHasEmpty:
                break
        elif sym == EMPTY:
            result.add(EMPTY)
            hasEmpty = True
            break
    hasEmpty |= hasNonTerminal and allNonTerminalHasEmpty
    if not hasEmpty:
        result.discard(EMPTY)
    return hasEmpty


def updNonTerminalFirst(result, cfg, non) -> bool:
    ntHasEmpty = False
    for id_ in cfg.getProductions(non):
        hasNonTerminal = False
        allNonTerminalHasEmpty = True
        for sym in cfg.getProduction(id_)[1]:
            if cfg.isTerminal(sym):
                result[non].add(sym)
                break
            elif cfg.isNonTerminal(sym):
                hasNonTerminal = True
                allNonTerminalHasEmpty &= updNonTerminalFirst(result, cfg, sym)
                result[non] |= result[sym]
                if not allNonTerminalHasEmpty:
                    break
            elif sym == EMPTY:
                ntHasEmpty = True
                break
        ntHasEmpty |= hasNonTerminal and allNonTerminalHasEmpty
    if ntHasEmpty:
        result[non].add(EMPTY)
    else:
        result[non].discard(EMPTY)
    return ntHasEmpty


def first(cfg) -> dict:
    """
    Calculate the first set of a given cfg
    """
    result = {k: set() for k in cfg.nonTerminals}
    for non, _ in cfg.nonTerminalToProdIDs.items():
        if not result[non]:
            updNonTerminalFirst(result, cfg, non)
    return result


class LRItem:

    """
    Is in fact a tri-tuple (productionID, dotPosition, lookForward)
    lookForward is a set, containing a set of id of terminals.
    """

    def __init__(self, cfg, productionID, dotPos=0, lookForward=None):
        self.cfg = cfg
        self.productionID = productionID
        self.dotPos = dotPos
        self.lookForward = lookForward  # WARNING: REFERENCE IS SHARED FOR
                                        # PERFORMANCE. AVOID EDITING THIS.
        self.__hashVal = None
    
    def __eq__(self, other):
        return self.productionID == other.productionID and \
            self.dotPos == other.dotPos and \
                self.lookForward == other.lookForward
            
    def __hash__(self):
        if self.__hashVal is None:
            self.__hashVal = hash((
                self.productionID, self.dotPos, 
                hash(tuple(sorted(list(self.lookForward), key=str)))
            ))
        return self.__hashVal
    
    def __str__(self):
        return "(%s, %s, %r)" % (self.productionID, self.dotPos, self.lookForward)
    
    def __repr__(self):
        return repr(str(self))
    
    def __lt__(self, other):
        """
        LRItemSet would need static order of LRItem to calculate hash.
        """
        if self.productionID == other.productionID:
            if self.dotPos == other.dotPos:
                return hash(self) < hash(other)
            return self.dotPos < other.dotPos
        return self.productionID < other.productionID

    def get(self, offset=0):
        return self.cfg.get(self.productionID, self.dotPos, offset)
    
    def gotoNext(self):
        return LRItem(self.cfg, self.productionID, self.dotPos + 1, self.lookForward)
    
    def atEnd(self) -> bool:
        prod = self.cfg.getProduction(self.productionID)[1]
        return len(prod) == self.dotPos or prod == ("", )


sequenceToFirst = {}


class LRItemSet:

    def __init__(self, cfg):
        self.cfg = cfg
        self.items = set()
        self.__needRecalculateHash = True  # lazy tag
        self.__hashVal = None
        self.__map = {}  # Map "step" to a list of item reference, in order to accelerate.

    def __hash__(self):
        if self.__needRecalculateHash:
            self.__hashVal = hash(tuple(sorted(list(self.items))))  # TIME COSTING
            self.__needRecalculateHash = False
        return self.__hashVal
    
    def __eq__(self, other):
        return self.items == other.items
    
    def __str__(self):
        return str(self.items)
    
    def addItem(self, item):
        if item not in self.items:
            self.items.add(item)
            self.__needRecalculateHash = True

    def getNext(self):
        """
        get all possible out-pointing edges toward other LRItemSets.
        """
        result = set()
        for item in self.items:
            step = item.get()
            if step is not None and step != "":
                self.__map.setdefault(step, []).append(item)
                result.add(step)
        return result

    def goto(self, step):
        """
        return a new LRItemSet.
        """
        result = LRItemSet(self.cfg)
        for item in self.__map[step]:
            result.addItem(item.gotoNext())
        return result

    def calcClosure(self, firstDict):
        """
        Return a new LRItemSet, which is the closure of self.
        """
        que = deque(self.items)
        record = {}
        while que:
            cur = que.pop()
            core = (cur.productionID, cur.dotPos)
            record.setdefault(core, set())
            record[core] |= cur.lookForward

            curSym = cur.get()  # symbol at current dot position

            if self.cfg.isNonTerminal(curSym):
                prod = self.cfg.getProduction(cur.productionID)[1][cur.dotPos + 1:]
                newProds = [prod + (lookForwardSym, ) for lookForwardSym in cur.lookForward]  # precalc to accelerate
                firstSets = []

                for newProd in newProds:
                    if newProd not in sequenceToFirst:
                        firstSet = set()
                        firstOfSeq(firstSet, self.cfg, newProd, firstDict)
                        sequenceToFirst[newProd] = firstSet
                    firstSets.append(sequenceToFirst[newProd])

                for productionID in self.cfg.getProductions(curSym):
                    newCore = (productionID, 0)
                    for firstSet in firstSets:
                        if newCore not in record or not firstSet.issubset(record[newCore]):
                            que.append(LRItem(self.cfg, productionID, 0, firstSet))

        result = LRItemSet(self.cfg)
        for k, v in record.items():
            v.discard(EMPTY)
            result.addItem(LRItem(self.cfg, *k, v))
        return result


def symToString(typedef, sym):
    if isinstance(sym, int):
        return typedef.getDisplayName(sym)
    return sym if sym != EMPTY else "''"


def itemToString(typedef, item):
    non, seq = item.cfg.getProduction(item.productionID)
    seqStr = " ".join(symToString(typedef, _) for _ in seq[:item.dotPos]) \
             + "." \
             + " ".join(symToString(typedef, _) for _ in seq[item.dotPos:])
    lfStr = "%s" % "/".join(sorted(symToString(typedef, _) for _ in item.lookForward))
    return "%s -> %s, %s" % (non, seqStr, lfStr)


def itemSetToString(typedef, itemSet):
    return '\n'.join(sorted(itemToString(typedef, _) for _ in itemSet.items))


def toStr(typedef, obj):
    if isinstance(obj, LRItemSet):
        return itemSetToString(typedef, obj)
    elif isinstance(obj, LRItem):
        return itemToString(typedef, obj)
    else:
        return symToString(typedef, obj)


def debugDetail(item, typedef, IDToItem, cfg):
    if isinstance(item, int):
        print("Detail of ItemSet ID %d:\n%s" % (item, toStr(typedef, IDToItem[item])))
    elif isinstance(item, tuple):
        print("Detail of Action %s:" % str(item))
        actionType, op = item
        if actionType == 0:  # shift
            print("ItemSet ID %d:\n%s" % (op, toStr(typedef, IDToItem[op])))
        elif actionType == 1:
            print("Production ID %d:\n%s" % (op, cfg.IDToGrammar[op]))


def debug(src, step, dst, table, tableName, collisionItem, typedef, IDToItem, cfg):
    print("=" * 50)
    print(
        "[ERROR] NOT LR 1 GRAMMAR: %s[%d][%s] has already been taken, value: %r. Trying to put: %r." \
        % (tableName, src, step, table[src][step], collisionItem)
    )
    print(
        ("Source: Item %d:\n%s\n" % (src, toStr(typedef, IDToItem[src]))) + \
        ("Step: %s\n" % toStr(typedef, step)) + \
        ("Dest Item %d:\n%s" % (dst, toStr(typedef, IDToItem[dst])) if dst is not None else "")
    )
    debugDetail(table[src][step], typedef, IDToItem, cfg)
    debugDetail(collisionItem, typedef, IDToItem, cfg)


def genActionGoto(typedef, cfg, needItemToID=False):
    cfgForFirst = cfg.removeLeftRecursion() if cfg.isLeftRecursive() else cfg
    firstDict = first(cfgForFirst)

    initProdID = cfg.nonTerminalToProdIDs[cfg.startSymbol][0]
    initItem = LRItem(cfg, initProdID, 0, {"$"})

    initItemSet = LRItemSet(cfg)
    initItemSet.addItem(initItem)
    initItemSet = initItemSet.calcClosure(firstDict)

    que = deque([initItemSet])
    edges = {}

    itemToID = {}
    coreToClosure = {}  # calculate closure is time-costing. Thus use a dict to accelerate.
    while que:
        cur = que.popleft()
        if cur not in itemToID:
            itemToID[cur] = len(itemToID)
        for step in cur.getNext():
            nextItemSetCore = cur.goto(step)  # get the core first

            if nextItemSetCore not in coreToClosure:
                coreToClosure[nextItemSetCore] = nextItemSetCore.calcClosure(firstDict)
            nextItemSet = coreToClosure[nextItemSetCore]

            if nextItemSet not in itemToID:
                itemToID[nextItemSet] = len(itemToID)
                que.append(nextItemSet)
            edges.setdefault(itemToID[cur], []).append((step, itemToID[nextItemSet]))
    
    # for k, v in itemToID.items():
    #     print(v)
    #     print(toStr(typedef, k))

    # TODO delete this after debug
    IDToItem = {v: k for k, v in itemToID.items()}

    action, goto = Action(cfg, len(itemToID)), Goto(cfg, len(itemToID))
    for src, v in edges.items():
        for step, dst in v:
            # src, step, dst forms a full edge. note that src and dst are int.
            # print("%d -> %d via %r" % (src, dst, step))
            if cfg.isTerminal(step):
                if action[src][step] is not None:
                    debug(src, step, dst, action, "action", (0, dst), typedef, IDToItem, cfg)
                else:
                    action[src][step] = (0, dst)  # 0 means Shift
            elif cfg.isNonTerminal(step):
                if goto[src][step] is not None:
                    debug(src, step, dst, goto, "goto", dst, typedef, IDToItem, cfg)
                else:
                    goto[src][step] = dst

    for k, v in itemToID.items():
        for item in k.items:
            # print(toStr(typedef, item), item.atEnd())
            if item.atEnd():
                for sym in item.lookForward:
                    if action[v][sym] is not None:
                        debug(v, sym, None, action, "action", (1, item.productionID), typedef, IDToItem, cfg)
                    else:
                        if item.productionID:
                            action[v][sym] = (1, item.productionID)  # 1 means Reduce
                        else:
                            action[v][sym] = (2, None)  # 2 means Accept
    if needItemToID:
        return action, goto, itemToID
    else:
        return action, goto


def parse(tokenList, typedef, cfg, action=None, goto=None):
    if action is None or goto is None:
        action, goto = genActionGoto(typedef, cfg)
    
    stateStack, nodeStack = [0], [PTNode(cfg.EOF)]  # PTNode Objects in nodeStack

    # lexStr is the lexical string; token type is int.
    for lexStr, tokenType in tokenList:
        currentState = stateStack[-1]
        while True:
            # print(currentState, typedef.getName(tokenType))
            if action[currentState][tokenType] is None:
                print("ERROR: %s, %s" % (currentState, tokenType))
                exit()
            actionType, nextState = action[currentState][tokenType]
            if actionType == 0:  # shift to another state
                stateStack.append(nextState)
                nodeStack.append(PTNode(lexStr))
                break
            elif actionType == 1:
                prodID = nextState
                nonTerminal, sequence = cfg.getProduction(prodID)
                # print("Reduce using grammar %d: %s -> %r" % (prodID, nonTerminal, sequence))
                nonTerminalNode = PTNode(nonTerminal, prodID=prodID)
                for i in range(len(sequence) - 1, -1, -1):
                    symbol = sequence[i]
                    if symbol == EMPTY:
                        continue
                    currentSymbol = nodeStack.pop()
                    stateStack.pop()
                    assert isinstance(currentSymbol, PTNode)
                    nonTerminalNode.addChild(currentSymbol)
                nonTerminalNode.reverse()

                currentState = stateStack[-1]
                nextState = goto[currentState][nonTerminal]
                stateStack.append(nextState)
                nodeStack.append(nonTerminalNode)
                currentState = stateStack[-1]
                continue
            elif actionType == 2:
                # print("Accepted")
                break
            else:
                assert False

        # print(stateStack, nodeStack, tokenType, actionType, nextState)
    # print(nodeStack)
    return ParseTree(nodeStack[-1])


if __name__ == "__main__":
    typedef = TypeDefinition.load(FOLDER + "typedef")
    cfg = ContextFreeGrammar.load(typedef, FOLDER + "simpleJavaCFG")
    # action.save(FOLDER + "simpleJavaAction")
    # goto.save(FOLDER + "simpleJavaGoto")
    # exit()
    action = Action.load(cfg, FOLDER + "simpleJavaAction")
    goto = Goto.load(cfg, FOLDER + "simpleJavaGoto")

    with open(FOLDER + "test.sjava", "r") as f:
        src = f.read()
    tokenList = scanner.parse(typedef, src, ['line_comment', 'block_comment', 'space'])
    print(tokenList)
    pt = parse(tokenList, typedef, cfg, action, goto)
    print(pt)
