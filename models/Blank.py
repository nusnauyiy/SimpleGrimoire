from abc import ABC, abstractmethod
import random
from typing import Union, List

from util.util import str_to_bytes, bytes_to_str


class Blank(ABC):
    DELETE = 1
    REPLACE = 2
    TYPES = {DELETE, REPLACE}

    @staticmethod
    def get_blank(removed=None, blank_type: TYPES = DELETE):
        if blank_type not in Blank.TYPES:
            raise TypeError(f"invalid blank type: {blank_type}")
        if blank_type == Blank.DELETE:
            return DeleteBlank(removed)
        if blank_type == Blank.REPLACE:
            return ReplaceBlank(removed)

    def __init__(self, blank_type: TYPES = DELETE, removed: bytes = None):
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


class ReplaceBlank(Blank):
    DIGITS, NUMBERS, LETTERS, ALPHANUMERICS = range(4)
    TYPES = {DIGITS, NUMBERS, LETTERS, ALPHANUMERICS}

    def __init__(self, removed: bytes = None):
        super().__init__(removed=removed, blank_type=Blank.REPLACE)
        self.replacements = []

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed),
            "type": "REPLACE",
            "replacements": self.replacements
        }

    def pretty_print(self):
        return "[_]"
