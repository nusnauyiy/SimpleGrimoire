# [(
import string
import sys

def is_digit(i):
    return i in string.digits
    
def parse_num(s,i):
    n = ''
    while s[i:] and is_digit(s[i]):
        n += s[i]
        i = i +1
    return i,n

def parse_paren(s, i):
    assert s[i] == '('
    i, v = parse_expr(s, i+1)
    if s[i:] == '':
        raise Exception(s, i)
    assert s[i] == ')'
    return i+1, v

def parse_expr(s, i = 0):
    expr = []
    is_op = True
    while s[i:]:
        c = s[i]
        if c in string.digits:
            if not is_op: raise Exception(s,i)
            i,num = parse_num(s,i)
            expr.append(num)
            is_op = False
        elif c in ['+', '-', '*', '/']:
            if is_op: raise Exception(s,i)
            expr.append(c)
            is_op = True
            i = i + 1
        elif c == '(':
            if not is_op: raise Exception(s,i)
            i, cexpr = parse_paren(s, i)
            expr.append(cexpr)
            is_op = False
        elif c == ')':
            break
        else:
            raise Exception(s,i)
    if is_op:
        raise Exception(s,i)
    return i, expr

def main(arg):
    try:
        return parse_expr(arg)
    except:
        sys.exit(1)

def test_one_input(input_data: bytes):
    try:
        input_str = input_data.decode("UTF-8")
        parse_expr(input_str)
    except ValueError:
        # Invalid input, but not a bug
        pass

if __name__== "__main__":
    f = open(sys.argv[1], "r")
    main(f.read())
    
# )]
