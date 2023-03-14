import sys

from new_benchmarks.pyparsec import pyparsec

alphaP = pyparsec.letters
alphaP.tag = 'alphaP'

digitP = pyparsec.digits
digitP.tag = 'digitP'

quoteP = pyparsec.char('"')
quoteP.tag = 'quoteP'
stringP = quoteP >> pyparsec.many(alphaP | digitP | pyparsec.whitespace) >> quoteP
stringP.tag = 'stringP'

idP = pyparsec.letter >> pyparsec.many(alphaP | digitP)
idP.tag = 'idP'

atomP = idP | digitP | stringP
atomP.tag = 'atomP'

openP = pyparsec.char('(')
closeP = pyparsec.char(')')
listP = pyparsec.forward(lambda: openP >> pyparsec.sep_by(pyparsec.whitespace, pyparsec.many(sexprP)) >> closeP)
listP.tag = 'listP'
sexprP = (atomP |  listP)
sexprP.tag = 'sexprP'


def main(arg):
    v = sexprP.parse(arg)
    if isinstance(v, pyparsec.Left):
        # raise Exception('parse failed')
        sys.exit(1)
    return v

if __name__== "__main__":
    f = open(sys.argv[1], "r")
    main(f.read())

def test_one_input(input_data: bytes):
    try:
        input_str = input_data.decode("UTF-8")
        v = sexprP.parse(input_str)
        if isinstance(v, pyparsec.Left):
            # Invalid input, but not a bug
            pass
    except ValueError:
        pass
