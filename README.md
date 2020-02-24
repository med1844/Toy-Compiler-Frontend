# newCompilerTest
Python implementation of scanner, LR(1) Parsing method, Action &amp; Goto Table, Parse Tree &amp; AST.

On top of these, I implemented a compiler that translate an experimental language `simpleJava` into NASM.

## How to use

### Create Action & Goto and save them

1. write TypeDefinition files that define matching rules of different type of tokens.
2. write CFG files that define the Context Free Grammar you want to use.
3. Load them.
4. use `Parser.genActionGoto` to generate Action & Goto table.

```python
typedef = TypeDefinition.load("TYPEDEF")
cfg = ContextFreeGrammar.load(typedef, "CFG")
action, goto = Parser.genActionGoto(typedef, cfg)
action.save('ACTION')
goto.save('GOTO')
```

The format of typeDef and CFG files are described in `typeDef.py` and `cfg.py`, and examples are available in `/simpleCalc`, `/simpleJava`, and `/simpleSQL`.

### Use scanner and Action & Goto to parse input string

1. read input.
2. use `scanner.parse` to split tokens.
3. use `Parser.parse` to get `ParseTre`e.

```python
action = Action.load(cfg, "ACTION")
goto = Goto.load(cfg, "GOTO")

with open("SOURCE", "r") as f:
    src = f.read()
tokenList = scanner.parse(typedef, src, ['line_comment', 'block_comment', 'space'])
pt = Parser.parse(tokenList, typedef, cfg, action, goto)
```

### Use ParseTree to evaluate attribute grammars

Simple attribute grammar is supported by `ParseTreeActionRegister`.

Use decorators to create link between productions and functions:

```python
ar = ParseTreeActionRegister(cfg)

@ar.production('F -> F ** G')
def __f0(f, f1, _, g):
    f.val = f1.val ** g.val

@ar.production('G -> ( E )')
def __g0(g, leftPar, e, rightPar):
    g.val = e.val

@ar.production('G -> int_const')
def __g1(g, int_const):
    g.val = int(int_const.getContent())

@ar.production('G -> id')
def __g2(g, id_):
    global d
    g.val = d[id_.getContent()]
```

The example above shows how to evaluate values using attribute grammars. You can also use them to build AST:

```python
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
```

It is also possible to use `ParseTree` to generate other intermediate representations.

### Define action on each AST node

Similar to `ParseTreeActionRegister.production`, use `ASTActionRegister.action` to map an actionID to a function.

Each `ASTNode` has an actionID for performing actions. By default, actionID equals to the content:

```python
class ASTNode(TreeNode):

    def __init__(self, content, *childs, actionID=None):
        if actionID is None:
            actionID = content
```

But if the `actionID` parameter is set, then the `ASTNode` would not replace it with content.

Then just use `astar.action` to decorate functions:

```python
@aar.action("add")
def _add(add, l, r):
    add.cb.addILOC("push", "eax")
    add.cb.addILOC("mov", "eax", r.var.getOP())
    add.cb.addILOC("add", "eax", l.var.getOP())
    add.var = Variable(getTempVarName(), getType(l, r), add.ns)
    add.cb.addILOC("mov", add.var.getOP(), "eax")
    add.cb.addILOC("pop", "eax")
```

## About simpleJava

This is a small experimental language. 

When I design it, I hope it can support class definition and methods like java, while you can still write code in the biggest scope. That is to say, there is no need to declare a class and write a `public static void main(String[] args)` method to make the code run.

I also hope it can offer friendly learning experience that python does. Builtin functions like `print`, `open`, `with` are just awesome.

But I found such ideas are super hard to implement in assembly language. The more code I wrote, the harder it became to maintain. Eventually I decided to give up and enjoy the last several days of my winter vacation.

Now simpleJava supports:

- integer constant and string literal
- print (using _printf)
- integer variable declaration (only integer)
- variable assignment, basic arithmatics (+, -, *, /, %, etc) and conditions (and, or, not, ==, !=, etc)
- `if`, `else`, `while`, `for`
- `continue`, `break`
- function declaration with integer return value

The rest rules are just the same as `java` and `C`. See test source files in `/simpleJava` for examples.

### How to compile and run

I have only tested this compiler on windows 10, 64 bit, python 3.7.5. The code it produces may not be able to run on other platforms.

Since this is just a compiler test, I decided not to use tools that parse command line options, so it maybe hard to use.

1. install nasm, minGW, and configure PATH.
2. write your `.sjava` file and save it as FILENAME.sjava.
3. change line 392 in `simpleJavaCompiler.py`, open the file you just saved.
4. `python simpleJavaCompiler.py > FILENAME.asm`
5. `nasm -f win32 FILENAME.asm`
6. `gcc FILENAME.obj -o FILENAME.exe`
7. `FILENAME.exe`
