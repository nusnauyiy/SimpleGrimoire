# [(
import sys

def cgi_decode(s):
    """Decode the CGI-encoded string `s`:
       * replace "+" by " "
       * replace "%xx" by the character with hex number xx.
       Return the decoded string.  Raise `ValueError` for invalid inputs."""

    # Mapping of hex digits to their integer values
    hex_values = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
    }

    t = ""
    i = 0
    while i < len(s):
        c = s[i]
        if c == '+':
            t += ' '
        elif c == '%':
            digit_high, digit_low = s[i + 1], s[i + 2]
            i += 2
            if digit_high in hex_values and digit_low in hex_values:
                v = hex_values[digit_high] * 16 + hex_values[digit_low]
                t += chr(v)
            else:
                # raise ValueError("Invalid encoding")
                sys.exit(1)
        else:
            t += c
        i += 1
    return t
def main(arg):
    cgi_decode(arg.strip())
    sys.exit(0)

def test_one_input(input_data: bytes):
    try:
        input_str = input_data.decode("UTF-8")
        cgi_decode(input_str)
    except ValueError:
        # Invalid input, but not a bug
        pass

if __name__== "__main__":
    f = open(sys.argv[1], "r")
    main(f.read())
# )]
