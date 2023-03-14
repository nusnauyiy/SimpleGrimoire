"""
Referencing grammar.py from https://github.com/neil-kulkarni/arvada
Some code snippets used directly with permission from Caroline Lemieux.
"""
import random
import re

from lark import Lark


class Grammar():
    def __init__(self, start):
        self.start = start
        self.rules = {}

    def add_rule(self, rule):
        self.rules[rule.name] = rule

    def __str__(self):
        return '\n'.join([str(rule) for rule in self.rules.values()])

    def pretty_print(self):
        return '\n'.join([rule.pretty_print() for rule in self.rules.values()])

    def parser(self):
        return Lark(str(self), start=self.start, ambiguity='explicit')

    def sample_positives(self, n, max_depth):
        samples = set()
        attempts = 0
        while len(samples) < n and attempts < 10 * n:
            attempts += 1
            try:
                sample = self.generate_positive_example(max_depth)
                if len(sample) > 1000:
                    continue
                samples.add(sample)
            except RecursionError:
                continue
        return samples

    def generate_positive_example(self, max_depth, start_nonterminal='start', cur_depth=0):
        """
        Samples a random positive example from the grammar, with max_depth as much as possible.
        """

        # Helper function: gets all the nonterminals for a body
        def body_nonterminals(grammar, body):
            nonterminals = []
            for item in body:
                if item in grammar.rules:
                    nonterminals.append(item)
            return nonterminals
        def unescape_regex(terminal):
            return re.sub(r'\\(.)', r'\1', re.sub('^/|/$', '', terminal))
        # print(f"cur_depth={cur_depth}")
        # print("1")
        bodies = self.rules[start_nonterminal].bodies
        # If we've reached the max depth, try to choose a non-recursive rule.
        # print("2")
        if cur_depth >= max_depth:
            terminal_bodies = [body for body in bodies if len(body_nonterminals(self, body)) == 0]
            if len(terminal_bodies) == 0: #hardcode for now :(
                terminal_bodies = self.rules["terminal"].bodies
            terminal_body = terminal_bodies[random.randint(0, len(terminal_bodies) - 1)]

            return "".join([unescape_regex(elem) for elem in terminal_body]) # referencing https://mentaljetsam.wordpress.com/2007/04/13/unescape-a-python-escaped-string/
        body_to_expand = bodies[random.randint(0, len(bodies) - 1)]
        # print(f"body to expand={body_to_expand}")
        nonterminals_to_expand = body_nonterminals(self, body_to_expand)
        # print(f"nonterminals_to_expand={nonterminals_to_expand}")
        expanded_body = [self.generate_positive_example(max_depth, elem, cur_depth + 1)
                         if elem in nonterminals_to_expand
                         else unescape_regex(elem) # referencing https://mentaljetsam.wordpress.com/2007/04/13/unescape-a-python-escaped-string/
                         for elem in body_to_expand]
        # print("4")
        return "".join(expanded_body)

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