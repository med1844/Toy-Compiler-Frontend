from collections import deque
from cfg import ContextFreeGrammar
from typeDef import TypeDefinition
from action import Action
from goto import Goto
from Ast import ASTNode, AbstractSyntaxTree, ASTActionRegister
from parseTree import ParseTreeActionRegister
import scanner
import Parser
import sys


typedef = TypeDefinition.load("simpleJava/typedef")
cfg = ContextFreeGrammar.load(typedef, "simpleJava/simpleJavaCFG")
# action, goto = Parser.genActionGoto(typedef, cfg)
# action.save('simpleJava/simpleJavaAction')
# goto.save('simpleJava/simpleJavaGoto')
# exit()
action = Action.load(cfg, "simpleJava/simpleJavaAction")
goto = Goto.load(cfg, "simpleJava/simpleJavaGoto")
par = ParseTreeActionRegister(cfg)


cb_count = -2
def getNewCodeBlockName():
    global cb_count
    cb_count += 1
    if cb_count == -1:
        return "_main"
    return "__CB_%d" % (cb_count)


@par.production("StatementList -> StatementList Statement")
def _stmtl0(stmtl, stmtl0, stmt):
    stmtl.node = stmtl0.node
    stmtl.node.addChild(stmt.node)

@par.production("StatementList -> Statement")
def _stmtl1(stmtl, stmt):
    stmtl.node = ASTNode("stmtList", stmt.node)

@par.production(
    "Statement -> Declaration",
    "Statement -> Expr",
    "Statement -> WhileBlock",
    "Statement -> IfBlock",
    "Statement -> ForBlock",
    "Statement -> ReturnStatement", 
    "Statement -> FlowControl"
)
def _stmt2(stmt, other):
    stmt.node = other.node

@par.production("Expr -> f0 ;")
def _expr0(expr, f0, semi):
    expr.node = f0.node

@par.production(
    "c0 -> c1", "c1 -> c2", "c2 -> c3", "c3 -> c4", "c4 -> e0",
    "e0 -> e1", "e1 -> e2", "e2 -> e3", "e3 -> e4", "f0 -> f1", 
    "f1 -> f2", "f2 -> c0"
)
def _cxx(ca, cb):
    ca.node = cb.node

@par.production("c0 -> c0 and c1")
def _c00(c0, c00, and_, c1):
    c0.node = ASTNode("and", c00.node, c1.node)

@par.production("c1 -> c1 or c2")
def _c10(c1, c10, or_, c2):
    c1.node = ASTNode("or", c10.node, c2.node)

@par.production("c2 -> not c3")
def _c20(c2, not_, c3):
    c2.node = ASTNode("not", c3.node)

@par.production("c3 -> c3 == c4")
def _c30(c3, c30, eq, c4):
    c3.node = ASTNode("eq", c30.node, c4.node)

@par.production("c3 -> c3 < c4")
def _c31(c3, c30, eq, c4):
    c3.node = ASTNode("lt", c30.node, c4.node)

@par.production("c3 -> c3 > c4")
def _c32(c3, c30, eq, c4):
    c3.node = ASTNode("gt", c30.node, c4.node)

@par.production("c3 -> c3 <= c4")
def _c33(c3, c30, eq, c4):
    c3.node = ASTNode("le", c30.node, c4.node)

@par.production("c3 -> c3 >= c4")
def _c34(c3, c30, eq, c4):
    c3.node = ASTNode("ge", c30.node, c4.node)

@par.production("c3 -> c3 != c4")
def _c35(c3, c30, eq, c4):
    c3.node = ASTNode("ne", c30.node, c4.node)

@par.production("e0 -> ++ e1")
def _e00(e0, sp, e1):
    e0.node = ASTNode("sp", e1.node)  # self plus

@par.production("e0 -> -- e1")
def _e01(e0, sm, e1):
    e0.node = ASTNode("sm", e1.node)  # self minus

@par.production("e1 -> e1 + e2")
def _e10(e1, e10, plus, e2):
    e1.node = ASTNode("add", e10.node, e2.node)

@par.production("e1 -> e1 - e2")
def _e11(e1, e10, minus, e2):
    e1.node = ASTNode("sub", e10.node, e2.node)

@par.production("e3 -> e4 += e3")
def _e30(e1, e2, iplus, e10):
    e1.node = ASTNode("iadd", e2.node, e10.node)

@par.production("e3 -> e4 -= e3")
def _e31(e1, e2, iminus, e10):
    e1.node = ASTNode("isub", e2.node, e10.node)

@par.production("e2 -> e2 * e3")
def _e20(e2, e20, mul, e3):
    e2.node = ASTNode("mul", e20.node, e3.node)

@par.production("e2 -> e2 / e3")
def _e21(e2, e20, mul, e3):
    e2.node = ASTNode("div", e20.node, e3.node)

@par.production("e3 -> e4 *= e3")
def _e32(e2, e3, mul, e20):
    e2.node = ASTNode("imul", e3.node, e20.node)

@par.production("e3 -> e4 /= e3")
def _e33(e2, e3, mul, e20):
    e2.node = ASTNode("idiv", e3.node, e20.node)

@par.production("e2 -> e2 % e3")
def _e22(e2, e20, mod, e3):
    e2.node = ASTNode("mod", e20.node, e3.node)

@par.production("e3 -> e4 %= e3")
def _e34(e2, e3, mul, e20):
    e2.node = ASTNode("imod", e3.node, e20.node)

@par.production("f0 -> f1 = f0", "f0 -> f1 = Allocation")
def _f00(f0, f00, assg, f1):
    f0.node = ASTNode("assign", f00.node, f1.node)

@par.production("f1 -> f1 . f2")
def _f10(f1, f10, dot, f2):
    f1.node = ASTNode("getattr", f10.node, f2.node)

