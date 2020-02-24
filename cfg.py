from typeDef import TypeDefinition


class ContextFreeGrammar:

    """
    production:
        nonTerminal -> sequence | sequence | ...
    
    The cfg parser will first split input to python tuples, 
    record both nonTerminals and all symbols, and give ID to each production.
    Then using terminals = allSymbols - nonTerminals, we can get terminals.
    """

    SUBSTITUTE = "_"
    EOF = "$"

    @staticmethod
    def load(typeDef, fileName):
        """
        Given type definition and fileName, create and return a CFG object.
        """
        assert isinstance(typeDef, TypeDefinition)
        nonTerminals = set()
        allSymbol = set()
        grammarToID = {}
        rawGrammarToID = {}
        startSymbol = None

        temp = []

        with open(fileName, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                nonTerminal, seqs = line.split(" -> ")

                if startSymbol is None:
                    startSymbol = nonTerminal
                nonTerminals.add(nonTerminal)
                allSymbol.add(nonTerminal)

                for seq in seqs.split(" | "):
                    symbols = seq.split(" ")
                    temp.append((nonTerminal, symbols))
                    rawGrammarToID["%s -> %s" % (nonTerminal, seq)] = \
                        len(rawGrammarToID)
                    for symbol in seq.split(" "):
                        allSymbol.add(symbol)

        for i, (nonTerminal, symbols) in enumerate(temp):
            symbols = tuple("" if sym == "''"
                            else typeDef.getIDByDisplayName(sym) if sym not in nonTerminals
                            else sym
                            for sym in symbols)
            grammarToID[(nonTerminal, symbols)] = i

        terminals = {typeDef.getIDByDisplayName(_)
                     for _ in allSymbol - nonTerminals if _ != "''"}

        return ContextFreeGrammar(typeDef, terminals, nonTerminals,
                                  startSymbol, grammarToID, rawGrammarToID)

    def __init__(self, typeDef, terminals, nonTerminals,
                 startSymbol, grammarToID, rawGrammarToID):
        self.typeDef = typeDef
        self.terminals = terminals
        self.nonTerminals = nonTerminals
        self.startSymbol = startSymbol
        self.grammarToID = grammarToID
        self.rawGrammarToID = rawGrammarToID
        self.IDToGrammar = {v: k for k, v in self.grammarToID.items()}
        self.nonTerminalToProdIDs = {}

        for k, v in grammarToID.items():
            self.nonTerminalToProdIDs.setdefault(k[0], list()).append(v)
        
    def __str__(self):
        return str(self.grammarToID)
    
    def get(self, productionID, dotPos, offset=0):
        """
        Given a production id, and the dot position, return the symbol at that 
        position.

        eg: 
            (E, (E, +, T)): 6
            calling get(6, 1) would return +.
        
        if dotPos + offset is out of bound, it would return None.
        """
        if dotPos + offset >= len(self.IDToGrammar[productionID][1]):
            return None
        return self.IDToGrammar[productionID][1][dotPos + offset]
    
    def getProduction(self, productionID):
        """
        Return the sequence of a given production.

        eg:
            (E, (E, +, T)): 6
            calling getProduction(6) would return (E, (E, +, T))
        """
        return self.IDToGrammar[productionID]

    def isNonTerminal(self, op):
        return op in self.nonTerminals
    
    def isTerminal(self, op):
        return op in self.terminals
    
    def getProductions(self, nonTerminal):
        """
        Return list of production ids that the nonTerminal can lead to.
        WARNING: DO NOT MODIFY THE RETURN VALUE.
        """
        return self.nonTerminalToProdIDs[nonTerminal]
    
    def isLeftRecursive(self):
        for nonTerminal, ids in self.nonTerminalToProdIDs.items():
            for id_ in ids:
                if nonTerminal == self.getProduction(id_)[1][0]:
                    return True
        return False
    
    def __getLeftRecursionFreeProduction(self, nonTerminal, ids):
        subNonTerminal = nonTerminal + self.SUBSTITUTE
        grammarList, subGrammarList = [], []
        for id_ in ids:
            grammar = self.getProduction(id_)[1]
            if nonTerminal == grammar[0]:
                subGrammarList.append(grammar[1:] + (subNonTerminal, ))
            else:
                grammarList.append(grammar + (subNonTerminal, ))
        return (nonTerminal, tuple(grammarList)), (subNonTerminal, tuple(subGrammarList))
    
    def removeLeftRecursion(self):
        """
        Return a new ContextFreeGrammar object, containing no left recursion.
        if:
            A -> A a1 | A a2 | A a3 | ... | b1 | b2 | b3 | ... 
        then change to:
            A -> b1 A_ | b2 A_ | b3 A_ | ...
            A_ -> a1 A_ | a2 A_ | a3 A_ | ...
        """
        resultGrammarToID = {}
        resultNonTerminals = set(self.nonTerminals)
        for nonTerminal, ids in self.nonTerminalToProdIDs.items():
            isRecursive = False
            for id_ in ids:
                if nonTerminal == self.getProduction(id_)[1][0]:  # left recursive
                    isRecursive = True
                    break
            if isRecursive:
                (newNonTerminal, newProduction), (newSubNonTerminal, newSubProduction) = \
                    self.__getLeftRecursionFreeProduction(nonTerminal, ids)
                resultNonTerminals.add(newSubNonTerminal)
                for prod in newProduction:
                    resultGrammarToID[(newNonTerminal, prod)] = len(resultGrammarToID)
                for prod in newSubProduction:
                    resultGrammarToID[(newSubNonTerminal, prod)] = len(resultGrammarToID)
            else:
                for id_ in ids:
                    resultGrammarToID[self.getProduction(id_)] = len(resultGrammarToID)
        return ContextFreeGrammar(self.typeDef, self.terminals, resultNonTerminals,
                                  self.startSymbol, resultGrammarToID, self.rawGrammarToID)
    
    def isEOF(self, sym):
        return sym == '$'
        

if __name__ == "__main__":
    typedef = TypeDefinition.load("simpleJava/typedef")
    cfg = ContextFreeGrammar.load(typedef, "simpleJava/CFG")
    print(cfg.typeDef)
    print(cfg.terminals)
    print(cfg.nonTerminals)
    print(cfg.startSymbol)
    print(cfg.grammarToID)
    print(cfg.rawGrammarToID)