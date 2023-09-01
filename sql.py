from cfg import ContextFreeGrammar
from typeDef import TypeDefinition
from action import Action
from goto import Goto
from parseTree import ParseTreeActionRegister
import scanner
import parser


typedef = TypeDefinition.from_filename("simpleSQL/sqltypedef")
cfg = ContextFreeGrammar.load(typedef, "simpleSQL/SQL")
action, goto = parser.genActionGoto(typedef, cfg)

tokenList = scanner.parse_by_re(typedef, input())
pt = parser.parse(tokenList, typedef, cfg, action, goto)
print(pt)
