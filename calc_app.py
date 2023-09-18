import json
from lang_def import LangDef

ld = LangDef.from_json(json.load(open("calc_v2.json", "r")))

while True:
    try:
        inputString = input(">>> ")
        print(ld.eval(inputString, {}))

    except EOFError:
        break
