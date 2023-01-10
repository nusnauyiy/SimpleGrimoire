from copy import copy

from models.Blank import Blank
from util.util import bytes_to_str, str_to_bytes


class GeneralizedInput:
    def __init__(self, input_data=None, is_exploded_data=False):
        if input_data is None:
            input_data = []
        if is_exploded_data:
            self.input = [str_to_bytes(c) if isinstance(c, str) else copy(c) for c in input_data]
            self.merge_adjacent_gaps_and_bytes()
        else:
            self.input = input_data

    def __eq__(self, other):
        if isinstance(other, GeneralizedInput):
            if len(self.input) != len(other.input):
                return False
            for i in range(len(self.input)):
                if self.input[i] != other.input[i]:
                    return False
            return True
        return False

    def __str__(self):
        res = "GeneralizedInput["
        for token in self.input:
            if isinstance(token, bytes):
                res += bytes_to_str(token) + " "
            else:
                res += f"{token} "
        res += "]"
        return res

    # replace all blanks with empty string and return the input as bytes
    def get_bytes(self) -> bytes:
        res: bytes = b""
        for token in self.input:
            if isinstance(token, Blank):
                continue
            res += token
        return res

    def merge_adjacent_gaps_and_bytes(self):
        i = len(self.input) - 1
        while i >= 1:
            elem = self.input[i]
            prev_elem = self.input[i - 1]
            if isinstance(elem, Blank) and isinstance(prev_elem, Blank):
                prev_elem.removed += elem.removed
                del self.input[i]
            elif isinstance(elem, bytes) and isinstance(prev_elem, bytes):
                self.input[i - 1] += elem
                del self.input[i]
            i -= 1

    def to_map(self):
        return {
            "input": [i.to_map() if isinstance(i, Blank) else bytes_to_str(i) for i in self.input]
        }

    def to_exploded_input(self):
        res = []
        for token in self.input:
            if isinstance(token, Blank):
                res.append(token)
            else:
                token_str = bytes_to_str(token)
                for c in token_str:
                    res.append(c)
        return res
