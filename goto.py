import json


class Goto:

    def __init__(self, cfg, stateCount, table=None):
        self.cfg = cfg
        self.stateCount = stateCount
        self.table = [{k: None for k in self.cfg.nonTerminals} for _ in range(self.stateCount)] if table is None else table
    
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
            json.dump({"stateCount": self.stateCount, "table": self.table}, f)

    @staticmethod
    def loadFromString(cfg, string):
        obj = json.loads(string)
        resultAction = Goto(cfg, obj["stateCount"], table=obj["table"])
        return resultAction
    
    @staticmethod
    def load(cfg, fileName):
        with open(fileName, "r") as f:
            resultGoto = Goto.loadFromString(cfg, f.read())
        return resultGoto