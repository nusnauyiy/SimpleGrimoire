import sys
from lark import Lark, Transformer

from ebnf_generator import generate_ebnf_v2, START_NAME

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
    # takes in two files: first is the generalized inputs that we make the parser from
    # second is the new string we want to parse
    global grammar
    grammar = generate_ebnf_v2(argv[1])
    # print(grammar)
    # print(json_grammar)
    parser = Lark(grammar, start=START_NAME, ambiguity='explicit')
    with open(sys.argv[2]) as f:
        # f here is contains new string
        tree = parser.parse(f.read())
        print(tree)
        print(TreeToJson().transform(tree))


if __name__ == '__main__':
    main(sys.argv)
