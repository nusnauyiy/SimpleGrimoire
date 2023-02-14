import sys
from typing import List

'''
INPUT = FACE+

FACE := LARM? LCHEEK SPACE* SWEAT? SPACE* LEYE SPACE* MOUTH? SPACE* REYE SPACE* SWEAT? SPACE* RCHEEK RARM?

LARM := '~' | '_' | '\\' | ',' | '-'
RARM := '~' | '_' | '/' | ',' | '-'

LCHEEK := '(' | '[' | '{'
RCHEEK := ')' | ']' | '}'

SWEAT := '"'

LEYE := 'o' | '.' | '-' | '\'' | '=' | ';' | '~'
REYE := 'o' | '.' | '-' | '\'' | '=' | ';' | '~'
MOUTH := 'u' | 'v' | 'w' | '-' | '_' | 'n'
'''

LARM = ['~', '_', '\\', ',', '-']
RARM = ['~', '_', '/', ',', '-']
LCHEEK = ['(', '[', '{']
RCHEEK = [')', ']', '}']
SWEAT = ['"']
LEYE = ['o', '.', '-', '\'', '=', ';', '~']
REYE = ['o', '.', '-', '\'', '=', ';', '~']
MOUTH = ['u', 'v', 'w', '-', '_', 'n']

def parse_helper(input_str: str, i: int) -> List[str]:
    next_token = {"LARM", "LCHEEK"}
    res = []

    while i < len(input_str):
        if "LARM" in next_token:
            if input_str[i] in LARM:
                res.append(input_str[i])
                i += 1
            next_token.remove("LARM")
            continue
        if "LCHEEK" in next_token:
            if input_str[i] not in LCHEEK:
                raise AssertionError(f"invalid next token {input_str[i]}, next={next}")
            res.append(input_str[i])
            i += 1
            next_token.remove("LCHEEK")
            next_token.add("SPACE")
            next_token.add("SWEAT")
            next_token.add("LEYE")
        if "SPACE" in next_token:
            if input_str[i] != " ":
                next_token.remove("SPACE")
            else:
                i += 1
            continue
        if "SWEAT" in next_token:
            if input_str[i] in SWEAT:
                res.append(input_str[i])
                i += 1
            next_token.remove("SWEAT")
            next_token.add("SPACE")
            continue
        if "LEYE" in next_token:
            if input_str[i] not in LEYE:
                raise AssertionError(f"invalid next token {input_str[i]}, next={next}")
            res.append(input_str[i])
            i += 1
            next_token = {"SPACE", "MOUTH", "REYE"}
            continue
        if "MOUTH" in next_token:
            c = input_str[i]
            if c in MOUTH:
                res.append(input_str[i])
                i += 1
            next_token.remove("MOUTH")
            if c in REYE:
                next_token.add("SPACE")
                next_token.add("SWEAT")
                next_token.add("RCHEEK")
            else:
                next_token.add("SPACE")
            continue
        if "REYE" in next_token:
            if input_str[i] not in REYE:
                if "RCHEEK" in next_token:
                    next_token.remove("REYE")
                    continue
                raise AssertionError(f"invalid next token {input_str[i]}, next={next}")
            res.append(input_str[i])
            i += 1
            next_token = {"SPACE", "SWEAT", "RCHEEK"}
            continue
        if "RCHEEK" in next_token:
            if input_str[i] not in RCHEEK:
                raise AssertionError(f"invalid next token {input_str[i]}, next={next}")
            res.append(input_str[i])
            i += 1
            next_token = {"RARM"}
            continue
        if "RARM" in next_token:
            if input_str[i] in RARM:
                res.append(input_str[i])
                i += 1
            next_token = {"LARM", "LCHEEK"}
            continue
        sys.exit(1)
        # raise AssertionError(f"invalid state next={next_token}")

    if "LARM" not in next_token and "RARM" not in next_token:
        # raise AssertionError("invalid face")
        sys.exit(1)
    # return res
    sys.exit(0)

def parse(input_str: str) -> List[str]:
    parse_helper(input_str, 0)


# def test_one_input(input_data: bytes):
#     try:
#         input_str = input_data.decode("UTF-8")
#         return parse(input_str)
#     except ValueError:
#         # Invalid input, but not a bug
#         pass

def main(arg):
    parse(arg)

if __name__== "__main__":
    f = open(sys.argv[1], "r")
    main(f.read())