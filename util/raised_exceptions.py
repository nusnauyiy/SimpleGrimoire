import ast
import sys


class ExceptionsVisitor(ast.NodeVisitor):
    def visit_Module(self, node: ast.Module):
        self.exceptions = set()
        self.generic_visit(node)
        return self.exceptions

    def visit_Raise(self, node: ast.Raise):
        if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
            self.exceptions.add(node.exc.func.id)


def find_raised_exceptions(filename):
    def parse_file(filename):
        with open(filename, "r") as source:
            tree = ast.parse(source.read())
        return tree

    def find_all_raised_exceptions(tree):
        return ExceptionsVisitor().visit(tree)

    tree = parse_file(filename)

    return find_all_raised_exceptions(tree)


def main(argv):
    print(find_raised_exceptions(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
