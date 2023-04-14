import re
import string
import sys
import json

from grammar_generator.ebnf import Grammar, Rule
from models.ReplaceClass import ReplaceClass

START_NAME = "start"
TERM_NAME = "term"

def get_json(filename):
    f = open(filename, 'r')
    return json.load(f)

def str_to_lark_regex(s: str):
    return f"/{escape_regex(s)}/x"

def escape_regex(str):
    return re.escape(str).replace("/", "\\/")

def generalized_input_to_regex(input):
    regex = "".join([s if isinstance(s, str) else "(.+)" for s in input])
    return re.compile(regex)

def add_terminal_class_rule(grammar, rule_name, rule_value):
    rule = Rule(rule_name)
    for c in rule_value:
        if c == "\n":
            continue # TODO: currently ebnf doesn't work with newline
        rule.add_body([str_to_lark_regex(c)])
    grammar.add_rule(rule)

# Generates an arbitrary-length repeat version of the given rule
# eg. rule_name = "rule", generates
# rules : rule | rule rules
def add_repeat_rule(grammar, rule_name):
    repeat_rule_name = rule_name + "s"
    rule = Rule(repeat_rule_name)
    rule.add_body([rule_name]).add_body([rule_name, repeat_rule_name])
    grammar.add_rule(rule)

def generate_start_rule_body(generalized_input):
    rule_body = []
    replacements_set = set()
    for token in generalized_input:
        if isinstance(token, str):
            rule_body.append(str_to_lark_regex(token))
        elif token.get("type") == "DELETE":
            pass  # do not add anything to the rule
        elif token.get("type") == "REPLACE":
            replacements = token.get("replacements")
            replacement_strs = [f"{r.lower()}" for r in replacements if r != "NUMBER"]  # remove numbers for now, TODO
            replacements_set.update(replacement_strs)
            rule_body.append([f"{r}s" for r in replacement_strs] + [START_NAME.lower()])  # add repeat rule, add start name here to allow recursion

    return rule_body, replacements_set


def generate_ebnf_replacement(saved_inputs_filename):
    saved_data = get_json(saved_inputs_filename)

    grammar = Grammar(START_NAME)

    start_rule = Rule(START_NAME)
    seen_replacements = set()
    for entry in saved_data:
        # add subrule based on input
        generalized_input = entry.get("generalized").get("input")
        body, body_replacements = generate_start_rule_body(generalized_input)
        start_rule.add_body(body)
        seen_replacements.update(body_replacements)
    grammar.add_rule(start_rule)

    # add terminal class rules
    for replacement_class in seen_replacements:
        replace_enum = ReplaceClass.get_enum_value(replacement_class)
        add_terminal_class_rule(grammar, replacement_class, ''.join(ReplaceClass.get_char(replace_enum)))
        add_repeat_rule(grammar, replacement_class)

    print(grammar.pretty_print())
    return grammar

def main(argv):
    grammar = generate_ebnf_replacement(argv[1])
    print(grammar.sample_positives(10, 3))


if __name__ == "__main__":
    main(sys.argv)
