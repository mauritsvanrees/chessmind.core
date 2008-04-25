#! /usr/bin/env python2.4

import board
import piece
import position
import game

modules = (board, piece, position, game)

def _test():
    import doctest
    import sys
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    verbose = "-v" in sys.argv
    for mod in modules:
        doctest.testmod(mod, verbose=verbose,
                        optionflags=optionflags, report=0)
    doctest.master.summarize()

if __name__ == "__main__":
    _test()

