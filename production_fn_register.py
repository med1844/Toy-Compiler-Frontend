from typing import Callable, Dict, Tuple
from cfg import ContextFreeGrammar
from io_utils.to_json import ToJson
import inspect
import itertools


class ProductionFnRegister(ToJson):
    def __init__(self, cfg: ContextFreeGrammar):
        self.__production_to_action: Dict[int, Tuple[int, str, Callable]] = {}
        self.__cfg = cfg

    def production(self, *productions: str):
        """
        register a function to run at some position in the production

        @tree.production('E -> E "+" T')
        def foo(e, e1, plus, t):
            return "bar"
        """

        def decorate(function: Callable):
            for prod in productions:
                prod_id = self.__cfg.raw_grammar_to_id[prod]
                non_terminal, seq = self.__cfg.get_production(prod_id)
                self.__production_to_action[prod_id] = (
                    sum(map(lambda *_: 1, filter(lambda x: x != "''", seq))),
                    non_terminal,
                    function,
                )
            return function

        return decorate

    def get_production_mapping(self):
        return self.__production_to_action

    @staticmethod
    def preprocess_fn(fn: Callable) -> str:
        fn_src_lines = inspect.getsource(fn).split("\n")
        indent = min(
            sum(1 for _ in itertools.takewhile(str.isspace, line))
            for line in fn_src_lines
            if line
        )
        return "\n".join(
            filter(
                lambda x: not x.startswith("@"), map(lambda x: x[indent:], fn_src_lines)
            )
        )

    def to_json(self) -> Dict[int, Tuple[int, str, Tuple[str, str]]]:
        return {
            k: (
                nargs,
                non_terminal,
                (
                    fn.__name__,
                    self.preprocess_fn(fn),
                ),
            )
            for k, (nargs, non_terminal, fn) in self.__production_to_action.items()
        }

