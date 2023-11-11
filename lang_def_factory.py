from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition


class LangDefFactory:
    """a factory class that bridges `LangDef` and dependencies required to generate portable `LangDef` transition table."""

    @staticmethod
    def new(typedef: TypeDefinition, cfg: ContextFreeGrammar) -> LangDef:
        action, goto = gen_action_todo(cfg)
        return LangDef(
            typedef.get_dfa_set().to_json(),
            cfg.raw_grammar_to_id,
            cfg.prod_id_to_nargs_and_non_terminal,
            action.to_json(),
            goto.to_json(),
        )

