# Python imports
from exceptions import Exception

#own imports
from definitions import CHESS_ROWS, CHESS_COLS, BLACK, WHITE


class ChessException(Exception):
    pass


class PositionException(ChessException):
    """Position is outside the board.
    """
    pass


class ImpossibleMove(ChessException):
    """Move cannot be made.
    """
    pass


class PlayerException(ChessException):
    """White tries to move on Black's turn or vice versa.
    """
    pass


class PromotionException(Exception):
    """A Pawn should be promoted but we do not know what to make it.

    Programs can try a move, catch this exception, ask the player what
    he wants to make of his pawn and then try the move again with that
    information.
    """
    pass


def position(square):
    """Turn square (A1) into row/col position (0, 0).
    Note: A is the column, 1 is the row.

    The basis is checked by the tests for parseRow and parseCol.
    Let's at least check some corner cases.

    >>> position('A1')
    (0, 0)
    >>> position(u'A1')
    (0, 0)
    >>> position('A8')
    (7, 0)
    >>> position('H1')
    (0, 7)
    >>> position('H8')
    (7, 7)

    The Off the End of the Pier Show.
    >>> position('A0')
    Traceback (most recent call last):
    ...
    PositionException: ...
    >>> position('I4')
    Traceback (most recent call last):
    ...
    PositionException: ...

    """
    first = square[0]
    second = square[1]
    col = parseCol(first)
    row = parseRow(second)
    return (row, col)


def parseCol(input):
    """Turn the input into a col number.

    Some good input.

    >>> parseCol('A')
    0
    >>> parseCol('a')
    0
    >>> parseCol(u'A')
    0
    >>> parseCol('F')
    5
    >>> parseCol('H')
    7

    Some bad input.

    >>> parseCol('I')
    Traceback (most recent call last):
    PositionException: ...
    >>> parseCol(0)
    Traceback (most recent call last):
    PositionException: ...
    """
    try:
        parsed = ord(input.upper()) - ord('A')
    except AttributeError:
        raise PositionException, "Bad input for col; %s" % input
    if not 0 <= parsed < CHESS_COLS:
        raise PositionException, "Col out of range; %s parsed as %d." \
              % (input, parsed)
    return parsed


def parseRow(input):
    """Turn the input into a row number.

    Some good input.

    >>> parseRow(1)
    0
    >>> parseRow(2)
    1
    >>> parseRow(8)
    7

    Some bad input.

    >>> parseRow('A')
    Traceback (most recent call last):
    PositionException: ...
    >>> parseRow(0)
    Traceback (most recent call last):
    PositionException: ...
    """
    try:
        parsed = int(input) - 1
    except ValueError:
        raise PositionException, "Bad input for row; %s" % input
    if not 0 <= parsed < CHESS_ROWS:
        raise PositionException, "Row out of range; %s parsed as %d." \
              % (input, parsed)
    return parsed


def squarify(row, col):
    """Turn row/col position (0, 0) into square (A1).
    Note: A is the column, 1 is the row.

    >>> squarify(0,0)
    'A1'
    >>> squarify(0,7)
    'H1'
    >>> squarify(7,0)
    'A8'
    >>> squarify(7,7)
    'H8'

    The Off the End of the Pier Show.
    >>> squarify(8, 1)
    Traceback (most recent call last):
    ...
    PositionException: ...
    >>> squarify(1, 8)
    Traceback (most recent call last):
    ...
    PositionException: ...

    """
    first = reverseCol(col)
    second = reverseRow(row)
    return first + str(second)


def reverseCol(input):
    """Turn the col index into a user friendly name like 'A'.

    Some good input.

    >>> reverseCol(0)
    'A'
    >>> reverseCol(2)
    'C'
    >>> reverseCol(7)
    'H'

    Some bad input.

    >>> reverseCol(-1)
    Traceback (most recent call last):
    PositionException: ...
    >>> reverseCol(8)
    Traceback (most recent call last):
    PositionException: ...
    >>> reverseCol('A')
    Traceback (most recent call last):
    PositionException: ...
    """
    try:
        parsed = chr(input + ord('A'))
    except TypeError:
        raise PositionException, "Bad input for col; %s" % input
    if not 0 <= input < CHESS_COLS:
        raise PositionException, "Col out of range; %d parsed as %s." \
              % (input, parsed)
    return parsed


def reverseRow(input):
    """Turn the row index (0) into a user friendly row number (1).

    Some good input.

    >>> reverseRow(0)
    1
    >>> reverseRow(2)
    3
    >>> reverseRow(7)
    8

    Some bad input.

    >>> reverseRow(-1)
    Traceback (most recent call last):
    PositionException: ...
    >>> reverseRow(8)
    Traceback (most recent call last):
    PositionException: ...
    >>> reverseRow('A')
    Traceback (most recent call last):
    PositionException: ...
    """
    try:
        parsed = int(input) + 1
    except ValueError:
        raise PositionException, "Bad input for row; %s" % input
    if not 0 < parsed <= CHESS_ROWS:
        raise PositionException, "Row out of range; %s parsed as %d." \
              % (input, parsed)
    return parsed


def squareColour(square):
    """What is the background colour of the square?

    >>> squareColour('A1') == BLACK
    True
    >>> squareColour('A2') == WHITE
    True
    >>> squareColour('A3') == BLACK
    True
    >>> squareColour('B1') == WHITE
    True
    >>> squareColour('H8') == BLACK
    True
    """
    row, col = position(square)
    return positionColour(row, col)


def positionColour(row, col):
    """What is the background colour of the square?
    >>> positionColour(0,0) == BLACK
    True
    >>> positionColour(0,1) == WHITE
    True
    >>> positionColour(1,0) == WHITE
    True
    >>> positionColour(1,1) == BLACK
    True
    >>> positionColour(7,7) == BLACK
    True
    """
    if (row + col) % 2 == 0:
        return BLACK
    else:
        return WHITE
