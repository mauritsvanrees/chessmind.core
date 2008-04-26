from definitions import *
from position import position, squarify

def _wantedMovesPossible(piece, start, wanted):
    """Return True only if all wanted squares can be reached by the
    piece when starting from start.

    Help function for testing.
    """
    for target in wanted:
        if not piece.canMove(start, target):
            return False
    return True


def _unwantedMovesNotPossible(piece, start, unwanted):
    """Return True only if all unwanted squares cannot be reached by
    the piece when starting from start.

    Help function for testing.
    """
    for target in unwanted:
        if piece.canMove(start, target):
            return False
    return True


class Piece(object):
    """Base class for pieces (King, Queen, etc).

    A piece should at least be printable.

    >>> piece = Piece()
    >>> str(piece)
    '.'
    >>> print piece
    .

    """
    name = ''
    value = 0
    symbol = '.'
    max_moves = 0
    number = 0

    def __init__(self, colour=PLAIN):
        self.colour = colour

    def __str__(self):
        if self.colour == WHITE:
            return self.symbol.upper()
        elif self.colour == BLACK:
            return self.symbol.lower()
        else:
            return self.symbol

    def afterMove(self, **kwargs):
        """Method called after a piece has moved.
        Can be overwritten by pieces that need special handling,
        like castling.
        """
        pass

    def isWhite(self):
        return self.colour == WHITE

    def isBlack(self):
        return self.colour == BLACK

    def isEmpty(self):
        return self.colour == PLAIN

    def isEnemy(self, other):
        """

        First we create some pieces.

        >>> white = Piece(colour=WHITE)
        >>> black = Piece(colour=BLACK)
        >>> empty = Empty()

        I am not an enemy of myself.

        >>> white.isEnemy(white)
        False
        >>> black.isEnemy(black)
        False
        >>> empty.isEnemy(empty)
        False

        Noone is an enemy of an empty square.

        >>> white.isEnemy(empty)
        False
        >>> black.isEnemy(empty)
        False

        Is an empty square anyone's enemy?

        >>> empty.isEnemy(white)
        False
        >>> empty.isEnemy(black)
        False

        White and black are mutual enemies.

        >>> white.isEnemy(black)
        True
        >>> black.isEnemy(white)
        True

        """
        if self.isEmpty() or other.isEmpty():
            return False
        return self.colour != other.colour

    def isKing(self):
        return self.name == 'King'

    def isQueen(self):
        return self.name == 'Queen'

    def isRook(self):
        return self.name == 'Rook'

    def isBishop(self):
        return self.name == 'Bishop'

    def isKnight(self):
        return self.name == 'Knight'

    def isPawn(self):
        return self.name == 'Pawn'

    def castlingMoves(self, start):
        # By default, a piece cannot castle.
        # Overwrite for King and possibly Rook.
        return []

    def canMove(self, start, target):
        """Can the piece legally move from start square to target,
        provided there are no obstacles?
        """
        for direction in self.possibleMoves(start):
            if target in direction:
                return True
        return False

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        return []

    def upDownMoves(self, row, col, max=None, direction=1):
        """List possible forward moves.
        """
        moves = []
        count = 0
        max = max or self.max_moves or CHESS_ROWS
        while count < max:
            count += 1
            row += direction
            if 0 <= row < CHESS_ROWS:
                moves.append(squarify(row, col))
            else:
                break
        return moves

    def forwardMoves(self, row, col, max=None):
        """List possible forward moves.
        """
        return self.upDownMoves(row, col, max=max, direction=1)

    def backwardMoves(self, row, col, max=None):
        """List possible backward moves.
        """
        return self.upDownMoves(row, col, max=max, direction=-1)

    def sideWaysMoves(self, row, col, direction=1):
        """List possible sideways moves.
        """
        moves = []
        count = 0
        while count < CHESS_COLS:
            count += 1
            col += direction
            if 0 <= col < CHESS_COLS:
                moves.append(squarify(row, col))
            else:
                break
        return moves

    def leftMoves(self, row, col):
        """List possible left moves.
        """
        return self.sideWaysMoves(row, col, direction=-1)

    def rightMoves(self, row, col, max=None):
        """List possible right moves.
        """
        return self.sideWaysMoves(row, col, direction=1)

    def diagonalMoves(self, startrow, startcol):
        """List possible diagonal moves.
        """
        directions = []

        # Go to the top left.
        row = startrow
        col = startcol
        direction = []
        while row < 7 and col > 0:
            row += 1
            col -= 1
            direction.append(squarify(row, col))
        if len(direction) > 0:
            directions.append(direction)

        # Go to the top right.
        row = startrow
        col = startcol
        direction = []
        while row < 7 and col < 7:
            row += 1
            col += 1
            direction.append(squarify(row, col))
        if len(direction) > 0:
            directions.append(direction)

        # Go to the bottom right.
        row = startrow
        col = startcol
        direction = []
        while row > 0 and col < 7:
            row -= 1
            col += 1
            direction.append(squarify(row, col))
        if len(direction) > 0:
            directions.append(direction)

        # Go to the bottom left.
        row = startrow
        col = startcol
        direction = []
        while row > 0 and col > 0:
            row -= 1
            col -= 1
            direction.append(squarify(row, col))
        if len(direction) > 0:
            directions.append(direction)

        return directions

    def attackMoves(self, start):
        """Return list of squares that can be attacked.  This only
        lists squares that cannot be reached by normal movement.  In
        other words: only for a pawn this would return anything.
        """
        return []

    def isEnPassantTarget(self):
        # Overwrite for Pawn.
        return False

