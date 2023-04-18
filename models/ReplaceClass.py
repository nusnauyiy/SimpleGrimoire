import string
import random
from enum import Enum
from util.string_sampler import generate_real_number_str, generate


class ReplaceClass(Enum):
    DIGIT, HEXDIGIT, LETTER, WHITESPACE, PUNCTUATION, ALPHANUMERIC, PRINTABLE = range(7)

    @staticmethod
    def get_enum_value(name: str):
        name = name.lower()
        return {
            "digit": ReplaceClass.DIGIT,
            # "number": ReplaceClass.NUMBER,
            "hexdigit": ReplaceClass.HEXDIGIT,
            "letter": ReplaceClass.LETTER,
            "whitespace": ReplaceClass.WHITESPACE,
            "punctuation": ReplaceClass.PUNCTUATION,
            "alphanumeric": ReplaceClass.ALPHANUMERIC,
            "printable": ReplaceClass.PRINTABLE
        }[name]

    @staticmethod
    def get_lark_class(name: str):
        name = name.lower()
        return {
            "digits": {"name": "INT", "import": "%import common.INT"},
            # "numbers": {"name": "NUMBER", "import": "%import common.NUMBER"},
            "hexdigits": {"name": "HEXDIGIT+", "import": "%import common.HEXDIGIT"},
            "letters": {"name": "LETTER", "import": "%import common.LETTER"},
            "whitespaces": {"name": "WS", "import": "%import common.WS"},
            "punctuations": {"name": r"""/[!"#$%&'()*+,-.\/:;<=>?@[\\]^_`{|}~]/""", "import": ""},
            # https://docs.python.org/3/library/string.html
            "alphanumerics": {"name": "(LETTER | INT)+", "import": "%import common.LETTER\n%import common.INT"},
            "printables": {"name": r"""(LETTER | INT | WS | /[!"#$%&'()*+,-.\/:;<=>?@[\\]^_`{|}~]/)+""",
                          "import": "%import common.LETTER\n%import common.INT\n%import common.WS"}
        }[name]

    @staticmethod
    def get_char(replace_class: 'ReplaceClass'):
        return {
            ReplaceClass.DIGIT: [string.digits],
            # NUMBERS: [string.digits, "."],
            ReplaceClass.HEXDIGIT: ["abcdefABCDEF", string.digits],
            ReplaceClass.LETTER: [string.ascii_lowercase, string.ascii_uppercase],
            ReplaceClass.WHITESPACE: [string.whitespace],
            ReplaceClass.PUNCTUATION: [string.punctuation],
            ReplaceClass.ALPHANUMERIC: [string.ascii_letters, string.digits],
            ReplaceClass.PRINTABLE: [string.ascii_letters, string.digits, string.whitespace, string.punctuation]
        }[replace_class]

    @staticmethod
    def generate(replace_class: 'ReplaceClass'):
        result = ""
        # if replace_class == ReplaceClass.NUMBER:
        #     result = generate_real_number_str()
        # else:
        groups = ReplaceClass.get_char(replace_class)
        length = random.randint(len(groups) * 2, len(groups) * 10)
        result = generate(groups, length)
        return result