@par.production("f1 -> f1 [ f2 ]")
def _f11(f1, f10, lob, f2, rob):
    f1.node = ASTNode("getitem", f10.node, f2.node)

@par.production("e4 -> ( f0 )")
def _f20(e3, lp, f0, rp):
    e3.node = f0.node

@par.production("e4 -> Value")
def _f21(e3, value):
    e3.node = value.node

@par.production("Declaration -> VarDeclaration ;")
def _decl0(declaration, varDeclaration, semi):
    declaration.node = varDeclaration.node

@par.production("Declaration -> FunctionDeclaration")
def _decl1(declaration, functionDeclaration):
    declaration.node = functionDeclaration.node

@par.production("VarDeclaration -> Type IdList")
def _vardecl0(vardec, type_, idList):
    vardec.node = ASTNode("varDec", type_.node, idList.node)

@par.production("IdList -> IdList , Id")
def _idl0(idl, idl0, comma, id_):
    idl.node = idl0.node
    idl.node.addChild(id_.node)

@par.production("IdList -> Id")
def _idl1(idl, id_):
    idl.node = ASTNode("idList", id_.node)

@par.production("Id -> id")
def _id0(id_, id_0):
    id_.node = ASTNode(id_0.getContent(), actionID="id_var")

@par.production("Id -> id = c0", "Id -> id = Allocation")
def _id1(id_, id_0, assg, c0):
    id_.node = ASTNode("assign", ASTNode(id_0.getContent(), actionID="id_var"), c0.node)

@par.production("FunctionDeclaration -> Type id ( DefParamList ) { StatementList }")
def _funcdec0(funcDec, type_, id_, lp, defParamList, rp, lcb, stmtl, rcb):
    funcDec.node = ASTNode(
        "funcDec",
        type_.node,
        ASTNode(id_.getContent(), actionID="id_func"),
        defParamList.node,
        stmtl.node
    )

@par.production("DefParamList -> DefParamList , DefParam")
def _defpl0(defpl, defpl0, comma, defp):
    defpl.node = defpl0.node
    defpl.node.addChild(defp.node)

@par.production("DefParamList -> DefParam")
def _defpl1(defpl, defp):
    defpl.node = ASTNode("defParamList", defp.node)

@par.production("DefParam -> Type id")
def _defp0(defp, type_, id_):
    defp.node = ASTNode("defParam", type_.node, ASTNode(id_.getContent(), actionID="id_func_var"))

@par.production("Allocation -> new FunctionCall")
def _alloc0(alloc, new, func):
    alloc.node = ASTNode("newObj", func.node)

@par.production("Allocation -> new BasicType AllocArrays")
def _alloc1(alloc, new, basicType, arr):
    alloc.node = ASTNode("newArr", basicType.node, arr.node)

@par.production("AllocArrays -> AllocArrays [ c0 ]")
def _alarr0(alarr, alarr0, lo, c0, ro):
    alarr.node = alarr0.node
    alarr.node.addChild(c0.node)

@par.production("AllocArrays -> [ c0 ]")
def _alarr1(alarr, lo, c0, ro):
    alarr.node = ASTNode("dimensions", c0.node)

@par.production("WhileBlock -> while ( c0 ) { StatementList }")
def _whileBlock0(wb, while_, lp, c0, rp, lcb, sl, rcb):
    wb.node = ASTNode("whileBlock", c0.node, sl.node)

@par.production("IfBlock -> if ( c0 ) { StatementList }")
def _ifBlock0(ib, if_, lp, c0, rp, lcb, sl, rcb):
    if "node" not in ib:
        ib.node = ASTNode("ifBlock", c0.node, sl.node)
    else:
        ib.node.addChild(c0.node)
        ib.node.addChild(sl.node)

@par.production("IfBlock -> if ( c0 ) { StatementList } else { StatementList }")
def _ifBlock1(ib, if_, lp, c0, rp, lcb, sl, rcb, else_, lcb0, sl0, rcb0):
    if "node" not in ib:
        ib.node = ASTNode("ifBlock", c0.node, sl.node, sl0.node)
    else:
        ib.node.addChild(c0.node)
        ib.node.addChild(sl.node)
        ib.node.addChild(sl0.node)

@par.production("IfBlock -> if ( c0 ) { StatementList } else IfBlock", index=8)
def _ifBlock1(ib, if_, lp, c0, rp, lcb, sl, rcb, else_, ib0):
    if "node" not in ib:
        ib.node = ASTNode("ifBlock", c0.node, sl.node)
    else:
        ib.node.addChild(c0.node)
        ib.node.addChild(sl.node)
    ib0.node = ib.node

@par.production("ForInit -> VarDeclaration", "ForInit -> c0", "ForExpr -> c0")
def _forinit0(forinit, b):
    forinit.node = b.node

@par.production("ForInit -> ''", "ForExpr -> ''")
def _empty(a):
    a.node = ASTNode("none")

@par.production("ForBlock -> for ( ForInit ; ForExpr ; ForExpr ) { StatementList }")
def _forblock0(forBlock, for_, lp, forinit, semi0, forexpr0, semi1, forexpr1, rp, lcb, stmtl, rcb):
    forBlock.node = ASTNode(
        "forBlock",
        forinit.node,
        forexpr0.node,
        stmtl.node,
        forexpr1.node
    )

@par.production("ReturnStatement -> return c0 ;")
def _rs0(rs, ret, c0, semi):
    rs.node = ASTNode("return", c0.node)

@par.production("Type -> BasicType")
def _type0(type_, basicType):
    type_.node = basicType.node
    type_.node.isArray = False
    type_.node.dim = 0