class Empty(Piece):
    """Empty square

    >>> piece = Empty()
    >>> str(piece)
    '.'
    >>> print piece
    .
    >>> piece.isEmpty()
    True

    """
    name = 'Empty'
    value = 0
    symbol = '.'
    max_moves = 0
    number = 0

    def canMove(self, start, target):
        return False

    def possibleMoves(self, start):
        return [[]]


class King(Piece):
    """The King piece.  Do not lose this one! ;-)

    >>> piece = King(WHITE)
    >>> str(piece)
    'K'
    >>> print piece
    K

    >>> start = 'E1'
    >>> piece.possibleMoves(start)
    [['D2'], ['E2'], ['F2'], ['F1'], ['D1']]


    >>> piece.castlingMoves(start)
    ['C1', 'G1']

    After the King has moved once, it should not have the castling
    moves anymore.

    >>> piece.afterMove()
    >>> piece.castlingMoves(start)
    []

    >>> start = 'E3'
    >>> wanted = ('D4', 'E4', 'F4', 'F3', 'F2', 'E2', 'D2', 'D3')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('E1', 'E5', 'G3')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'B1'
    >>> piece.possibleMoves(start)
    [['A2'], ['B2'], ['C2'], ['C1'], ['A1']]

    """

    name = 'King'
    value = 1000
    symbol = 'K'
    max_moves = 1
    number = 1

    def __init__(self, colour=PLAIN):
        super(King, self).__init__(colour=colour)
        # Set this to False after the King has moved
        self.can_castle = True

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        row, col = position(start)
        directions = []
        # Go round the clock starting at the top left
        if row < 7:
            if col > 0:
                directions.append([squarify(row+1, col-1)])
            directions.append([squarify(row+1, col)])
            if col < 7:
                directions.append([squarify(row+1, col+1)])
        # Try to move right
        if col < 7:
            directions.append([squarify(row, col+1)])
        # Try the three bottom moves
        if row > 0:
            if col < 7:
                directions.append([squarify(row-1, col+1)])
            directions.append([squarify(row-1, col)])
            if col > 0:
                directions.append([squarify(row-1, col-1)])
        # Try to move left
        if col > 0:
            directions.append([squarify(row, col-1)])
        return directions


    def castlingMoves(self, start):
        # Note: make sure that D1-C1 is not interpreted as a castling
        # move.
        directions = []
        # Castling:
        if self.can_castle:
            if self.colour == WHITE and start == 'E1':
                directions.append('C1')
                directions.append('G1')
            elif self.colour == BLACK and start == 'E8':
                directions.append('C8')
                directions.append('G8')
        return directions

    def afterMove(self, **kwargs):
        self.can_castle = False


