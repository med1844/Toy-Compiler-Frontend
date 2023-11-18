"""
Back-end for the visualization of the parsing process
"""

from flask import render_template, Flask, request
from cfg import ContextFreeGrammar, gen_action_todo, LangPrinter
from lang_def import LangDef
from lang_def_builder import LangDefBuilder
import os
from typing import List, Tuple
from vis_utils.tree import Tree, TreeNode

app = Flask(__name__)


app.secret_key = os.urandom(16)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generateLR", methods=["POST"])
def generate():
    rawCFG = request.form["CFG"]
    cfg = ContextFreeGrammar.from_string(rawCFG)
    lp = LangPrinter(cfg)

    app.config["cfg"] = cfg
    app.config["ld"] = LangDefBuilder.new(cfg)
    app.config["lp"] = lp

    dump_dst = []
    action, goto = gen_action_todo(cfg, dump_dst)
    item_set_to_id, edges = dump_dst.pop()

    terminals, non_terminals = sorted(action.terminals), sorted(goto.non_terminals)
    symbols = terminals + non_terminals
    result = [["state"] + list(map(lp.to_string, symbols))]

    for i in range(len(action)):
        result.append(
            [str(i)]
            + [str(action[i][str(k)]) if str(k) in action[i] else "" for k in terminals]
            + [str(goto[i][k]) if k in goto[i] else "" for k in non_terminals]
        )

    itemToID = {}
    for k, v in item_set_to_id.items():
        itemToID[lp.to_string(k)] = v

    cfgForFirst = cfg.remove_left_recursion() if cfg.is_left_recursive() else cfg
    firstDict = cfgForFirst.first()
    firstSet = {
        k: ", ".join([lp.to_string(sym) for sym in v])
        for k, v in firstDict.items()
    }

    return render_template(
        "parse_result.html", itemToID=itemToID, table=result, firstSet=firstSet
    )


def parse_pt_n_log(cfg: ContextFreeGrammar, ld: LangDef, lp: LangPrinter, tokens: List[Tuple[int, str]]) -> Tuple[Tree, List[str]]:
    log = []
    state_stack = [0]
    node_stack: List[TreeNode] = [
        TreeNode("$")
    ]  # str -> terminal, Any -> evaluated non_terminal, depends on PT action fn return type

    for token_type, lex_str in tokens:
        current_state = state_stack[-1]
        while True:
            if ld.action_json["table"][current_state][str(token_type)] is None:
                raise ValueError("ERROR: %s, %s" % (current_state, str(token_type)))
            action_type, next_state = ld.action_json["table"][current_state][
                str(token_type)
            ]
            if action_type == 0:  # shift to another state
                state_stack.append(next_state)
                node_stack.append(TreeNode(lex_str))
                log.append((str(state_stack), str(node_stack), "Shift to state %d" % next_state))
                break
            elif action_type == 1:
                prod_id: int = next_state
                non_terminal, sequence = cfg.get_production(prod_id)
                nargs = len(sequence)
                log.append((str(state_stack), str(node_stack), "Reduce using production %d: %s -> %s" % (prod_id, non_terminal, " ".join(lp.to_string(v) for v in sequence))))
                non_terminal_node = TreeNode(non_terminal)
                for _ in range(nargs):
                    state_stack.pop()
                    non_terminal_node.childs.append(node_stack.pop())
                non_terminal_node.childs.reverse()

                current_state = state_stack[-1]
                next_state = ld.goto_json["table"][current_state][non_terminal]
                state_stack.append(next_state)
                node_stack.append(non_terminal_node)
                current_state = state_stack[-1]
                continue
            elif action_type == 2:
                break
            else:
                assert False

    return Tree(node_stack[-1]), log


@app.route("/parse", methods=["POST", "GET"])
def parse():
    string = request.form["string"]
    cfg = app.config["cfg"]
    ld = app.config["ld"]
    lp = app.config["lp"]
    token_list = ld.scan(string)
    pt, log = parse_pt_n_log(cfg, ld, lp, token_list)
    return {"pt": str(pt), "log": log}
