from cfg import ContextFreeGrammar, gen_action_todo
from lang_def import LangDef
from typeDef import TypeDefinition


class LangDefFactory:
    """a factory class that bridges `LangDef` and dependencies required to generate portable `LangDef` transition table."""

    @staticmethod
    def new(typedef: TypeDefinition, cfg: ContextFreeGrammar) -> LangDef:
        action, goto = gen_action_todo(cfg)
        return LangDef(
            list(map(lambda x: x.to_json(), typedef.get_dfa_list())),
            cfg.raw_grammar_to_id,
            cfg.prod_id_to_nargs_and_non_terminal,
            action.to_json(),
            goto.to_json(),
        )

