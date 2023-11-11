# newCompilerTest

Python implementation of scanner, LR(1) Parsing method, Action &amp; Goto Table, Parse Tree &amp; AST.

On top of these, I implemented a compiler that translate an experimental language `simpleJava` into NASM.

## How to use

First, you should provide regex definition of tokens, and the context free grammar of your language.

For demonstration purpose, here I will define a language that describes a subset of all possible arithmetic expressions:

```python
from typeDef import TypeDefinition
from cfg import ContextFreeGrammar


typedef = TypeDefinition()
typedef.add_definition("+", r"\+")
typedef.add_definition("-", r"-")
typedef.add_definition("*", r"\*")
typedef.add_definition("(", r"\(")
typedef.add_definition(")", r"\)")
typedef.add_definition("int_const", r"0|(-?)[1-9][0-9]*")
cfg = ContextFreeGrammar.from_string(
    typedef,
    """
    START -> E
    E -> E + T | E - T | T
    T -> T * F | F
    F -> ( E ) | int_const
    """,
)
```

Then, you need to build a `LangDef` object through `LangDefBuilder`:

```python
from lang_def_builder import LangDefBuilder

ld = LangDefBuilder.new(typedef, cfg)
```

`ld` stores all information required to parse the language you defined.

You could then define **actions** that should be executed when a production was recognized by decorating `ld`:

```python
@ld.production("E -> T", "T -> F")
def __identity(_, e: int) -> int:
    return e

@ld.production("E -> E + T")
def __add(_, e: int, _p: str, t: int) -> int:
    return e + t

@ld.production("E -> E - T")
def __sub(_, e: int, _m: str, t: int) -> int:
    return e - t

@ld.production("T -> T * F")
def __mul(_, t: int, _m: str, f: int) -> int:
    return t * f

@ld.production("F -> ( E )")
def __par(_, _l, e: int, _r) -> int:
    return e

@ld.production("F -> int_const")
def __int(_, int_const: str) -> int:
    return int(int_const)
```

You can now host a calculator using a few lines:

```python
while True:
    try:
        print(ld.eval(input(">>> "), {}))
    except EOFError:
        break
```

You should get a working calculator:

```
> python test_calc.py
>>> 5 + 6 * 7 - (8 - 9 * 10)
129
>>> (5 + 6) * 7 - 8 - 9 * 10
-21
>>>
```

## Portability

You don't have to always copy & paste heavy dependencies such as `TypeDefinition`, `ContextFreeGrammar`, and `dfa_utils` when you need to use them.

If you want to use a parser in your project, you only need to copy `lang_def.py`, where all transition tables are stored, and all parsing algorithms are defined.

You can do this by calling `ld.to_json()`. This would dump all internal transition tables into a single `LangDef`.

Notice that associated action functions would not be saved. You must manually define them after you loaded `LangDef` using `LangDef.from_json()`.

For example:

```python
import json
from lang_def import LangDef

ld = LangDef.from_json(json.load(open("calc_v2.json", "r")))

@ld.production("E -> E + T")
def __e0(_c, e: int, _: str, t: int):
    return e + t

@ld.production("E -> E - T")
def __e1(_c, e: int, _: str, t: int):
    return e - t

@ld.production("E -> T")
def __e2(_c, b):
    return b

@ld.production("E -> - T")
def __e3(_c, _: str, t: int):
    return -t

@ld.production("T -> ( E )")
def __g0(_, _leftPar: str, e: int, _rightPar: str):
    return e

@ld.production("T -> int_const")
def __g1(_, int_const: str):
    return int(int_const)

while True:
    try:
        print(ld.eval(input(">>> "), {}))
    except EOFError:
        break
```

This would allow you avoid rebuilding transition tables from definitions each time, which could be time-consuming when the definition is too large.

## Planned improvements

- [x] Rewrite lexer using DFA instead of NFA-based `re`
  - [x] Impl regex parser that generates NFA
    - [x] `*`
    - [x] `|`
    - [x] `?`
    - [x] `()`
    - [x] `+` (requires impl `Copy` trait for `FiniteAutomata`)
    - [x] `\`
    - [x] `[x-x]`
    - [x] `.`
  - [x] Impl NFA to DFA algo
    - [x] Add tests
  - [x] Impl minimize DFA algo
    - [x] Add tests
  - [x] Write a hash function that encodes the structural information of arbitrary finite automata for auto tests
  - [x] Implement a lexer that's based on DFA
  - [x] Add FA serialization & de-serialization
  - [ ] Add accept state id propagation & merge for faster scanning
- [x] Migrate to typed python
- [ ] Make parser a module
- [x] Optimize parser memory usage by eliminating building actual parse tree
- [x] Add unit tests for each module
- [ ] Define interfaces for CFG parser & implement other parsers (LL1, etc)
- [ ] Move `simpleSQL` and `simpleJava` to other repositories
  - [ ] For `simpleSQL`, implement an operator-based sql engine in a separate project
  - [ ] For ``simpleJava, implement IR passes & maybe generate LLVM IRs in a separate project
    - [ ] control flow graph generation?
    - [ ] SSA generation?
    - [ ] Partial redundancy elimination?
- [ ] Add CLI support for generating a standalone front end parser (.py) given type definition, CFG definition, and tree action.
