import glob
import sys
from lark import Lark, Transformer

from ebnf_generator import START_NAME, generate_ebnf, generate_ebnf_v3, generate_ebnf_v4
from ebnf_generator_v5 import generate_ebnf_v5

grammar = None

class TreeToJson(Transformer):
    def string(self, s):
        (s,) = s
        return s[1:-1]

    def number(self, n):
        (n,) = n
        return float(n)

    list = list
    pair = tuple
    dict = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False


def main(argv):
    # takes in three files:
    # - argv[1] is the generalized inputs from the grimoire run (generates rules)
    # - argv[2] is the valid inputs that grimoire generated (generates terminals)
    # - argv[3] is the folder containing strings we want to parse
    global grammar
    grammar = generate_ebnf_v5(argv[1], argv[2])
    parser = Lark(grammar, start=START_NAME, ambiguity='explicit')

    test_strings_dir = argv[3]
    test_files = [f for f in glob.glob(f"{test_strings_dir}/*")]
    num_success = 0
    for test_file in test_files:
        with open(test_file) as f:
            # f here is contains new string
            inp = f.read()
            print(f"input: {inp}")
            try:
                tree = parser.parse(inp)
                print(f"output:\n{tree.pretty()}")
                num_success += 1
            except:
                print(f"! failed to parse!")
            f.close()
    return num_success, len(test_files)


if __name__ == '__main__':
    main(sys.argv)
