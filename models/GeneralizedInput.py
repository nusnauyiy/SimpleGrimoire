from models.Blank import Blank
from util.util import bytes_to_str


class GeneralizedInput:
    def __init__(self, input_data=None):
        if input_data is None:
            input_data = []
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
                res += "Blank "
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
                del self.input[i]
            elif isinstance(elem, bytes) and isinstance(prev_elem, bytes):
                self.input[i - 1] += elem
                del self.input[i]
            i -= 1

    def to_map(self):
        return {
            "input": [{} if isinstance(i, Blank) else bytes_to_str(i) for i in self.input]
        }
