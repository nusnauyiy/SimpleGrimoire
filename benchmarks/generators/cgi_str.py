"""
A generator of random CGI encoded strings
"""

URL_VALID_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~+"
HEX_DIGITS = "ABCDEFabcdef0123456789"


class ByteBackedRandom:
    """
    Provides an interface for some "random" decisions that are in fact
    influenced by a a byte sequence. 
    """

    def __init__(self, random_bytes):
        self.random_bytes = random_bytes
        self.byte_idx = 0

    def random_byte(self):
        if self.byte_idx < len(self.random_bytes):
            b = self.random_bytes[self.byte_idx]
            self.byte_idx += 1
            return b
        else:
            # When random runs out, return 0. Ideally we should extend with 
            # an arbitrary (but deterministic given the `random_bytes`
            # provided) sequence of bytes 
            return 0

    def random_float_between_0_and_1(self):
        return self.random_byte() / 255

    def random_choice(self, choice_domain):
        choice_idx = self.random_byte() % len(choice_domain)
        return choice_domain[choice_idx]


def generate_valid_cgi_string(random_bytes: bytes) -> str:
    """
    Using `random_bytes` as a source of randomness, generate a random CGI-encoded string.
    """
    bbr = ByteBackedRandom(random_bytes)

    string_len = bbr.random_choice([1, 2, 5, 10, 20, 40, 80])
    ret_string = ""
    for _ in range(string_len):
        # 1/4 of the time, generate a special character:
        if bbr.random_float_between_0_and_1() < 0.25:
            ret_string += "%" + bbr.random_choice(HEX_DIGITS) + bbr.random_choice(HEX_DIGITS)
        else:
            ret_string += bbr.random_choice(URL_VALID_CHARACTERS)
    return ret_string


def generate_cgi_string(random_bytes: bytes) -> str:
    """
    Using `random_bytes` as a source of randomness, generate a random string containing
    only characters that are valid in a CGI string. 
    """

    bbr = ByteBackedRandom(random_bytes)

    string_len = bbr.random_choice([1, 2, 5, 10, 20, 40, 80])
    ret_string = ""
    for _ in range(string_len):
        ret_string += bbr.random_choice(URL_VALID_CHARACTERS + "%")
    return ret_string