@par.production("Type -> BasicType Arrays")
def _type1(type_, basicType, arrays):
    type_.node = basicType.node
    type_.node.isArray = True
    type_.node.dim = arrays.dim  # dimension number

@par.production("Arrays -> Arrays #")
def _arr0(arr, arr0, sharp):
    arr.dim = arr0.dim + 1

@par.production("Arrays -> #")
def _arr1(arr, sharp):
    arr.dim = 1

@par.production(
    "BasicType -> int",
    "BasicType -> float",
    "BasicType -> double",
    "BasicType -> long", 
    "BasicType -> char", 
    "BasicType -> bool", 
    "BasicType -> void", 
    "BasicType -> short", 
    "BasicType -> id"
)
def _basicType0(bt, typ):
    bt.node = ASTNode(typ.getContent(), actionID="type")

@par.production("Value -> FunctionCall")
def _val0(value, functionCall):
    value.node = functionCall.node

@par.production("FunctionCall -> id ( ParamList )")
def _func0(func, id_, lp, pal, rp):
    func.node = ASTNode("functionCall", ASTNode(id_.getContent(), actionID="noAction"), pal.node)

@par.production("ParamList -> ParamList , Param")
def _pal0(paraml, paraml0, comma, param):
    paraml.node = paraml0.node
    paraml.node.addChild(param.node)

@par.production("ParamList -> Param")
def _pal1(paraml, param):
    paraml.node = ASTNode("parameterList", param.node)

@par.production("ParamList -> ''")
def _pal2(paraml):
    paraml.node = ASTNode("parameterList")

@par.production("Param -> c0")
def _par0(par, c0):
    par.node = c0.node

@par.production("Value -> Constant")
def _val1(value, constant):
    value.node = ASTNode(constant.val, actionID="const")
    value.node.type = constant.type

@par.production("Value -> id")
def _val2(value, id_):
    value.node = ASTNode(id_.getContent(), actionID="id_var")

@par.production("Constant -> int_const")
def _const0(const, int_const):
    const.val = int_const.getContent()
    const.type = "int"

@par.production("Constant -> str_literal")
def _const1(const, str_literal):
    const.val = str_literal.getContent()
    const.type = "String"

@par.production("Constant -> char_literal")
def _const3(const, char):
    const.val = char.getContent()
    const.type = "char"

@par.production("Constant -> true", "Constant -> false")
def _const2(const, boolean):
    const.val = boolean.getContent()
    const.type = "bool"

@par.production("Constant -> null")
def _const3(const, null):
    const.val = null.getContent()
    const.type = "null"

@par.production("FlowControl -> continue ;")
def _continue0(flc, cont, semi):
    flc.node = ASTNode("continue")

@par.production("FlowControl -> break ;")
def _continue1(flc, brk, semi):
    flc.node = ASTNode("break")

with open("simpleJava/simple.sjava", "r") as f:
    src = f.read()
tokenList = scanner.parse(typedef, src, ['line_comment', 'block_comment', 'space'])
pt = Parser.parse(tokenList, typedef, cfg, action, goto)
pt.evaluate(par)
ast = AbstractSyntaxTree(pt.getRoot().node)


class CodeBlock:

    def __init__(self, name):
        self.name = name
        self.list = []
        self.next = None
        self.segment = []
    
    def addILOC(self, op, *l):
        self.list.append((op, *l))
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name
    
    def __ne__(self, other):
        if isinstance(other, str):
            return self.name != other
        return self.name != other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __iter__(self):
        return iter(self.list)
    
    def calcSegment(self):
        self.segment.clear()
        segCount = 0
        for op, *_ in self.list:
            self.segment.append(segCount)
            if op == "seg":
                segCount += 1
    
    def getSegments(self):
        self.calcSegment()
        newCBs = [self] + [CodeBlock(self.name + "_SEG_%d" % i) for i in range(1, self.segment[-1] + 1)]
        for i in range(len(self.list)):
            if self.list[i][0] != "seg":
                if self.segment[i]:
                    newCBs[self.segment[i]].addILOC(*self.list[i])
        i = len(self.list) - 1
        while self.segment[i]:
            self.list.pop()
            i -= 1
        for i in range(len(newCBs) - 1):
            l, r = newCBs[i], newCBs[i + 1]
            l.next = r
        return newCBs
    
    def updateCur(self):
        for i, (_, *rest) in enumerate(self.list):
            self.list[i] = list(self.list[i])
            for j in range(len(rest)):
                if isinstance(rest[j], tuple):
                    if isinstance(rest[j][0], str) and rest[j][0] == "cur":
                        self.list[i][j + 1] = (self, rest[j][1])

    def updateNone(self):
        for i, (_, *rest) in enumerate(self.list):
            self.list[i] = list(self.list[i])
            for j in range(len(rest)):
                if rest[j] is None:
                    self.list[i][j + 1] = EXIT_BLOCK
    
    def updateNext(self):
        # update operands containing next of other CB
        if isinstance(self.next, tuple):
            self.next = self.next[0].next
        for i, (_, *rest) in enumerate(self.list):
            self.list[i] = list(self.list[i])
            for j in range(len(rest)):
                if isinstance(rest[j], tuple):
                    self.list[i][j + 1] = self.list[i][j + 1][0].next

EXIT_BLOCK = CodeBlock("_exit")
EXIT_BLOCK.addILOC("mov", "eax", "0")
EXIT_BLOCK.addILOC("ret")

    
BSS = []  # section .bss
def addBSS(name, storageSpace, number):
    """
    Declare `number` `storageSpace` for `name`.
    """
    BSS.append("    %s: %s %s" % (name, storageSpace, number))


DATA = []  # section .data
def addDATA(name, storageSpace, value):
    DATA.append("    %s: %s %s" % (name, storageSpace, value))


