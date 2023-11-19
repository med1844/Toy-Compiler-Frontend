# Compiler front-end framework

[![pre-commit](https://github.com/medioqrity/Compiler-Frontend/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/medioqrity/Compiler-Frontend/actions/workflows/pre-commit.yml)

This repository contains:

- A regex engine that supports a subset of regex, based on Min-DFA.
- A LR(1) transition table generator.
- A portable scanner + parser, and built-in CFG production action support (i.e. functions to be called when some production is reduced)

## How to use

To start with, you need to build a language definition object using `LangDefBuilder` class method:

```python
from lang_def_builder import LangDefBuilder

ld = LangDefBuilder.new(
    """
    START -> E
    E -> E "+" T | E "-" T | T
    T -> T "*" F | F
    F -> "(" E ")" | int_const
    int_const -> r"0|(-?)[1-9][0-9]*"
    """
)
```

`ld` has type `LangDef`, which stores all information required to parse the language you defined.

You could then define **actions** that should be executed when a production was recognized by decorating `ld`:

```python
@ld.production("E -> T", "T -> F", "F -> int_const")
def __identity(_, e: int) -> int:
    return e

@ld.production('E -> E "+" T')
def __add(_, e: int, _p: str, t: int) -> int:
    return e + t

@ld.production('E -> E "-" T')
def __sub(_, e: int, _m: str, t: int) -> int:
    return e - t

@ld.production('T -> T "*" F')
def __mul(_, t: int, _m: str, f: int) -> int:
    return t * f

@ld.production('F -> "(" E ")"')
def __par(_, _l, e: int, _r) -> int:
    return e

@ld.production('int_const -> r"0|(-?)[1-9][0-9]*"')
def __int(_, int_const: str) -> int:
    return int(int_const)
```

You can now host a calculator within a few lines:

```python
while True:
    try:
        print(ld.eval(input(">>> "), {}))
    except EOFError:
        break
```

Save these code snippets into a file, e.g. `test_calc.py`. Then, you should get a working calculator:

```
$ python test_calc.py
>>> 5 + 6 * 7 - (8 - 9 * 10)
129
>>> (5 + 6) * 7 - 8 - 9 * 10
-21
>>>
```

## Portability

You don't have to always copy & paste heavy dependencies such as `TypeDefinition`, `ContextFreeGrammar`, and `dfa_utils` when you need to use them.

If you want to use a parser in your project, you only need to copy `lang_def.py`, where all transition tables are stored, and all parsing algorithms are defined.

You can do this by calling `ld.to_json()`. This would dump all internal transition tables into a single `LangDef`:

```python
json.dump(ld.to_json(), open("calc_v2.json", "w"))
```

Notice that **associated action functions would not be saved**. You must manually define them after you loaded `LangDef` using `LangDef.from_json()`.

For example:

```python
import json
from lang_def import LangDef

ld = LangDef.from_json(json.load(open("calc_v2.json", "r")))

@ld.production("E -> T", "T -> F", "F -> int_const")
def __identity(_, e: int) -> int:
    return e

@ld.production('E -> E "+" T')
def __add(_, e: int, _p: str, t: int) -> int:
    return e + t

@ld.production('E -> E "-" T')
def __sub(_, e: int, _m: str, t: int) -> int:
    return e - t

@ld.production('T -> T "*" F')
def __mul(_, t: int, _m: str, f: int) -> int:
    return t * f

@ld.production('F -> "(" E ")"')
def __par(_, _l, e: int, _r) -> int:
    return e

@ld.production('int_const -> r"0|(-?)[1-9][0-9]*"')
def __int(_, int_const: str) -> int:
    return int(int_const)

while True:
    try:
        print(ld.eval(input(">>> "), {}))
    except EOFError:
        break
```

This would allow you avoid rebuilding transition tables from definitions each time, which could be time-consuming when the definition is too large.

## Web app

We provided a web app that could print out the content of each LR(1) item set, and their transition tables. On top of that, you can parse and see result in real time:

![webapp](webapp.svg)

The screenshot shows the parsing result of this expression:

```lisp
(define (even? x)
  (& x 1))
```

The underlying CFG is:

```
START -> expression
expression -> function_call | val
function_call -> "(" id arguments ")"
arguments -> expression arguments | expression
val -> int_const | id
int_const -> r"0|(-?)[1-9][0-9]*"
id -> r".|([a-zA-Z]|_)([a-zA-Z]|[0-9]|_|\?)*"
```

### Start web app

```python
flask --app server.py run
```

## Supported regex

Currently it only supports `*`, `|`, `?`, `+`, `[a-z]`, `[^x]`. You may use `\` to change the meaning of these special chars, including `\` itself.

The core underlying mechanism is range matching. An edge in DFA could accept multiple ranges of chars.

## Supported CFG

We used a slight variant of BNF form:
- `::=` got replaced by `->`.
- Texts surrounded by quotes, e.g. `"xxx"`, represents terminals. On top of BNF form, we introduced `r"..."` to tell that this terminal should be parsed using regex engine.
- `''` means epsilon.
- Everything else that's not wrapped in quotes are considered as non-terminal. If you prefer wrapping them with `<>`, you are free to do so.
- You must use `START` as the entry non-terminal.

Here's an example:

```
START -> E
E -> E "+" T | E "-" T | T
T -> "(" E ")" | int_const
int_const -> r"0|(-?)[1-9][0-9]*"
```

In this CFG, `"+", "-", "(", ")", r"0|(-?)[1-9][0-9]*"` are terminals, `START, E, T, int_const` are non-terminals.

Notice that in plain terminals (`"+", "-", "(", ")"`), you don't need to use `\` to alter their meanings. Instead, they would be all treated as normal chars to be matched.

## Planned improvements

<details>

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
  - [x] Add accept state id propagation & merge for faster scanning
- [x] Migrate to typed python
- [x] Make parser a module (now it's `LangDef`)
- [x] Optimize parser memory usage by eliminating building actual parse tree
- [x] Add unit tests for each module
- [x] (Cancelled) ~~Define interfaces for CFG parser & implement other parsers (LL1, etc)~~
- [ ] Improve `ContextFreeGrammar.from_string` parser, make it support `r"[^ ]*"`
- [ ] Further optimize the performance of `LangDef`
- Web app optimizations:
  - [x] (Cancelled) ~~Add custom `TypeDefinition` to web app~~
    You don't have to provide a separate type definition file now
  - [ ] Add example `TypeDefinition` and `ContextFreeGrammar` to web app
- Language definition QOL issues:
  - [x] Unify `TypeDefinition` and `ContextFreeGrammar` into one file (CFG section, typedef section)
    Note: not by dividing into sections, but by integrating literals into CFG
  - [x] Remove boilerplate definitions in `typedef`, i.e. things don't need regex power (e.g. `public public`, `( \(`)
  - [x] (Cancelled) ~~Make `ContextFreeGrammar` support BNF notation (or maybe extended BNF?)~~
    - My personal preference is `->` over `::=`; I also need regex support
    - Adding brackets, like `<non_terminal>`, is supported as long as they don't contain space
- [x] Move `simpleSQL` and `simpleJava` to other repositories
  - [ ] For `simpleSQL`, implement an operator-based sql engine in a separate project
  - [ ] For `simpleJava`, implement IR passes & maybe generate LLVM IRs in a separate project
    - [ ] control flow graph generation?
    - [ ] SSA generation?
    - [ ] Partial redundancy elimination?
- [x] (Cancelled) ~~Add CLI support for generating a standalone front end parser (.py) given type definition, CFG definition, and tree action.~~
  - Already fulfilled by `LangDef` class.

</details>
