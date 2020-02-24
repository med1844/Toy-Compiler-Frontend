class Goto:

    def __init__(self, cfg, itemToID):
        self.cfg = cfg
        self.stateCount = itemToID
        self.table = [{k: None for k in self.cfg.nonTerminals} for _ in range(self.stateCount)]
    
    def __getitem__(self, item):
        return self.table[item]
    
    def __str__(self):
        processedNonTerminals = sorted(list(self.cfg.nonTerminals))
        fmt = [len(str(_)) for _ in processedNonTerminals]
        for i in range(self.stateCount):
            for j, k in enumerate(processedNonTerminals):
                fmt[j] = max(fmt[j], len(str(self.table[i][k])))
        for i in range(len(fmt)):
            fmt[i] = "%%%ds" % fmt[i]
        result = []
        result.append('\t'.join([" "] + [fmt[i] % str(k) for i, k in enumerate(processedNonTerminals)]))
        for i in range(self.stateCount):
            result.append('\t'.join([str(i)] + [fmt[j] % str(self.table[i][k]) for j, k in enumerate(processedNonTerminals)]))
        return '\n'.join(result)
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self.stateCount
    
    def nonTerminals(self):
        return sorted(list(self.cfg.nonTerminals))

    def getHead(self):
        return ["state"] + [str(k) for k in sorted(list(self.cfg.nonTerminals))]
    
    def getRow(self, i):
        return [str(i)] + [str(self.table[i][k]) for k in sorted(list(self.cfg.nonTerminals))]
    
    def save(self, fileName):
        with open(fileName, "w") as f:
            f.write(str(self.stateCount) + "\n")
            f.write(str(self))
    
    @staticmethod
    def load(cfg, fileName):
        with open(fileName, "r") as f:
            stateCount, _, *rest = f.readlines()
            processedNonTerminals = sorted(list(cfg.nonTerminals))
            resultGoto = Goto(cfg, int(stateCount))
            for line in rest:
                stateNum, *gotos = line.split('\t')
                for i, goto in enumerate(gotos):
                    resultGoto[int(stateNum)][processedNonTerminals[i]] = eval(goto)
        return resultGoto