EXTERN = set()
def addEXTERN(name):
    EXTERN.add(name)


temp_id = -1
def getTempVarName():
    global temp_id
    temp_id += 1
    return "__t_%d" % temp_id

def getType(l, r):
    return "int"


declaredVars = {}


class Object:

    TYPE_TO_SIZE = {
        "String": 1,
        "short": 2,
        "int": 4,
    }

    SIZE_TO_DATA = {
        1: "db",
        2: "dw",
        4: "dd"
    }

    SIZE_TO_BSS = {
        1: "resb",
        2: "resw",
        4: "resd",
    }

    SIZE_TO_OP = {
        1: "byte",
        2: "word",
        4: "dword",
    }

    def __init__(self, name, size, type_, isPointer, namespace):
        self.name = name
        self.size = size
        self.type = type_
        self.isPointer = isPointer
        self.namespace = namespace
        if namespace not in declaredVars:
            declaredVars[namespace] = {}
        declaredVars[namespace][name] = self
    
    def __repr__(self):
        return repr(self.name)
    
    def getOP(self):
        pass


class ConstValue(Object):

    def __init__(self, name, type_, value, namespace):
        super().__init__(name, self.TYPE_TO_SIZE[type_], type_, False, namespace)
        self.value = value
        addDATA(self.name, self.SIZE_TO_DATA[self.size], str(self.value))
    
    def getOP(self):
        return "%s [%s]" % (self.SIZE_TO_OP[self.size], self.name)


class ConstPointer(Object):

    def __init__(self, name, type_, value, namespace):
        super().__init__(name, 4, type_, False, namespace)
        self.value = value
        addDATA(self.name, self.SIZE_TO_DATA[self.size], str(self.value))
    
    def getOP(self):
        return "%s" % self.name


class Variable(Object):
    """
    Including all non-ptr variables.
    int a; -> a is a Value
    """

    def __init__(self, name, type_, namespace):
        super().__init__(name, self.TYPE_TO_SIZE[type_], type_, False, namespace)
        addBSS(self.name, self.SIZE_TO_BSS[self.size], 1)
    
    def getOP(self):
        return "%s [%s]" % (self.SIZE_TO_OP[self.size], self.name)
    

class Reference(Object):

    def __init__(self, name, type_, namespace):
        super().__init__(name, 4, type_, True, namespace)  # 32 bit address is 4
        addBSS(self.name, self.SIZE_TO_BSS[self.size], 1)
    
    def getOP(self):
        return "%s" % self.name
    

class ValueArray(Variable):

    def __init__(self, name, type_, length, namespace):
        super().__init__(name, type_, namespace)
        self.length = length


class RefArray(Reference):
    
    def __init__(self, name, type_, length, namespace):
        super().__init__(name, type_, namespace)
        self.length = length


firstAAR = ASTActionRegister()
@firstAAR.action("stmtList", index=0)
def _stmtl(stmtl, *rest):
    stmtl.cb = CodeBlock(getNewCodeBlockName())
ast.evaluate(firstAAR)

def updateCB(cur, childs):
    for child in childs:
        if "cb" not in child:
            child.cb = cur.cb
        child.run(updateCB)
ast.run(updateCB)

def forceUpdateCB(cur, childs):
    for child in childs:
        child.cb = cur.cb
        child.run(forceUpdateCB)


depth = -1
count = {}  # depth: count
def initNS(cur, childs):
    global depth
    if cur.getContent() == "stmtList":
        depth += 1
        if depth not in count:
            count[depth] = -1
        count[depth] += 1
        cur.ns = (depth, count[depth])
        for child in childs:
            child.run(initNS)
        depth -= 1
    else:
        cur.ns = (depth, count[depth])
        for child in childs:
            child.run(initNS)
    declaredVars[cur.ns] = {}
ast.run(initNS)

nsInheritance = {}  # record the inheritance relationship between namespaces, for ID look up
def getNsInheritance(cur, childs):
    for child in childs:
        if child.ns not in nsInheritance:
            nsInheritance[child.ns] = cur.ns
        child.run(getNsInheritance)
ast.run(getNsInheritance)

def updateNS(cur, childs):
    for child in childs:
        child.ns = cur.ns
        child.run(updateNS)


aar = ASTActionRegister()

@aar.action("varDec", index=0)
def _varDec(varDec, type_, idList):
    for node in idList.getChilds():
        node.dec = True
        node.type = type_.getContent()
        node.isArray = type_.isArray
        node.dim = type_.dim

@aar.action("id_var")
def _id_var(id_):
    varName = "__v_%d_%d_%s" % (id_.ns[0], id_.ns[1], id_.getContent())
    if "dec" in id_:
        if id_.type[0].islower():
            id_.var = Variable(varName, id_.type, id_.ns)
    else:
        ns = id_.ns
        while True:
            tempVarName = "__v_%d_%d_%s" % (ns[0], ns[1], id_.getContent())
            if tempVarName in declaredVars[ns]:
                id_.var = declaredVars[ns][tempVarName]
                break
            if ns not in nsInheritance:
                print("[ERROR] Undefined variable: %s has not been declared yet." % varName)
                exit()
            ns = nsInheritance[ns]

@aar.action("assign", index=0)
def _assign_begin(assg, l, r):
    if "dec" in assg:
        l.dec = True
        l.type = assg.type
        l.isArray = assg.isArray
        l.dim = assg.dim

@aar.action("assign")
def _assign(assg, l, r):
    assg.cb.addILOC("mov", "ebx", r.var.getOP())
    assg.cb.addILOC("mov", l.var.getOP(), "ebx")
    assg.var = l.var

