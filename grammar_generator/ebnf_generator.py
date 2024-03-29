import re
import sys
import json
from lark import Lark

"""
we want two things here
1. a generated grammar from the generalized_input.json file
    I'll convert it to a string (EBNF), because this is what Lark wants
2. a parser, which will be generated by Lark
"""
START_NAME = "start"
TERM_NAME = "term"
TERMINAL_NAME = "terminal"
TERMINAL_STRING = f"""
{TERMINAL_NAME}: (DIGIT | LETTER)+

%import common.DIGIT
%import common.LETTER
    """

def get_json(filename):
    f = open(filename, 'r')
    return json.load(f)


def generalized_input_to_rule(input):
    return " ".join(["".join(["\"", s, "\""]) if isinstance(s, str) else TERMINAL_NAME for s in input])
def generate_ebnf(filename):
    data = get_json(filename)
    grammar = f"?{START_NAME}:"
    def format_entry(entry):
        return "".join([" ", generalized_input_to_rule(entry.get("generalized").get("input"))])
    rules_str = map(format_entry, data)
    grammar += "\n|".join(rules_str)
    # for entry in data:
    #     grammar = "".join([grammar, "\t| ", generalized_input_to_rule(entry.get("generalized").get("input")), "\n"])
    return "".join([grammar, TERMINAL_STRING])


def generalized_input_to_rule_v2(input):
    expr = "".join([re.escape(s) if isinstance(s, str) else ".+" for s in input])
    return "".join(["/", expr, "/"])


def generate_ebnf_v2(filename):
    data = get_json(filename)
    grammar = f"?{START_NAME}:"

    def format_entry(entry):
        return "".join([" ", generalized_input_to_rule_v2(entry.get("generalized").get("input"))])
    rules_str = map(format_entry, data)
    grammar += "\n|".join(rules_str)
    # for entry in data:
    #     grammar = "".join([grammar, "\t| ", generalized_input_to_rule(entry.get("generalized").get("input")), "\n"])
    return grammar

def generalized_input_to_rule_v3(input):
    return " ".join([f"/{re.escape(s)}/" if isinstance(s, str) else TERMINAL_NAME for s in input])

def generalized_input_to_terminals_v3(input):
    return "\n| ".join(set([f"/{re.escape(s.get('removed'))}/" for s in input if not isinstance(s, str)]))

def generate_ebnf_v3(filename):
    data = get_json(filename)
    grammar = f"?{START_NAME}:"

    def format_entry(entry):
        return "".join([" ", generalized_input_to_rule_v3(entry.get("generalized").get("input"))])
    rules_str = map(format_entry, data)
    grammar += "\n|".join(rules_str)

    terminals = []
    for entry in data:
        terminals.append(generalized_input_to_terminals_v3(entry.get("generalized").get("input")))
    terminal_str = f"\n{TERMINAL_NAME}:" + "\n| ".join(terminals)

    return "".join([grammar, terminal_str])

def generalized_input_to_rule_v4(input):
    return " ".join([f"/{re.escape(s)}/" if isinstance(s, str) else TERM_NAME for s in input])

def generalized_input_to_terminals_v4(input):
    return "\n| ".join(set([f"/{re.escape(s.get('removed'))}/" for s in input if not isinstance(s, str)]))

def generate_ebnf_v4(filename):
    data = get_json(filename)
    grammar = f"?{START_NAME}:"

    def format_entry(entry):
        return "".join([" ", generalized_input_to_rule_v4(entry.get("generalized").get("input"))])
    rules_str = map(format_entry, data)
    grammar += "\n|".join(rules_str)

    grammar += f"\n{TERM_NAME}: {START_NAME} | {TERMINAL_NAME}"

    terminals = []
    for entry in data:
        terminals.append(generalized_input_to_terminals_v4(entry.get("generalized").get("input")))
    terminal_str = f"\n{TERMINAL_NAME}:" + "\n| ".join(terminals)

    return "".join([grammar, terminal_str])



def main(argv):
    print(generate_ebnf_v4(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
