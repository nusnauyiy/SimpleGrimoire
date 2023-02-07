"""
Referencing grammar.py from https://github.com/neil-kulkarni/arvada
"""

class Grammar():
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def __str__(self):
        return '\n'.join([str(rule) for rule in self.rules])

    def pretty_print(self):
        return '\n'.join([rule.pretty_print() for rule in self.rules])

class Rule():
    def __init__(self, name):
        self.name = name
        self.bodies = []

    def add_body(self, body):
        self.bodies.append(body)
        return self

    def __str__(self):
        res = f"{self.name}: "
        res += " | ".join([" ".join(body) for body in self.bodies])
        return res

    def pretty_print(self):
        return self.__str__().replace("|", "\n  |")