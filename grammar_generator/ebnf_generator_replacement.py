import re
import string
import sys
import json

from grammar_generator.ebnf import Grammar, Rule

START_NAME = "start"
TERM_NAME = "term"
TERMINAL_NAME = "terminal"
DIGITS_NAME = "digits"
# NUMBERS_NAME = "numbers"
HEXDIGITS_NAME = "hexdigits"
LETTERS_NAME = "letters"
WHITESPACES_NAME = "whitespaces"
PUNCTUATIONS_NAME = "punctuations"
ALPHANUMERICS_NAME = "alphanumerics"
PRINTABLE_NAME = "printable"

def get_json(filename):
    f = open(filename, 'r')
    return json.load(f)

def escape_regex(str):
    return re.escape(str).replace("/", "\\/")

def generalized_input_to_regex(input):
    regex = "".join([re.escape(s) if isinstance(s, str) else "(.+)" for s in input])
    return re.compile(regex)

def add_terminal_class_rule(grammar, rule_name, rule_value):
    rule = Rule(rule_name)
    for c in rule_value:
        rule.add_body([c])
    grammar.add_rule(rule)

def generate_start_rule_body(generalized_input):
    rule_body = []
    for token in generalized_input:
        if isinstance(token, str):
            # print(f"token: {token}")
            rule_body.append(token)
        elif token.get("type") == "DELETE":
            pass # do not add anything to the rule
        elif token.get("type") == "REPLACE":
            replacements = token.get("replacements") + [START_NAME] # add start name here to allow recursion
            # print(f"replacements: {replacements}")
            rule_body.append([r.lower() for r in replacements if r != "NUMBERS"]) # remove numbers for now, TODO
                                                                                  # TODO: should be CLASS+ instead of CLASS, right now only expands to 1 character
    return rule_body


def generate_ebnf_replacement(saved_inputs_filename):
    saved_data = get_json(saved_inputs_filename)

    grammar = Grammar(START_NAME)

    start_rule = Rule(START_NAME)
    generalized_input_regexes = []
    for entry in saved_data:
        # add subrule based on input
        generalized_input = entry.get("generalized").get("input")
        start_rule.add_body(generate_start_rule_body(generalized_input))
        # start_rule.add_body([f"/{escape_regex(s)}/" if isinstance(s, str) else TERM_NAME for s in generalized_input])
        # create regex from input
        r = generalized_input_to_regex(generalized_input)
        generalized_input_regexes.append(r)
    grammar.add_rule(start_rule)

    # grammar.add_rule(Rule(TERM_NAME).add_body([START_NAME]).add_body([TERMINAL_NAME]))

    # add terminal class rules
    add_terminal_class_rule(grammar, DIGITS_NAME, string.digits)
    # grammar.add_rule(Rule(NUMBERS_NAME))
    add_terminal_class_rule(grammar, HEXDIGITS_NAME, string.hexdigits)
    add_terminal_class_rule(grammar, LETTERS_NAME, string.ascii_letters)
    add_terminal_class_rule(grammar, WHITESPACES_NAME, string.whitespace)
    add_terminal_class_rule(grammar, PUNCTUATIONS_NAME, string.punctuation)
    add_terminal_class_rule(grammar, ALPHANUMERICS_NAME, string.ascii_letters + string.digits)
    add_terminal_class_rule(grammar, PRINTABLE_NAME, string.printable)

    print(grammar.pretty_print())
    return grammar

def main(argv):
    grammar = generate_ebnf_replacement(argv[1])
    print(grammar.sample_positives(10, 3))


if __name__ == "__main__":
    main(sys.argv)
