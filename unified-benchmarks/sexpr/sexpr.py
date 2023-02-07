import myparsec as pyparsec
import sys
import json

alphaP = pyparsec.letters
alphaP.tag = 'alphaP'

digitP = pyparsec.digits
digitP.tag = 'digitP'

quoteP = pyparsec.char('"')
quoteP.tag = 'quoteP'
stringP = quoteP >> pyparsec.many(alphaP | digitP | pyparsec.whitespace) >> quoteP
stringP.tag = 'stringP'

idP = pyparsec.letter >> pyparsec.many(alphaP|digitP)
idP.tag = 'idP'

atomP = idP | digitP | stringP
atomP.tag = 'atomP'

openP = pyparsec.char('(')
closeP = pyparsec.char(')')
listP = pyparsec.forward(lambda:  openP >> pyparsec.sep_by(pyparsec.whitespace, pyparsec.many(sexprP)) >> closeP)
listP.tag = 'listP'
sexprP = (atomP |  listP)
sexprP.tag = 'sexprP'


def main(arg):
    v = sexprP.parse(arg)
    if isinstance(v, pyparsec.Left):
        # raise Exception('parse failed')
        sys.exit(1)
    return v
