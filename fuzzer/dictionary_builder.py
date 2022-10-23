import ast
import sys

class ConstantVisitor(ast.NodeVisitor):
  def visit_Module(self, node: ast.Module):
    self.constants = set()
    self.generic_visit(node)
    return self.constants
  def visit_Constant(self, node: ast.Constant):
    if isinstance(node.value, str):
      self.constants.add(node.value)

def build_dictionary(filename):
    def parse_file(filename):
        with open(filename, "r") as source:
            tree = ast.parse(source.read())
        return tree

    def find_all_const(tree):
        return ConstantVisitor().visit(tree)

    tree = parse_file(filename)

    return find_all_const(tree)

def main(argv):
  print(build_dictionary(argv[1]))

if __name__ == "__main__":
  main(sys.argv)