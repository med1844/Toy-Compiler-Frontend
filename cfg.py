from typing import Self, Set, List, Tuple, Dict, Any
from typeDef import TypeDefinition


class ContextFreeGrammar:

    """
    production:
        nonTerminal -> sequence | sequence | ...
    
    The cfg parser will first split input to python tuples, 
    record both nonTerminals and all symbols, and give ID to each production.
    Then using terminals = allSymbols - nonTerminals, we can get terminals.
    """

    SUBSTITUTE = "_"
    EOF = -1

    @classmethod
    def load(cls, typedef: TypeDefinition, filename: str) -> Self:
        """
        Given type definition and fileName, create and return a CFG object.
        """
        assert isinstance(typedef, TypeDefinition)
        with open(filename, "r") as f:
            src = f.read()
        return cls.from_string(typedef, src)
    
    @classmethod
    def from_string(cls, typedef: TypeDefinition, string: str) -> Self:
        """
        Given type definition and CFG string, create and return a CFG object.
        """
        assert isinstance(typedef, TypeDefinition)
        non_terminals: Set[str] = set()
        all_symbol: Set[str] = set()
        grammar_to_id: Dict[Tuple[str, Tuple[str | int, ...]], int] = {}
        raw_grammar_to_id: Dict[str, int] = {}
        start_symbol = None

        temp: List[Tuple[str, List[str]]] = []

        for line in string.split('\n'):
            line = line.strip()
            if not line:
                continue
            non_terminal, seqs = line.split(" -> ")

            if start_symbol is None:
                start_symbol = non_terminal
            non_terminals.add(non_terminal)
            all_symbol.add(non_terminal)

            for seq in seqs.split(" | "):
                symbols = seq.split(" ")
                temp.append((non_terminal, symbols))
                raw_grammar_to_id["%s -> %s" % (non_terminal, seq)] = \
                    len(raw_grammar_to_id)
                for symbol in seq.split(" "):
                    all_symbol.add(symbol)
        assert start_symbol is not None

        for i, (non_terminal, symbols) in enumerate(temp):
            symbols = tuple("" if sym == "''"
                            else typedef.get_id_by_display_name(sym) if sym not in non_terminals
                            else sym
                            for sym in symbols)
            grammar_to_id[(non_terminal, symbols)] = i

        terminals = {typedef.get_id_by_display_name(_)
                     for _ in all_symbol - non_terminals if _ != "''"}

        return cls(typedef, terminals, non_terminals,
                                  start_symbol, grammar_to_id, raw_grammar_to_id)

    def __init__(self, typedef: TypeDefinition, terminals: Set[int], non_terminals: Set[str],
                 start_symbol: str, grammar_to_id: Dict[Tuple[str, Tuple[str | int, ...]], int], raw_grammar_to_id: Dict[str, int]):
        self.typedef = typedef
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.start_symbol = start_symbol
        self.grammar_to_id = grammar_to_id
        self.raw_grammar_to_id = raw_grammar_to_id
        self.id_to_grammar = {v: k for k, v in self.grammar_to_id.items()}
        self.non_terminal_to_prod_id: Dict[str, List[int]] = {}

        for k, v in grammar_to_id.items():
            self.non_terminal_to_prod_id.setdefault(k[0], list()).append(v)
        
    def __str__(self):
        return str(self.grammar_to_id)
    
    def get_symbol_in_prod(self, production_id: int, dot_pos: int, offset=0):
        """
        Given a production id, and the dot position, return the symbol at that 
        position.

        eg: 
            (E, (E, +, T)): 6
            calling get(6, 1) would return +.
        
        if dotPos + offset is out of bound, it would return None.
        """
        if dot_pos + offset >= len(self.id_to_grammar[production_id][1]):
            return None
        return self.id_to_grammar[production_id][1][dot_pos + offset]
    
    def get_production(self, prod_id: int):
        """
        Return the sequence of a given production.

        eg:
            (E, (E, +, T)): 6
            calling getProduction(6) would return (E, (E, +, T))
        """
        return self.id_to_grammar[prod_id]

    def is_non_terminal(self, op: Any):
        return op in self.non_terminals
    
    def is_terminal(self, op: Any):
        return op in self.terminals
    
    def get_productions(self, non_terminal: str) -> List[int]:
        """
        Return list of production ids that the nonTerminal can lead to.
        WARNING: DO NOT MODIFY THE RETURN VALUE.
        """
        return self.non_terminal_to_prod_id[non_terminal]
    
    def is_left_recursive(self):
        for non_terminal, ids in self.non_terminal_to_prod_id.items():
            for id_ in ids:
                if non_terminal == self.get_production(id_)[1][0]:
                    return True
        return False
    
    def __get_left_recursion_free_production(self, nonTerminal, ids):
        subNonTerminal = nonTerminal + self.SUBSTITUTE
        grammarList, subGrammarList = [], []
        for id_ in ids:
            grammar = self.get_production(id_)[1]
            if nonTerminal == grammar[0]:
                subGrammarList.append(grammar[1:] + (subNonTerminal, ))
            else:
                grammarList.append(grammar + (subNonTerminal, ))
        return (nonTerminal, tuple(grammarList)), (subNonTerminal, tuple(subGrammarList))
    
    def remove_left_recursion(self):
        """
        Return a new ContextFreeGrammar object, containing no left recursion.
        if:
            A -> A a1 | A a2 | A a3 | ... | b1 | b2 | b3 | ... 
        then change to:
            A -> b1 A_ | b2 A_ | b3 A_ | ...
            A_ -> a1 A_ | a2 A_ | a3 A_ | ...
        """
        result_grammar_to_id = {}
        result_non_terminals = set(self.non_terminals)
        for non_terminal, ids in self.non_terminal_to_prod_id.items():
            is_recursive = False
            for id_ in ids:
                if non_terminal == self.get_production(id_)[1][0]:  # left recursive
                    is_recursive = True
                    break
            if is_recursive:
                (new_non_terminal, new_production), (new_sub_non_terminal, new_sub_production) = \
                    self.__get_left_recursion_free_production(non_terminal, ids)
                result_non_terminals.add(new_sub_non_terminal)
                for prod in new_production:
                    result_grammar_to_id[(new_non_terminal, prod)] = len(result_grammar_to_id)
                for prod in new_sub_production:
                    result_grammar_to_id[(new_sub_non_terminal, prod)] = len(result_grammar_to_id)
            else:
                for id_ in ids:
                    result_grammar_to_id[self.get_production(id_)] = len(result_grammar_to_id)
        return ContextFreeGrammar(self.typedef, self.terminals, result_non_terminals,
                                  self.start_symbol, result_grammar_to_id, self.raw_grammar_to_id)
    
    def is_EOF(self, sym):
        return sym == -1
        

if __name__ == "__main__":
    typedef = TypeDefinition.from_filename("simpleJava/typedef")
    cfg = ContextFreeGrammar.load(typedef, "simpleJava/CFG")
    print(cfg.typedef)
    print(cfg.terminals)
    print(cfg.non_terminals)
    print(cfg.start_symbol)
    print(cfg.grammar_to_id)
    print(cfg.raw_grammar_to_id)