@aar.action("const")
def _const(const):
    val = str(const.getContent())
    if const.type[0].islower():
        const.var = ConstValue(getTempVarName(), const.type, val, const.ns)
    else:
        if const.type == "String":
            val += ", 0"
        const.var = ConstPointer(getTempVarName(), const.type, val, const.ns)

@aar.action("add")
def _add(add, l, r):
    add.cb.addILOC("push", "eax")
    add.cb.addILOC("mov", "eax", r.var.getOP())
    add.cb.addILOC("add", "eax", l.var.getOP())
    add.var = Variable(getTempVarName(), getType(l, r), add.ns)
    add.cb.addILOC("mov", add.var.getOP(), "eax")
    add.cb.addILOC("pop", "eax")

@aar.action("sub")
def _sub(sub, l, r):
    sub.cb.addILOC("push", "eax")
    sub.cb.addILOC("mov", "eax", l.var.getOP())
    sub.cb.addILOC("sub", "eax", r.var.getOP())
    sub.var = Variable(getTempVarName(), getType(l, r), sub.ns)
    sub.cb.addILOC("mov", sub.var.getOP(), "eax")
    sub.cb.addILOC("pop", "eax")

@aar.action("mul")
def _mul(mul, l, r):
    mul.cb.addILOC("push", "eax")
    mul.cb.addILOC("mov", "eax", l.var.getOP())
    mul.cb.addILOC("mul", r.var.getOP())
    mul.var = Variable(getTempVarName(), getType(l, r), mul.ns)
    mul.cb.addILOC("mov", mul.var.getOP(), "eax")
    mul.cb.addILOC("pop", "eax")

@aar.action("div")
def _div(div, l, r):
    div.cb.addILOC("push", "eax")
    div.cb.addILOC("push", "ebx")
    div.cb.addILOC("push", "edx")
    div.cb.addILOC("xor", "edx", "edx")
    div.cb.addILOC("mov", "eax", l.var.getOP())
    div.cb.addILOC("mov", "ebx", r.var.getOP())
    div.cb.addILOC("div", "ebx")
    div.var = Variable(getTempVarName(), getType(l, r), div.ns)
    div.cb.addILOC("mov", div.var.getOP(), "eax")
    div.cb.addILOC("pop", "edx")
    div.cb.addILOC("pop", "ebx")
    div.cb.addILOC("pop", "eax")

@aar.action("mod")
def _mod(mod, l, r):
    mod.cb.addILOC("push", "eax")
    mod.cb.addILOC("push", "ebx")
    mod.cb.addILOC("push", "edx")
    mod.cb.addILOC("xor", "edx", "edx")
    mod.cb.addILOC("mov", "eax", l.var.getOP())
    mod.cb.addILOC("mov", "ebx", r.var.getOP())
    mod.cb.addILOC("div", "ebx")
    mod.var = Variable(getTempVarName(), getType(l, r), mod.ns)
    mod.cb.addILOC("mov", mod.var.getOP(), "edx")
    mod.cb.addILOC("pop", "edx")
    mod.cb.addILOC("pop", "ebx")
    mod.cb.addILOC("pop", "eax")

@aar.action("sp")
def _sp(sp, l):
    sp.cb.addILOC("inc", l.var.getOP())
    sp.var = l.var

@aar.action("sm")
def _sm(sm, l):
    sm.cb.addILOC("dec", l.var.getOP())
    sm.var = l.var

@aar.action("iadd")
def _iadd(iadd, l, r):
    iadd.cb.addILOC("push", "eax")
    iadd.cb.addILOC("mov", "eax", l.var.getOP())
    iadd.cb.addILOC("add", "eax", r.var.getOP())
    iadd.cb.addILOC("mov", l.var.getOP(), "eax")
    iadd.cb.addILOC("pop", "eax")
    iadd.var = l.var

@aar.action("isub")
def _isub(isub, l, r):
    isub.cb.addILOC("push", "eax")
    isub.cb.addILOC("mov", "eax", l.var.getOP())
    isub.cb.addILOC("sub", "eax", r.var.getOP())
    isub.cb.addILOC("mov", l.var.getOP(), "eax")
    isub.cb.addILOC("pop", "eax")
    isub.var = l.var

@aar.action("imul")
def _imul(imul, l, r):
    imul.cb.addILOC("push", "eax")
    imul.cb.addILOC("mov", "eax", l.var.getOP())
    imul.cb.addILOC("mul", r.var.getOP())
    imul.cb.addILOC("mov", l.var.getOP(), "eax")
    imul.cb.addILOC("pop", "eax")
    imul.var = l.var

@aar.action("idiv")
def _idiv(idiv, l, r):
    idiv.cb.addILOC("push", "eax")
    idiv.cb.addILOC("push", "ebx")
    idiv.cb.addILOC("push", "edx")
    idiv.cb.addILOC("xor", "edx", "edx")
    idiv.cb.addILOC("mov", "eax", l.var.getOP())
    idiv.cb.addILOC("mov", "ebx", r.var.getOP())
    idiv.cb.addILOC("div", "ebx")
    idiv.cb.addILOC("mov", l.var.getOP(), "eax")
    idiv.cb.addILOC("pop", "edx")
    idiv.cb.addILOC("pop", "ebx")
    idiv.cb.addILOC("pop", "eax")
    idiv.var = l.var

@aar.action("imod")
def _imod(imod, l, r):
    imod.cb.addILOC("push", "eax")
    imod.cb.addILOC("push", "ebx")
    imod.cb.addILOC("push", "edx")
    imod.cb.addILOC("xor", "edx", "edx")
    imod.cb.addILOC("mov", "eax", l.var.getOP())
    imod.cb.addILOC("mov", "ebx", r.var.getOP())
    imod.cb.addILOC("div", "ebx")
    imod.cb.addILOC("mov", l.var.getOP(), "edx")
    imod.cb.addILOC("pop", "edx")
    imod.cb.addILOC("pop", "ebx")
    imod.cb.addILOC("pop", "eax")
    imod.var = l.var

