from cfg_utils.cfg import ContextFreeGrammar
from lr1.action_goto_builder import ActionGotoBuilder
from lr1.lr1_itemset_automata import LRItemSetAutomata
from lang_def import LangDef


class LangDefBuilder:
    """A helper class that bridges `LangDef` and dependencies required to generate portable `LangDef` transition table.
    Also helps reduce boilerplate code."""

    @staticmethod
    def new(cfg: ContextFreeGrammar) -> LangDef:
        action, goto = ActionGotoBuilder.new(cfg, LRItemSetAutomata.new(cfg))
        return LangDef(
            cfg.typedef.get_dfa_set().to_json(),
            cfg.raw_grammar_to_id,
            cfg.prod_id_to_nargs_and_non_terminal,
            action.to_json(),
            goto.to_json(),
        )

