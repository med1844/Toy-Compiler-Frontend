from typing import List, Dict, Optional, Tuple
import json

from io_utils.to_json import ToJson
from cfg_utils.cfg import ContextFreeGrammar


class Action(ToJson):
    def __init__(self, cfg: ContextFreeGrammar, stateCount: int, table=None):
        self.state_count = stateCount
        self.terminals = cfg.terminals | {cfg.EOF}
        self.table: List[Dict[str, Optional[Tuple[int, int]]]] = (
            [{} for _ in range(self.state_count)] if table is None else table
        )

    def __getitem__(self, item):
        return self.table[item]

    def __str__(self):
        terminals = self.terminals
        fmt = [len(str(_)) for _ in terminals]
        for i in range(self.state_count):
            for j, k in enumerate(terminals):
                fmt[j] = max(fmt[j], len(str(self.table[i].get(str(k), None))))
        str_fmt = list(map(lambda v: "%%%ds" % v, fmt))
        result = []
        result.append(
            "\t".join([" "] + [str_fmt[i] % str(k) for i, k in enumerate(terminals)])
        )
        for i in range(self.state_count):
            result.append(
                "\t".join(
                    [str(i)]
                    + [
                        str_fmt[j] % str(self.table[i].get(str(k), None))
                        for j, k in enumerate(terminals)
                    ]
                )
            )
        return "\n".join(result)

    def __contains__(self, item):
        return item in self.table

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.state_count

    def to_json(self):
        return {"state_count": self.state_count, "table": self.table}

    def save(self, fileName):
        with open(fileName, "w") as f:
            json.dump({"state_count": self.state_count, "table": self.table}, f)

    @staticmethod
    def loadFromString(cfg: ContextFreeGrammar, string):
        obj = json.loads(string)
        resultAction = Action(cfg, obj["stateCount"], table=obj["table"])
        return resultAction

    @staticmethod
    def load(cfg, fileName):
        with open(fileName, "r") as f:
            resultAction = Action.loadFromString(cfg, f.read())
        return resultAction
