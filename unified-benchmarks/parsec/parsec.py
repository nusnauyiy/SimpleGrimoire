import string
import json
import sys
import myparsec as pyparsec

alphap = pyparsec.char('a')
alphap.tag = 'alphap'
eqp = pyparsec.char('=')
eqp.tag = 'eqp'
digitp = pyparsec.digits
digitp.tag = 'digitp'
abcparser = pyparsec.word >> eqp >> digitp
abcparser.tag = 'abcparser'

def main(arg):
    v = abcparser.parse(arg)
    if isinstance(v, pyparsec.Left):
        # raise Exception('parse failed')
        sys.exit(1)
    return v
