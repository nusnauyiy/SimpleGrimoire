from abc import ABC, abstractmethod
from typing import Union, List, Dict

from models.ReplaceClass import ReplaceClass
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
        return "[_]"

    def __eq__(self, other):
        if isinstance(other, DeleteBlank):
            return self.removed == other.removed
        return False


class ReplaceBlank(Blank):


    def __init__(self, removed: bytes = None):
        super().__init__(removed=removed, blank_type=Blank.REPLACE)
        self.replacements = set()

        self.optimization_table: Dict[ReplaceClass, List[ReplaceClass]] = {
            ReplaceClass.HEXDIGIT: [ReplaceClass.DIGIT],
            ReplaceClass.ALPHANUMERIC: [ReplaceClass.DIGIT, ReplaceClass.HEXDIGIT, ReplaceClass.LETTER],
            ReplaceClass.PRINTABLE: [ReplaceClass.ALPHANUMERIC, ReplaceClass.DIGIT, ReplaceClass.HEXDIGIT, ReplaceClass.PUNCTUATION, ReplaceClass.WHITESPACE]
        }

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed),
            "type": "REPLACE",
            "replacements": [replace_class.name for replace_class in self.replacements]
        }

    def pretty_print(self):
        return "[+]"

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
