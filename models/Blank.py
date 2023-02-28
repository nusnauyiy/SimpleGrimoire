from typing import Union

from util.util import str_to_bytes, bytes_to_str


class Blank:
    DELETE = 1
    REPLACE = 2
    TYPES = {DELETE, REPLACE}

    def __init__(self, removed: bytes = None, blank_type=DELETE):
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

    def pretty_print(self):
        return "[_]" if self.blank_type == Blank.REPLACE else ""

    def append(self, other):
        if isinstance(other, bytes):
            self.removed += other
        elif isinstance(other, str):
            self.removed += str_to_bytes(other)
        elif isinstance(other, Blank):
            self.removed += other.removed

    def blank_type_str(self):
        if self.blank_type == Blank.DELETE:
            return "DELETE"
        if self.blank_type == Blank.REPLACE:
            return "REPLACE"

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed),
            "type": self.blank_type_str()
        }
