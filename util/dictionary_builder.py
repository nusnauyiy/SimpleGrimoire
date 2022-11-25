import ast
import sys

max_chunk = 10


class ConstantVisitor(ast.NodeVisitor):
    def visit_Module(self, node: ast.Module):
        self.constants = []
        self.generic_visit(node)
        return self.constants

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            self.constants.append(node.value)


def build_dictionary(filename):
    def parse_file(filename):
        with open(filename, "r") as source:
            tree = ast.parse(source.read())
        return tree

    def find_all_const(tree):
        return ConstantVisitor().visit(tree)

    tree = parse_file(filename)

    all_const = find_all_const(tree)
    return [s for const in all_const for s in split_by_n(const, max_chunk)]


def split_by_n(str, n):
    if (len(str) > n):
        return [str[i:i + n] for i in range(0, len(str), n)]
    else:
        return [str]


def main(argv):
    print(build_dictionary(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
