from typing import Union

from util.util import str_to_bytes, bytes_to_str


class Blank:
    def __init__(self, removed: bytes = None):
        if removed is None:
            self.removed = b""
        else:
            self.removed = removed
        pass

    def __eq__(self, other):
        if isinstance(other, Blank):
            return self.removed == other.removed
        return False

    def __str__(self):
        return f"Blank({self.removed})"

    def append(self, other):
        if isinstance(other, bytes):
            self.removed += other
        elif isinstance(other, str):
            self.removed += str_to_bytes(other)
        elif isinstance(other, Blank):
            self.removed += other.removed

    def to_map(self):
        return {
            "removed": bytes_to_str(self.removed)
        }
