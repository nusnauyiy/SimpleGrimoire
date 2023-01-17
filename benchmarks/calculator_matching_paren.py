# referencing Figure of https://publications.cispa.saarland/3101/1/fse2020-mimid.pdf
import sys

def digit(i) :
    return i in "01234567"

def parse_num(s, i):
    n = ''
    while i != len(s) and digit(s[i]):
        n += s[i]
        i = i + 1
    return i, n

def parse_paren(s, i, num_opening_paren):
    assert s[i] == '('
    i, v, n = parse_expr(s, i + 1, num_opening_paren)
    if i == len(s) : raise AssertionError(s, i)
    assert s[i] == ')'
    return i, v, n

def parse_expr(s, i = 0, num_opening_paren = 0):
    expr, is_op = [], True
    while i < len(s):
        c = s[i]
        if digit(c):
            if not is_op: raise AssertionError(s, i)
            i , num = parse_num(s, i)
            expr.append(num)
            is_op = False
        elif c in ['+', '-', '*', '/']:
            if is_op: raise AssertionError(s, i)
            expr.append(c)
            is_op, i = True, i + 1
        elif c == '(':
            if not is_op: raise AssertionError(s, i)
            num_opening_paren = num_opening_paren + 1
            i , cexpr, num_opening_paren = parse_expr(s, i+1, num_opening_paren)
            expr.append(cexpr)
            assert s[i] == ')'
            i = i + 1
            is_op = False
        elif c == ')':
            num_opening_paren = num_opening_paren - 1
            if num_opening_paren < 0: raise AssertionError(s, i, num_opening_paren)
            break
        else: raise AssertionError(s, i)
    if is_op: raise AssertionError(s, i)
    if i >= len(s) and num_opening_paren != 0: raise AssertionError(s, i, num_opening_paren)
    return i, expr, num_opening_paren

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