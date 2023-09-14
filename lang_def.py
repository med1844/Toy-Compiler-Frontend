from typing import List, Tuple
from collections import deque


class LangDef:
    """
    A class that captures everything that's required by a compiler front-end, with no dependency.
    This allows things to be portable, i.e. copy json files or embed them, and copy this class.
    Use this class to load these json files, and you should be good to go.

    By splitting generation code with the actual parsing code, we manage to reduce the amount of code
    that must be copied / ported. We also increase runtime performance, as generating these tables
    could be time-consuming.

    Both TypeDef and ContextFreeGrammar class should have implemented the ToJson trait.
    When build from scratch, put typedef.to_json(), action.to_json(), and goto.to_json() here.
    """

    def __init__(self, dfa_list_json: List, action_json, goto_json):
        self.dfa_list_json = dfa_list_json
        self.action_json = action_json
        self.goto_json = goto_json

