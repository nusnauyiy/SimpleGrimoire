from typing import List, Union
from models.Blank import Blank

class GeneralizedInput:
    def __init__(self, input: List[Union[bytes, Blank]] = []):
        self.input = input

    # replace all blanks with empty string and return the input as bytes
    def get_bytes(self) -> bytes:
        res: bytes = b""
        for token in self.input:
            if isinstance(token, Blank):
                continue
            res += token
        return res