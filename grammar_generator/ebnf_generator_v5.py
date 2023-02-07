import re
import sys
import json

from ebnf import Grammar, Rule

START_NAME = "start"
TERM_NAME = "term"
TERMINAL_NAME = "terminal"

def get_json(filename):
    f = open(filename, 'r')
    return json.load(f)

def escape_regex(str):
    return re.escape(str).replace("/", "\\/")

def generalized_input_to_regex(input):
    regex = "".join([re.escape(s) if isinstance(s, str) else "(.+)" for s in input])
    return re.compile(regex)

def generate_ebnf_v5(saved_inputs_filename, valid_inputs_filename):
    saved_data = get_json(saved_inputs_filename)
    valid_data = get_json(valid_inputs_filename)

    grammar = Grammar()

    start_rule = Rule(START_NAME)
    generalized_input_regexes = []
    for entry in saved_data:
        # add subrule based on input
        generalized_input = entry.get("generalized").get("input")
        start_rule.add_body([f"/{escape_regex(s)}/" if isinstance(s, str) else TERM_NAME for s in generalized_input])
        # create regex from input
        r = generalized_input_to_regex(generalized_input)
        generalized_input_regexes.append(r)
    grammar.add_rule(start_rule)

    grammar.add_rule(Rule(TERM_NAME).add_body([START_NAME]).add_body([TERMINAL_NAME]))

    terminal_rule = Rule(TERMINAL_NAME)
    terminals = set()
    for entry in valid_data:
        valid_input = entry.get("data")
        for pattern in generalized_input_regexes:
            m = pattern.match(valid_input)
            if m is None:
                pass
            else:
                terminals = terminals.union(m.groups())
    for terminal in terminals:
        terminal_rule.add_body([f"/{escape_regex(terminal)}/"])
    grammar.add_rule(terminal_rule)

    return grammar.pretty_print()

def main(argv):
    print(generate_ebnf_v5(argv[1], argv[2]))


if __name__ == "__main__":
    main(sys.argv)