@aar.action("eq")
def _eq(eq, l, r):
    eq.cb.addILOC("push", "eax")
    eq.cb.addILOC("xor", "eax", "eax")
    eq.cb.addILOC("push", "ebx")
    eq.cb.addILOC("mov", "ebx", l.var.getOP())
    eq.cb.addILOC("cmp", "ebx", r.var.getOP())
    eq.cb.addILOC("lahf")
    eq.cb.addILOC("shr", "eax", "14")
    eq.cb.addILOC("and", "eax", "1")
    eq.var = Variable(getTempVarName(), "int", eq.ns)
    eq.cb.addILOC("mov", eq.var.getOP(), "eax")
    eq.cb.addILOC("pop", "ebx")
    eq.cb.addILOC("pop", "eax")

@aar.action("ne")
def _ne(ne, l, r):
    ne.cb.addILOC("push", "eax")
    ne.cb.addILOC("xor", "eax", "eax")
    ne.cb.addILOC("push", "ebx")
    ne.cb.addILOC("mov", "ebx", l.var.getOP())
    ne.cb.addILOC("cmp", "ebx", r.var.getOP())
    ne.cb.addILOC("lahf")
    ne.cb.addILOC("shr", "eax", "14")
    ne.cb.addILOC("and", "eax", "1")
    ne.cb.addILOC("xor", "eax", "1")
    ne.var = Variable(getTempVarName(), "int", ne.ns)
    ne.cb.addILOC("mov", ne.var.getOP(), "eax")
    ne.cb.addILOC("pop", "ebx")
    ne.cb.addILOC("pop", "eax")

@aar.action("lt")
def _lt(lt, l, r):
    # l < r -> l - r < 0 -> sign = 1
    lt.cb.addILOC("push", "eax")
    lt.cb.addILOC("xor", "eax", "eax")
    lt.cb.addILOC("push", "ebx")
    lt.cb.addILOC("mov", "ebx", l.var.getOP())
    lt.cb.addILOC("cmp", "ebx", r.var.getOP())
    lt.cb.addILOC("lahf")
    lt.cb.addILOC("shr", "eax", "15")
    lt.cb.addILOC("and", "eax", "1")
    lt.var = Variable(getTempVarName(), "int", lt.ns)
    lt.cb.addILOC("mov", lt.var.getOP(), "eax")
    lt.cb.addILOC("pop", "ebx")
    lt.cb.addILOC("pop", "eax")

@aar.action("gt")
def _gt(gt, l, r):
    # l > r -> r - l < 0 -> sign = 1
    gt.cb.addILOC("push", "eax")
    gt.cb.addILOC("xor", "eax", "eax")
    gt.cb.addILOC("push", "ebx")
    gt.cb.addILOC("mov", "ebx", r.var.getOP())
    gt.cb.addILOC("cmp", "ebx", l.var.getOP())
    gt.cb.addILOC("lahf")
    gt.cb.addILOC("shr", "eax", "15")
    gt.cb.addILOC("and", "eax", "1")
    gt.var = Variable(getTempVarName(), "int", gt.ns)
    gt.cb.addILOC("mov", gt.var.getOP(), "eax")
    gt.cb.addILOC("pop", "ebx")
    gt.cb.addILOC("pop", "eax")

@aar.action("le")
def _le(le, l, r):
    # l <= r -> not l > r
    le.cb.addILOC("push", "eax")
    le.cb.addILOC("xor", "eax", "eax")
    le.cb.addILOC("push", "ebx")
    le.cb.addILOC("mov", "ebx", r.var.getOP())
    le.cb.addILOC("cmp", "ebx", l.var.getOP())
    le.cb.addILOC("lahf")
    le.cb.addILOC("shr", "eax", "15")
    le.cb.addILOC("and", "eax", "1")
    le.cb.addILOC("xor", "eax", "1")  # boolean not
    le.var = Variable(getTempVarName(), "int", le.ns)
    le.cb.addILOC("mov", le.var.getOP(), "eax")
    le.cb.addILOC("pop", "ebx")
    le.cb.addILOC("pop", "eax")

@aar.action("ge")
def _ge(ge, l, r):
    # l >= r -> not l < r
    ge.cb.addILOC("push", "eax")
    ge.cb.addILOC("xor", "eax", "eax")
    ge.cb.addILOC("push", "ebx")
    ge.cb.addILOC("mov", "ebx", l.var.getOP())
    ge.cb.addILOC("cmp", "ebx", r.var.getOP())
    ge.cb.addILOC("lahf")
    ge.cb.addILOC("shr", "eax", "15")
    ge.cb.addILOC("and", "eax", "1")
    ge.cb.addILOC("xor", "eax", "1")  # boolean not
    ge.var = Variable(getTempVarName(), "int", ge.ns)
    ge.cb.addILOC("mov", ge.var.getOP(), "eax")
    ge.cb.addILOC("pop", "ebx")
    ge.cb.addILOC("pop", "eax")

@aar.action("not")
def _not(not_, l):
    not_.cb.addILOC("push", "ebx")
    not_.cb.addILOC("mov", "ebx", l.var.getOP())
    not_.cb.addILOC("xor", "ebx", "1")
    not_.var = Variable(getTempVarName(), "int", not_.ns)
    not_.cb.addILOC("mov", not_.var.getOP(), "ebx")
    not_.cb.addILOC("pop", "ebx")

