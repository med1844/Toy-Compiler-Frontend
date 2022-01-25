"""
Back-end for the visualization of the compile process
"""

from flask import render_template, Flask, request, make_response, redirect, url_for
from cfg import ContextFreeGrammar
from typeDef import TypeDefinition
import Parser
import scanner
import os
app = Flask(__name__)


app.secret_key = os.urandom(16)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generateLR', methods=['POST'])
def generate():
    rawCFG = request.form['CFG']
    typedef = TypeDefinition.load("simpleJava/typedef")
    cfg = ContextFreeGrammar.loadFromString(typedef, rawCFG)
    action, goto, rawItemToID = Parser.genActionGoto(typedef, cfg, needItemToID=True)
    terminals, nonTerminals = action.terminals(), goto.nonTerminals()
    symbols = terminals + nonTerminals
    result = [["state"] + symbols]
    app.typedef = typedef
    app.cfg = cfg
    app.action = action  # should be session or cookie... but I don't know how
    app.goto = goto

    for i in range(len(action)):
        result.append([str(i)] + [str(action[i][k]) for k in terminals] + [str(goto[i][k]) for k in nonTerminals])

    itemToID = {}
    for k, v in rawItemToID.items():
        itemToID[Parser.toStr(typedef, k)] = v
    
    cfgForFirst = cfg.removeLeftRecursion() if cfg.isLeftRecursive() else cfg
    firstDict = Parser.first(cfgForFirst)
    firstSet = {k: ', '.join([typedef.getDisplayName(sym) for sym in v])
                for k, v in firstDict.items()}

    return render_template(
        "parse_result.html", 
        itemToID=itemToID,
        table=result,
        firstSet=firstSet
    )

@app.route('/parse', methods=['POST', 'GET'])
def parse():
    string = request.form['string']
    tokenList = scanner.parse(app.typedef, string, ["space"])
    
    pt, log = Parser.parse(tokenList, app.typedef, app.cfg, app.action, app.goto, needLog=True)
    return {
        'pt': str(pt),
        'log': log
    }