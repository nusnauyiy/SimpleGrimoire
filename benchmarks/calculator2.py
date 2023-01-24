# referencing Figure of https://publications.cispa.saarland/3101/1/fse2020-mimid.pdf
import sys

from benchmarks.calculator import parse_expr


def test_one_input(input_data: bytes):
    try:
        input_str = input_data.decode("UTF-8")
        parse_expr(input_str)
    except ValueError:
        # Invalid input, but not a bug
        pass

def main(arg):
    return parse_expr(arg)

if __name__== "__main__":
    print(main(sys.argv[1]))