from typing import List, Dict, Optional, Any
import json

from io_utils.to_json import ToJson
from .cfg import ContextFreeGrammar


class Goto(ToJson):
    def __init__(
        self,
        cfg: ContextFreeGrammar,
        state_count: int,
        table: Optional[List[Dict[str, Any]]] = None,
    ):
        self.state_count = state_count
        self.non_terminals = cfg.non_terminals
        self.table: List[Dict[str, Optional[int]]] = (
            [{} for _ in range(self.state_count)]
            if table is None
            else table
        )

    def __getitem__(self, item: int):
        return self.table[item]

    def __str__(self):
        non_terminals = self.non_terminals
        fmt = [len(str(_)) for _ in non_terminals]
        for i in range(self.state_count):
            for j, k in enumerate(non_terminals):
                fmt[j] = max(fmt[j], len(str(self.table[i].get(k, None))))
        str_fmt = list(map(lambda v: "%%%ds" % v, fmt))
        result = []
        result.append(
            "\t".join(
                [" "] + [str_fmt[i] % str(k) for i, k in enumerate(non_terminals)]
            )
        )
        for i in range(self.state_count):
            result.append(
                "\t".join(
                    [str(i)]
                    + [
                        str_fmt[j] % str(self.table[i].get(k, None))
                        for j, k in enumerate(non_terminals)
                    ]
                )
            )
        return "\n".join(result)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.state_count

    def to_json(self):
        return {"state_count": self.state_count, "table": self.table}

    def save(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.to_json(), f)

    @staticmethod
    def loadFromString(cfg: ContextFreeGrammar, string):
        obj = json.loads(string)
        resultAction = Goto(cfg, obj["state_count"], table=obj["table"])
        return resultAction

    @staticmethod
    def load(cfg: ContextFreeGrammar, fileName):
        with open(fileName, "r") as f:
            resultGoto = Goto.loadFromString(cfg, f.read())
        return resultGoto