class Queen(Piece):
    """The Queen.

    >>> piece = Queen()
    >>> start = 'D1'
    >>> piece.possibleMoves(start)[0]
    ['D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']
    >>> piece.possibleMoves(start)[1]
    ['C1', 'B1', 'A1']
    >>> piece.possibleMoves(start)[2]
    ['E1', 'F1', 'G1', 'H1']
    >>> piece.possibleMoves(start)[3]
    ['C2', 'B3', 'A4']
    >>> piece.possibleMoves(start)[4]
    ['E2', 'F3', 'G4', 'H5']
    >>> piece.possibleMoves(start)[5]
    Traceback (most recent call last):
    IndexError: list index out of range

    >>> vertical_wanted = ('D2', 'D3', 'D8')
    >>> _wantedMovesPossible(piece, start, vertical_wanted)
    True

    >>> diagonal_wanted = ('C2', 'B3', 'A4', 'E2', 'F3', 'G4', 'H5')
    >>> _wantedMovesPossible(piece, start, diagonal_wanted)
    True

    >>> horizontal_wanted = ('A1', 'B1', 'C1', 'E1', 'F1', 'G1', 'H1')
    >>> _wantedMovesPossible(piece, start, diagonal_wanted)
    True

    >>> unwanted = ('B2', 'C3', 'E3', 'F2')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'D4'
    >>> vertical_wanted = ('D1', 'D2', 'D3', 'D5', 'D6', 'D7', 'D8')
    >>> _wantedMovesPossible(piece, start, vertical_wanted)
    True

    >>> diagonal_forward_wanted = ('C5', 'B6', 'A7', 'E5', 'F6', 'G7', 'H8')
    >>> _wantedMovesPossible(piece, start, diagonal_forward_wanted)
    True

    >>> diagonal_backward_wanted = ('C3', 'B2', 'A1', 'E3', 'F2', 'G1')
    >>> _wantedMovesPossible(piece, start, diagonal_backward_wanted)
    True

    >>> unwanted = ('B3', 'B5', 'C6', 'E6', 'F5', 'F3', 'E2', 'C2')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    A Queen has no special attack moves like a pawn.

    >>> piece.attackMoves('E4')
    []
    """

    name = 'Queen'
    value = 9
    symbol = 'Q'
    max_moves = None
    number = 1

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        row, col = position(start)
        directions = []
        directions.append(self.forwardMoves(row, col))
        directions.append(self.backwardMoves(row, col))
        directions.append(self.leftMoves(row, col))
        directions.append(self.rightMoves(row, col))
        directions.extend(self.diagonalMoves(row, col))
        directions = [dir for dir in directions if len(dir) > 0]
        return directions


class Rook(Piece):
    """The Rook.

    >>> piece = Rook()
    >>> start = 'A1'
    >>> piece.possibleMoves(start)[0]
    ['A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
    >>> piece.possibleMoves(start)[1]
    ['B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1']

    >>> wanted = ('A2', 'A4', 'A8', 'B1', 'H1')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('B2', 'E8')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'H8'
    >>> wanted = ('H7', 'H4', 'H1', 'G8', 'A8')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('G7', 'E1')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True


    """

    name = 'Rook'
    value = 5
    symbol = 'R'
    max_moves = None
    number = 2

    def __init__(self, colour=PLAIN, can_castle=True):
        super(Rook, self).__init__(colour=colour)
        # Set this to False after the Rook has moved.
        # When a pawn is promoted to Rook, also make it False.
        self.can_castle = can_castle

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        row, col = position(start)
        directions = []
        directions.append(self.forwardMoves(row, col))
        directions.append(self.backwardMoves(row, col))
        directions.append(self.leftMoves(row, col))
        directions.append(self.rightMoves(row, col))
        directions = [dir for dir in directions if len(dir) > 0]
        return directions

    def afterMove(self, **kwargs):
        self.can_castle = False


class Bishop(Piece):
    """The Bishop.

    >>> piece = Bishop()
    >>> start = 'C1'
    >>> piece.possibleMoves(start)
    [['B2', 'A3'], ['D2', 'E3', 'F4', 'G5', 'H6']]

    >>> wanted = ('B2', 'A3', 'D2', 'E3', 'F4', 'G5', 'H6')
    >>> _wantedMovesPossible(piece, start, wanted)
    True


    >>> unwanted = ('B1', 'B3', 'C2', 'C3', 'D1', 'D3')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'C8'
    >>> wanted = ('B7', 'A6', 'D7', 'E6', 'F5', 'G4', 'H3')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('B8', 'B6', 'C7', 'C6', 'D8', 'D6')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True
    """

    name = 'Bishop'
    value = 3
    symbol = 'B'
    max_moves = None
    number = 2

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        row, col = position(start)
        return self.diagonalMoves(row, col)


class Knight(Piece):
    """The Knight.

    >>> piece = Knight()
    >>> start = 'B1'
    >>> piece.possibleMoves(start)
    [['A3'], ['C3'], ['D2']]

    >>> wanted = ('A3', 'C3', 'D2')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('B2', 'D3', 'D1')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'E3'
    >>> wanted = ('D5', 'F5', 'G4', 'G2', 'F1', 'D1', 'C2', 'C4')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('D4', 'E4', 'F4', 'F3', 'F2', 'E2', 'D2', 'D3')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    >>> start = 'H8'
    >>> piece.possibleMoves(start)
    [['G6'], ['F7']]

    >>> wanted = ('F7', 'G6')
    >>> _wantedMovesPossible(piece, start, wanted)
    True

    >>> unwanted = ('F8', 'G8', 'G7', 'H7', 'H6')
    >>> _unwantedMovesNotPossible(piece, start, unwanted)
    True

    """

    name = 'Knight'
    value = 3
    symbol = 'N'
    max_moves = 1
    number = 2

    def possibleMoves(self, start):
        """Return list of possible moves.

        Each item is itself a list of moves in one direction.        
        """
        row, col = position(start)
        directions = []
        # Go round the clock starting with the two top moves
        if row < 6:
            if col > 0:
                directions.append([squarify(row+2, col-1)])
            if col < 7:
                directions.append([squarify(row+2, col+1)])
        # Try the two right moves
        if col < 6:
            if row < 7:
                directions.append([squarify(row+1, col+2)])
            if row > 0:
                directions.append([squarify(row-1, col+2)])
        # Try the two bottom moves
        if row > 1:
            if col < 7:
                directions.append([squarify(row-2, col+1)])
            if col > 0:
                directions.append([squarify(row-2, col-1)])
        # Try the two left moves
        if col > 1:
            if row > 0:
                directions.append([squarify(row-1, col-2)])
            if row < 7:
                directions.append([squarify(row+1, col-2)])

        return directions