@aar.action("or")
def _or(or_, l, r):
    or_.cb.addILOC("push", "ebx")
    or_.cb.addILOC("mov", "ebx", l.var.getOP())
    or_.cb.addILOC("or", "ebx", r.var.getOP())
    or_.var = Variable(getTempVarName(), "int", or_.ns)
    or_.cb.addILOC("mov", or_.var.getOP(), "ebx")
    or_.cb.addILOC("pop", "ebx")

@aar.action("and")
def _and(and_, l, r):
    and_.cb.addILOC("push", "ebx")
    and_.cb.addILOC("mov", "ebx", l.var.getOP())
    and_.cb.addILOC("and", "ebx", r.var.getOP())
    and_.var = Variable(getTempVarName(), "int", and_.ns)
    and_.cb.addILOC("mov", and_.var.getOP(), "ebx")
    and_.cb.addILOC("pop", "ebx")

@aar.action("ifBlock")
def _ifBlock(ifb, *childs):
    for i in range(1, len(childs), 2):
        c0, sl = childs[i - 1], childs[i]
        ifb.cb.addILOC("if", c0.var, "1", sl.cb, ("cur", "next"))
    if len(childs) & 1:
        sl = childs[-1]
        ifb.cb.addILOC("goto", sl.cb, ("cur", "next"))
    else:
        ifb.cb.addILOC("goto", ("cur", "next"))
    ifb.cb.addILOC("seg")

def updateBreakBlock(cur, childs):
    for child in childs:
        child.bb = cur.bb
        child.run(updateBreakBlock)

def updateContinueBlock(cur, childs):
    for child in childs:
        child.lb = cur.lb
        child.run(updateContinueBlock)

@aar.action("whileBlock", index=0)
def _while_0(while_, c0, sl):
    c0.cb = sl.cb

@aar.action("whileBlock", index=1)
def _while_1(while_, c0, sl):
    sl.lb = sl.cb
    sl.run(updateContinueBlock)
    sl.bb = while_.cb
    sl.run(updateBreakBlock)
    sl.cb.addILOC("if", c0.var, "0", (while_.cb, "next"))

@aar.action("whileBlock")
def _while(while_, c0, sl):
    sl.cb.next = (while_.cb, "next")
    while_.cb.addILOC("goto", sl.cb)
    while_.cb.addILOC("seg")
    sl.cb.addILOC("goto", sl.cb)

@aar.action("forBlock", index=0)
def _for_0(for_, init, expr0, stmtl, expr1):
    expr0.cb = stmtl.cb
    expr1.cb = stmtl.cb
    stmtl.bb = for_.cb
    stmtl.run(updateBreakBlock)
    stmtl.lb = stmtl.cb
    stmtl.run(updateContinueBlock)

@aar.action("forBlock", index=2)
def _for_2(for_, init, expr0, stmtl, expr1):
    stmtl.cb.addILOC("if", expr0.var, "0", (for_.cb, "next"))

@aar.action("forBlock")
def _for(for_, init, expr0, stmtl, expr1):
    stmtl.cb.next = (for_.cb, "next")
    for_.cb.addILOC("goto", stmtl.cb)
    for_.cb.addILOC("seg")
    stmtl.cb.addILOC("goto", stmtl.cb)

@aar.action("break")
def _break(break_):
    break_.cb.addILOC("goto", (break_.bb, "next"))

@aar.action("continue")
def _continue(continue_):
    continue_.cb.addILOC("goto", continue_.lb)


declaredFunctions = {}

class Function:

    def __init__(self, returnType, name, parameters, sl):
        self.returnType = returnType
        self.name = name
        self.parameters = parameters
        self.sl = sl
    
    def __str__(self):
        return "%s(%s)" % (self.name, ", ".join("%s %s" % (var.type, var.name) for var in self.parameters))

    def __repr__(self):
        return repr(str(self))


@aar.action("defParam")
def _defParam(defp, type_, id_):
    varName = "__v_%d_%d_%s" % (id_.ns[0], id_.ns[1], id_.getContent())
    if type_.getContent()[0].islower():
        defp.var = Variable(varName, type_.getContent(), defp.ns)
    # TODO reference

@aar.action("defParamList")
def _defParamList(defpl, *defps):
    defpl.list = [_.var for _ in defps]

@aar.action("funcDec", index=0)
def _funcDec_0(func, type_, func_id, defpl, sl):
    defpl.ns = sl.ns
    defpl.run(updateNS)

@aar.action("funcDec", index=3)
def _funcDec_3(func, type_, func_id, defpl, sl):
    offset = 4  # return address need 4 bytes
    for var in defpl.list:
        sl.cb.addILOC("mov", "ebx", "[esp + %d]" % offset)
        sl.cb.addILOC("mov", var.getOP(), "ebx")
        offset += var.size

@aar.action("funcDec")
def _funcDec(func, type_, func_id, defpl, sl):
    funcName = str(func_id.getContent())
    declaredFunctions[funcName] = \
        Function(
            str(type_.getContent()),
            funcName,
            defpl.list,
            sl.cb
        )


builtinFunctions = {}

def builtin(functionName):
    def decorate(function):
        builtinFunctions[functionName] = function
        return function
    return decorate

@builtin("print")
def _print(paramList):
    addEXTERN("_printf")
    fmtParam = []
    totSize = 0
    for param in paramList.getChilds()[::-1]:
        paramList.cb.addILOC("push", param.var.getOP())
        totSize += param.var.size
        type_ = param.var.type
        if type_ == "int":
            fmtParam.append("%" + "d")
        elif type_ == "String":
            fmtParam.append("%" + "s")
    fmtParam.reverse()
    fmtVarName = getTempVarName()
    addDATA(fmtVarName, "db", '"' + " ".join(fmtParam) + '"' + ", 0Ah, 0")
    paramList.cb.addILOC("push", fmtVarName)
    paramList.cb.addILOC("call", "_printf")
    paramList.cb.addILOC("add", "esp", str(totSize + 4))

