import sys
from lark import Lark, Transformer

from ebnf_generator import generate_ebnf, START_NAME

grammar = None
# json_grammar = r"""
#     ?value: dict
#           | list
#           | string
#           | SIGNED_NUMBER      -> number
#           | "true"             -> true
#           | "false"            -> false
#           | "null"             -> null
#
#     list : "[" [value ("," value)*] "]"
#
#     dict : "{" [pair ("," pair)*] "}"
#     pair : string ":" value
#
#     string : ESCAPED_STRING
#
#     %import common.ESCAPED_STRING
#     %import common.SIGNED_NUMBER
#     %import common.WS
#     %ignore WS
#     """

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
    grammar = generate_ebnf(argv[1])
    print(grammar)
    # print(json_grammar)
    parser = Lark(grammar, start=START_NAME, ambiguity='explicit')
    with open(sys.argv[2]) as f:
        # f here is contains new string
        tree = parser.parse(f.read()).pretty()
        print(tree)
        # print(TreeToJson().transform(tree))


if __name__ == '__main__':
    main(sys.argv)