class Pawn(Piece):
    """The pawn.

    >>> white_pawn = Pawn(colour=WHITE)
    >>> white_pawn.possibleMoves('E3')
    [['E4']]

    >>> white_pawn.possibleMoves('E2')
    [['E3', 'E4']]

    And now a black pawn.

    >>> black_pawn = Pawn(colour=BLACK)
    >>> black_pawn.possibleMoves('E6')
    [['E5']]

    >>> black_pawn.possibleMoves('E7')
    [['E6', 'E5']]

    Now let's check which squares we can attack.  This would need an
    opponent piece at that spot, but only the board knows if that is
    the case, so we do not worry about that here.  For the same
    reason, we do not take en passant into account.

    >>> white_pawn.attackMoves('E2')
    [('D3', 'D2'), ('F3', 'F2')]
    >>> black_pawn.attackMoves('E7')
    [('D6', 'D7'), ('F6', 'F7')]

    A white pawn at the top row should never happen as it should
    promote then.  But what if we have not implemented that yet?  Same
    for black.
    
    >>> white_pawn.attackMoves('E8')
    []
    >>> black_pawn.attackMoves('E1')
    []

    A white pawn can also not be at the first row.  Neither can the
    black pawn be at the last row.  But we do not really care here.

    >>> white_pawn.attackMoves('A1')
    [('B2', 'B1')]
    >>> black_pawn.attackMoves('H8')
    [('G7', 'G8')]

    """

    name = 'Pawn'
    value = 1
    symbol = 'P'
    max_moves = 1
    number = 8

    def __init__(self, colour):
        super(Pawn, self).__init__(colour=colour)
        # Set this to True for one turn when the pawn is in a position
        # to be hit in passing by the opponent.
        self.can_be_en_passant_target = False

    def isEnPassantTarget(self):
        return self.can_be_en_passant_target

    def resetEnPassantTarget(self):
        self.can_be_en_passant_target = False

    def afterMove(self, **kwargs):
        startrow, temp = position(kwargs['start'])
        targetrow, temp = position(kwargs['target'])
        if abs(startrow - targetrow) == 2:
            self.can_be_en_passant_target = True

    def possibleMoves(self, start):
        """Make list of possible moves.
        """
        row, col = position(start)
        directions = []
        if self.colour == WHITE:
            if row == 1:
                max = 2
            else:
                max = 1
            directions.append(self.forwardMoves(row, col, max=max))
        if self.colour == BLACK:
            if row == 6:
                max = 2
            else:
                max = 1
            directions.append(self.backwardMoves(row, col, max=max))
        return directions

    def attackMoves(self, start):
        """Return list of square that this pawn can attack.
        Also return the matching squares that can be an en passant target.
        """
        row, col = position(start)
        directions = []
        if self.colour == WHITE and row < 7:
            if col > 0:
                target = squarify(row+1, col-1)
                en_passant = squarify(row, col-1)
                directions.append((target, en_passant))
            if col < 7:
                target = squarify(row+1, col+1)
                en_passant = squarify(row, col+1)
                directions.append((target, en_passant))
        if self.colour == BLACK and row > 0:
            if col > 0:
                target = squarify(row-1, col-1)
                en_passant = squarify(row, col-1)
                directions.append((target, en_passant))
            if col < 7:
                target = squarify(row-1, col+1)
                en_passant = squarify(row, col+1)
                directions.append((target, en_passant))
        return directions

# Map piece symbols to piece classes
PieceClasses = (King, Queen, Rook, Bishop, Knight, Pawn, Empty)
piecemap = {}
for klass in PieceClasses:
    piecemap[klass.symbol] = klass

# Map symbols to (lowercase) names for promotion pieces
PromotionClasses = (Queen, Rook, Bishop, Knight)
promotionmap = {}
for klass in PromotionClasses:
    promotionmap[klass.symbol] = klass.name.lower()

# Map piece symbols to the number of those pieces at the start of a
# game.
piece_numbers_list = []
for klass in PieceClasses:
    piece_numbers_list.append((klass.symbol, klass.number))

