import string
from abc import ABC, abstractmethod
import random
from typing import Union, List, Dict
from enum import Enum

from util.util import str_to_bytes, bytes_to_str


class Blank(ABC):
    DELETE = 1
    REPLACE = 2
    TYPES = {DELETE, REPLACE}

    @staticmethod
    def get_blank(removed=b"", blank_type: TYPES = DELETE):
        if blank_type not in Blank.TYPES:
            raise TypeError(f"invalid blank type: {blank_type}")
        if blank_type == Blank.DELETE:
            return DeleteBlank(removed)
        if blank_type == Blank.REPLACE:
            return ReplaceBlank(removed)

    def __init__(self, blank_type: TYPES = DELETE, removed: bytes = b""):
        if blank_type not in Blank.TYPES:
            raise TypeError(f"invalid blank type: {blank_type}")
        if removed is None:
            self.removed = b""
        else:
            self.removed = removed
        self.blank_type = blank_type

    def __eq__(self, other):
        if isinstance(other, Blank):
            return self.removed == other.removed and self.blank_type == other.blank_type
        return False

    def __str__(self):
        type_str = 'D' if self.blank_type == Blank.DELETE else 'R'
        return f"{type_str}Blank({self.removed})"

    def append(self, other):
        if isinstance(other, bytes):
            self.removed += other
        elif isinstance(other, str):
            self.removed += str_to_bytes(other)
        elif isinstance(other, Blank):
            self.removed += other.removed

    @abstractmethod
    def pretty_print(self):
        pass

    @abstractmethod
    def to_map(self):
        pass


class DeleteBlank(Blank):
    def __init__(self, removed: bytes = None):
        super().__init__(removed=removed, blank_type=Blank.DELETE)

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed),
            "type": "DELETE"
        }

    def pretty_print(self):
        return ""

    def __eq__(self, other):
        if isinstance(other, DeleteBlank):
            return self.removed == other.removed
        return False


class ReplaceClass(Enum):
    DIGITS, NUMBERS, HEXDIGITS, LETTERS, WHITESPACES, PUNCTUATIONS, ALPHANUMERICS, PRINTABLE = range(8)

    @staticmethod
    def get_char(replace_class: 'ReplaceClass'):
        return {
            ReplaceClass.DIGITS: [string.digits],
            # NUMBERS: [string.digits, "."],
            ReplaceClass.HEXDIGITS: ["abcdefABCDEF", string.digits],
            ReplaceClass.LETTERS: [string.ascii_lowercase, string.ascii_uppercase],
            ReplaceClass.WHITESPACES: [string.whitespace],
            ReplaceClass.PUNCTUATIONS: [string.punctuation],
            ReplaceClass.ALPHANUMERICS: [string.ascii_letters, string.digits],
            ReplaceClass.PRINTABLE: [string.ascii_letters, string.digits, string.whitespace, string.punctuation]
        }[replace_class]

    @staticmethod
    def generate(replace_class: 'ReplaceClass'):
        result = ""
        if replace_class == ReplaceClass.NUMBERS:
            num = random.randint(1, 1000000)
            den = random.randint(1, 1000000)
            result = str(num/den)
        else:
            groups = ReplaceClass.get_char(replace_class)
            for i in range(random.randint(len(groups)*2, len(groups)*10)):
                group = random.choice(groups)
                char = random.choice(group)
                result += char
        return result



class ReplaceBlank(Blank):


    def __init__(self, removed: bytes = None):
        super().__init__(removed=removed, blank_type=Blank.REPLACE)
        self.replacements = set()

        self.optimization_table: Dict[ReplaceClass, List[ReplaceClass]] = {
            ReplaceClass.HEXDIGITS: [ReplaceClass.DIGITS],
            ReplaceClass.ALPHANUMERICS: [ReplaceClass.DIGITS, ReplaceClass.HEXDIGITS, ReplaceClass.LETTERS],
            ReplaceClass.PRINTABLE: [ReplaceClass.ALPHANUMERICS, ReplaceClass.NUMBERS, ReplaceClass.PUNCTUATIONS, ReplaceClass.WHITESPACES]
        }

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed),
            "type": "REPLACE",
            "replacements": self.replacements
        }

    def pretty_print(self):
        return "[_]"

    def __eq__(self, other):
        if isinstance(other, ReplaceBlank):
            return self.removed == other.removed and len(
                self.replacements.symmetric_difference(other.replacements)) == 0
        return False

    def add_replacement(self, replace_class: ReplaceClass):
        self.replacements.add(replace_class)
        self.optimize_replacement()

    def recurse_optimize(self, replace_class):
        if replace_class not in self.optimization_table:
            return
        for child_replace_class in self.optimization_table[replace_class]:
            self.recurse_optimize(child_replace_class)
            self.replacements.remove(child_replace_class)

    def optimize_replacement(self):
        for replace_class in reversed(self.optimization_table):
            if replace_class in self.replacements:
                self.recurse_optimize(replace_class)
