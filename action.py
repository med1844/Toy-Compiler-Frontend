EMPTY = ""


class Action:

    def __init__(self, cfg, stateCount):
        self.cfg = cfg
        self.stateCount = stateCount
        self.table = [{k: None for k in self.cfg.terminals | {self.cfg.EOF}} for _ in range(self.stateCount)]

    def __getitem__(self, item):
        return self.table[item]
    
    def __str__(self):
        processedTerminals = sorted(list(self.cfg.terminals | {self.cfg.EOF}), key=str)
        fmt = [len(str(_)) for _ in processedTerminals]
        for i in range(self.stateCount):
            for j, k in enumerate(processedTerminals):
                fmt[j] = max(fmt[j], len(str(self.table[i][k])))
        for i in range(len(fmt)):
            fmt[i] = "%%%ds" % fmt[i]
        result = []
        result.append('\t'.join([" "] + [fmt[i] % str(k) for i, k in enumerate(processedTerminals)]))
        for i in range(self.stateCount):
            result.append('\t'.join([str(i)] + [fmt[j] % str(self.table[i][k]) for j, k in enumerate(processedTerminals)]))
        return '\n'.join(result)
    
    def __contains__(self, item):
        print(item in self.table)
        return item in self.table

    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self.stateCount
    
    def terminals(self):
        return sorted(list(self.cfg.terminals))

    def getHead(self):
        return ["state"] + [str(k) for k in sorted(list(self.cfg.terminals | {self.cfg.EOF}), key=str)]
    
    def getRow(self, i):
        return [str(i)] + [str(self.table[i][k]) for k in sorted(list(self.cfg.terminals | {self.cfg.EOF}), key=str)]

    def save(self, fileName):
        with open(fileName, "w") as f:
            f.write(str(self.stateCount) + "\n")
            f.write(str(self))
    
    @staticmethod
    def load(cfg, fileName):
        with open(fileName, "r") as f:
            stateCount, _, *rest = f.readlines()
            processedTerminals = sorted(list(cfg.terminals | {cfg.EOF}), key=str)
            resultAction = Action(cfg, int(stateCount))
            for line in rest:
                stateNum, *actions = line.split('\t')
                for i, action in enumerate(actions):
                    resultAction[int(stateNum)][processedTerminals[i]] = eval(action)
        return resultAction