@aar.action("return")
def _return(return_, c0):
    return_.cb.addILOC("mov", "eax", c0.var.getOP())
    return_.cb.addILOC("ret")

def match(var1, var2):
    return var1.type == var2.type

@aar.action("parameterList")
def _pml(pml, *childs):
    pml.list = [_.var for _ in childs]

@aar.action("functionCall")
def _funcCall(funcCall, funcName, paramList):
    if str(funcName) in builtinFunctions:
        builtinFunctions[str(funcName)](paramList)
    else:
        func = declaredFunctions[str(funcName)]
        if len(paramList.getChilds()) != len(func.parameters):
            print("[ERROR] Function call: Parameter number don't match.")
            exit()
        funcCall.cb.addILOC("push", "eax")
        funcCall.cb.addILOC("push", "ebx")
        totSize = 0
        for i in range(len(func.parameters) - 1, -1, -1):
            if not match(func.parameters[i], paramList.list[i]):
                print("[ERROR] Function call: Parameter %d don't match." % i)
                exit()
            var = paramList.list[i]
            funcCall.cb.addILOC("push", var.getOP())
            totSize += var.size
        funcCall.cb.addILOC("call", func.sl.name)
        funcCall.cb.addILOC("add", "esp", str(totSize))
        funcCall.var = Variable(getTempVarName(), func.returnType, funcCall.ns)
        funcCall.cb.addILOC("mov", funcCall.var.getOP(), "eax")
        funcCall.cb.addILOC("pop", "ebx")
        funcCall.cb.addILOC("pop", "eax")


ast.evaluate(aar)


cbs = {EXIT_BLOCK}
def getCB(cur, *childs):
    cbs.add(cur.cb)
ast.apply(getCB)

# split code blocks by goto
que = deque(cbs)
while que:
    cb = que.pop()
    segmentation = cb.getSegments()
    for i in range(1, len(segmentation)):
        cbs.add(segmentation[i])
        que.append(segmentation[i])

for cb in cbs:
    cb.updateCur()

# If A would like to goto B.next, we have to calculate
# B.next first before calculate A.
# If A.next is (B, next), then we have to calculate
# B.next before calculate CB that containing A.next.
nextDependency = {}
indeg = {k: 0 for k in cbs}

for cb in cbs:
    if isinstance(cb.next, tuple):
        nextDependency.setdefault(cb.next, []).append((cb, "next"))
        indeg[cb.next] = 0
        indeg[(cb, "next")] = 0
    for op, *_ in cb:
        if op == "goto":
            dest, *back = _[0]
            if isinstance(dest, tuple):
                nextDependency.setdefault(dest, []).append(cb)
                if back:
                    back = back[0]
                    nextDependency.setdefault(back, []).append(dest)
                    indeg[back] = 0
                indeg[dest] = 0
                indeg[cb] = 0
        elif op == "if":
            lop, rop, dest, *back = _
            if isinstance(dest, tuple):
                nextDependency.setdefault(dest, []).append(cb)
                if back:
                    back = back[0]
                    nextDependency.setdefault(back, []).append(dest)
                    indeg[back] = 0
                indeg[dest] = 0
                indeg[cb] = 0

for k, v in nextDependency.items():
    for dest in v:
        indeg[dest] += 1

# toposort
que = deque(k for k in indeg if not indeg[k])
while que:
    cur = que.pop()
    if isinstance(cur, tuple):
        cur[0].updateNext()
    else:
        cur.updateNext()
    if cur in nextDependency:
        for v in nextDependency[cur]:
            if v not in indeg:
                que.append(v)
            indeg[v] -= 1
            if not indeg[v]:
                que.append(v)

for cb in cbs:
    cb.updateNone()


ControlFlowGraph = {}

# change if and goto to jz and jmp
for cb in cbs:
    for i, (op, *rest) in enumerate(cb):
        cb.list[i] = list(cb.list[i])
        if op == "goto":
            cb.list[i][0] = "jmp"
            ControlFlowGraph.setdefault(cb, []).append(cb.list[i][1])
            if len(cb.list[i]) == 3:
                cb.list[i][1].addILOC("jmp", cb.list[i][2])
                ControlFlowGraph.setdefault(cb, []).append(cb.list[i][2])
                cb.list[i] = cb.list[i][:-1]
        elif op == "if":
            c0, const, st, *back = rest
            cb.list[i] = [
                ["push", "ebx"],
                ["mov", "ebx", c0.getOP()],
                ["cmp", "ebx", const],
                ["pop", "ebx"],
                ["jz", st]
            ]
            ControlFlowGraph.setdefault(cb, []).append(st)
            if back:
                back = back[0]
                st.addILOC("jmp", back)
                ControlFlowGraph.setdefault(cb, []).append(back)


# check cb that need jmp to _exit
outdeg = {}
for src, dests in ControlFlowGraph.items():
    outdeg[src] = len(dests)
    for dest in dests:
        if dest not in outdeg:
            outdeg[dest] = 0

for k, v in outdeg.items():
    if not v:
        k.addILOC("jmp", EXIT_BLOCK)


for ex in EXTERN:
    print("extern %s" % ex)
print("global _main")
print("\nsection .data")
print("\n".join(DATA))
print("\nsection .bss")
print("\n".join(BSS))
print("\nsection .text")
for cb in cbs:
    print("%s:" % cb.name)
    for line in cb:
        if line[0] != "seg":
            if not isinstance(line[0], list):
                print("    %s %s" % (str(line[0]), ", ".join(str(_) for _ in line[1:])))
            else:
                for l in line:
                    print("    %s %s" % (str(l[0]), ", ".join(str(_) for _ in l[1:])))