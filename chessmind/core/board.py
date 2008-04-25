#from exceptions import Exception
import logging
import sys
import copy

#Add logging to the console.
log = logging.getLogger('chessmind')
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)-5s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

import piece
import position
from definitions import *

# Some return states 
NORMAL = 0
CASTLING = 1
EN_PASSANT = 2

class Board(object):
    """
    >>> board = Board()
    >>> print board
    3 ...
    2 ...
    1 ...
      ABC

    """
    nrows = ROWS
    ncols = COLS

    def __init__(self):
        self.rows = []
        square = piece.Empty()
        for num in range(self.nrows):
            row = []
            for col in range(self.ncols):
                row.append(square)
            self.rows.append(row)

    def __str__(self):
        lines = ''
        for num in range(self.nrows, 0, -1):
            r = self.rows[num-1]
            line = str(num) + ' '
            for c in r:
                line += str(c)
            line += '\n'
            lines += line
        bottomline = '  ' + reduce(lambda x,y: x + y, self.columnNames())
        lines += bottomline
        return lines

    def columnNames(self):
        line = []
        base = ord('A')
        for num in range(self.ncols):
            line.append(chr(base + num))
        return line

class ChessBoard(Board):
    """

    Let's create a standard chess board.

    >>> board = ChessBoard()
    >>> board.nrows
    8
    >>> board.ncols
    8
    >>> print board
    8 rnbqkbnr
    7 pppppppp
    6 ........
    5 ........
    4 ........
    3 ........
    2 PPPPPPPP
    1 RNBQKBNR
      ABCDEFGH

    We should be able to make copies of this board.  There are several
    options.  Let's use them all and at the end of the tests see what
    the results are

    >>> normal_copy = board
    >>> import copy
    >>> shallow_copy = copy.copy(board)
    >>> deep_copy = copy.deepcopy(board)

    Let us check some squares.

    >>> board['A3'].isEmpty()
    True

    And see if we can set a piece there.

    >>> board['A3'] = piece.Pawn(WHITE)
    >>> board['A3'].isPawn()
    True

    Do we have a white king at E1?
    >>> piece = board['E1']
    >>> piece.colour == WHITE
    True
    >>> piece.name == 'King'
    True

    And do we have a black pawn at G7?

    >>> piece = board['G7']
    >>> piece.colour == BLACK
    True
    >>> piece.name == 'Pawn'
    True

    The white player may start.

    >>> board.player == WHITE
    True
    >>> board.move('E2', 'E4')

    Now the black player may move.

    >>> board.player == BLACK
    True
    >>> board.move('E4', 'E5')
    Traceback (most recent call last):
    PlayerException: ...
    >>> board.move('E7', 'E5')

    And now white may go again.

    >>> board.player == WHITE
    True
    >>> board.move('D2', 'D4')

    We made copies of the board in the beginning.  Let's see what has
    become of them.  We expect the normal and shallow copies to be the
    same as the board is now.

    >>> board == normal_copy
    True
    >>> board == shallow_copy
    False

    The only difference with the shallow copy is that a different
    player is on the move.  Let's check that.

    >>> board.player == BLACK
    True
    >>> shallow_copy.player == WHITE
    True
    >>> board.player = WHITE
    >>> board == shallow_copy
    True

    That is not what we want usually.  But the deep copy should still
    be the same as a fresh chess board, so we can use that if we want
    to copy a board:

    >>> deep_copy == ChessBoard()
    True

    And now we create an empty chess board.

    >>> board = ChessBoard(None)
    >>> board.nrows
    8
    >>> board.ncols
    8
    >>> print board
    8 ........
    7 ........
    6 ........
    5 ........
    4 ........
    3 ........
    2 ........
    1 ........
      ABCDEFGH

    Everything should be empty

    >>> for row in range(board.nrows):
    ...     for col in range(board.ncols):
    ...         if not board[row, col].isEmpty():
    ...             print False

    """
    nrows = CHESS_ROWS
    ncols = CHESS_COLS

    def __init__(self, diagram=CHESS_BOARD):
        self.player = WHITE
        self.rows = []
        if diagram == None:
            diagram = EMPTY_CHESS_BOARD
        self._load(diagram)

    def _load(self, diagram):
        diagram = diagram.strip()
        diagram = diagram.splitlines()
        diagram.reverse()
        assert(len(diagram) == self.nrows)
        for row in diagram:
            assert(len(row) == self.ncols)
            newrow = []
            for col in range(self.ncols):
                sign = row[col]
                newrow.append(self._new_piece(sign))
            self.rows.append(newrow)

    def export(self):
        """Return board as a diagram.

        >>> board1 = ChessBoard()
        >>> exported =  board1.export()
        >>> print exported
        rnbqkbnr
        pppppppp
        ........
        ........
        ........
        ........
        PPPPPPPP
        RNBQKBNR

        Let's use that as input for a new board and check that this
        results in the same board.

        >>> board2 = ChessBoard(exported)
        >>> board1 == board2
        True

        Let's try again with a different board

        >>> board1 = ChessBoard(HINT_BOARD)
        >>> board2 = ChessBoard(board1.export())
        >>> board1 == board2
        True

        """
        diagram = ''
        for num in range(self.nrows, 0, -1):
            row = self.rows[num-1]
            for square in row:
                symbol = square.symbol
                if square.colour == BLACK:
                    symbol = symbol.lower()
                diagram += symbol
            diagram += '\n'
        return diagram

    def _new_piece(self, sign):
        """Return a new chess piece.
        """
        if sign.islower():
            colour = BLACK
        elif sign.isupper():
            colour = WHITE
        else:
            colour = PLAIN
        sign = sign.upper()
        piecesigns = piece.piecemap.keys()
        assert(sign in piecesigns)
        klass = piece.piecemap.get(sign)
        return klass(colour=colour)

    def __cmp__(self, other):
        """Compare two boards.
        Only useful for equality really.
        We can shamelessly use string comparison then.
        Well, we want to check if the same player is next.
        """
        initial = cmp(str(self), str(other))
        if initial == 0:
            return cmp(self.player, other.player)
        return initial

    def switchPlayers(self):
        if self.player == WHITE:
            self.player = BLACK
        else:
            self.player = WHITE
        # Make sure all pawns of the new player are no longer en
        # passant targets.  This seems to best spot to do that.
        for row in range(self.nrows):
            for col in range(self.ncols):
                pawn = self[row, col]
                if pawn.isPawn() and pawn.colour == self.player:
                    pawn.resetEnPassantTarget()

    def __getitem__(self, square):
        """
        >>> board = ChessBoard()
        >>> board['A1'].isRook()
        True
        >>> board['a1'].isRook()
        True
        >>> board[u'A1'].isRook()
        True
        >>> board[0,0].isRook()
        True
        >>> board[7,3].isQueen()
        True
        >>> board['D8'].isQueen()
        True
        >>> board['D9'].isEmpty()
        Traceback (most recent call last):
        PositionException: ...
        >>> board[3,8].isEmpty()
        Traceback (most recent call last):
        PositionException: ...
        """
        # Check if the input is a string, possibly unicode
        if type(square) in (type('A1'), type(u'A1')):
            row, col = position.position(square)
        else:
            row, col = square
        try:
            return self.rows[row][col]
        except IndexError:
            raise position.PositionException, \
                  "Position (%s, %s) out of range." % (row, col)

    def __setitem__(self, square, piece):
        """Put the piece at the target square.

        Let's give the King his proper place.

        >>> king = piece.King(colour=WHITE)
        >>> target = 'E1'
        >>> row, col = position.position(target)
        >>> board = ChessBoard(EMPTY_CHESS_BOARD)
        >>> board[target].isEmpty()
        True
        >>> board[row, col].isEmpty()
        True
        >>> board[target] = king
        >>> board[target].isKing()
        True
        >>> board[row, col].isKing()
        True

        Let's try the same for a bishop, but use row and column
        numbers now.  We put a bishop at C8.

        >>> target = 'C8'
        >>> targetrow = 7
        >>> targetcol = 2
        >>> board[targetrow, targetcol].isEmpty()
        True
        >>> board[target].isEmpty()
        True
        >>> bishop = piece.Bishop()
        >>> board[targetrow, targetcol] = bishop
        >>> board[targetrow, targetcol].isBishop()
        True
        >>> board[target].isBishop()
        True

        Using unicode strings should work as well.
        
        >>> target = u'F5'
        >>> board[target].isEmpty()
        True
        >>> board[target] = piece.Knight()
        >>> board[target].isKnight()
        True

        Let's try to put a King outside the board.

        >>> board['E0'] = king
        Traceback (most recent call last):
        PositionException: ...

        >>> board[8,0] = king
        Traceback (most recent call last):
        PositionException: ...

        """
        # Check if the input is a string, possibly unicode
        if type(square) in (type('A1'), type(u'A1')):
            row, col = position.position(square)
        else:
            row, col = square
        try:
            self.rows[row][col] = piece
        except IndexError:
            raise position.PositionException, \
                  "Position (%s, %s) out of range." % (row, col)

    def empty(self, target):
        """Empty the target square.

        >>> target = 'E1'
        >>> board = ChessBoard()
        >>> board[target].name
        'King'
        >>> board[target].isEmpty()
        False

        Now we remove the King from power.
        >>> board.empty(target)
        >>> board[target].name
        'Empty'
        >>> board[target].isEmpty()
        True

        """
        self[target] = piece.Empty()

    def move(self, start, target, unconditional=False, promotion=False):
        """Move a piece from start to target position.

        Moving a non existing piece (from an empty position) should
        not be possible.

        >>> board = ChessBoard()
        >>> start = 'E3'
        >>> target = 'D4'
        >>> board.move(start, target)
        Traceback (most recent call last):
        PositionException: ...

        We want to move a Pawn from E2 to E4.

        >>> start = 'E2'
        >>> target = 'E4'
        >>> board[start].name
        'Pawn'

        We check that the target square is initially empty.

        >>> board[target].name
        'Empty'

        Then we let him move and check that the start position is now
        empty and that the Pawn is now at the target position.

        >>> board.move(start, target)
        >>> board[start].name
        'Empty'
        >>> board[target].name
        'Pawn'

        We let black move so we can continue testing with white.

        >>> board.move('D7', 'D5')

        What happens when we move a piece onto itself?  Does it self
        destruct?
        >>> start = 'B1'
        >>> target = 'B1'
        >>> board.move(start, target)
        Traceback (most recent call last):
        ImpossibleMove: ...
        >>> board[start].name
        'Knight'

        Try to hit an own piece.

        >>> start = 'D1'
        >>> target = 'D2'
        >>> board.move(start, target)
        Traceback (most recent call last):
        ImpossibleMove: ...

        Try to attack with a pawn

        >>> board.move('E4', 'D5')
        >>> piece = board['D5']
        >>> piece.isPawn() and piece.colour == WHITE
        True

        Now try en passant.  When the pawn does not take the en
        passant bait, the bait will cease to be an en passant target.
        In other words: you can only be an en passant target for one
        turn.

        >>> board.move('C7', 'C5')
        >>> board['C5'].isEnPassantTarget()
        True
        >>> board.move('A2', 'A3')
        >>> board['C5'].isEnPassantTarget()
        False
        >>> board.move('E7', 'E5')
        >>> board['E5'].isEnPassantTarget()
        True
        >>> board.move('D5', 'C6')
        Traceback (most recent call last):
        ImpossibleMove: ...

        E6 *can* be reached with en passant.  E5 should be empty after
        that.

        >>> board.move('D5', 'E6')
        >>> board['E5'].isEmpty()
        True

        Try castling, using our special test board.

        >>> board = ChessBoard(CASTLING_BOARD)
        >>> board.move('E1', 'C1')
        >>> board['C1'].isKing()
        True
        >>> board['D1'].isRook()
        True
        >>> board['A1'].isEmpty()
        True
        >>> board['H1'].isRook()
        True

        This actually works!  Nice. :) So let's try it for the black
        king as well.

        >>> board.move('E8', 'G8')
        >>> board['G8'].isKing()
        True
        >>> board['F8'].isRook()
        True
        >>> board['H8'].isEmpty()
        True
        >>> board['A8'].isRook()
        True


        Now, a pawn should be promoted when we reaches the other
        side.  Let's setup a board for testing that.

        >>> board = ChessBoard(PROMOTION_BOARD)

        The white pawn at C7 can move to C8 and be promoted.  But then
        we need to know if it wants to become a Queen or something
        else.  If not specified, this should raise an exception.

        >>> board.move('C7', 'C8')
        Traceback (most recent call last):
        PromotionException: ...

        Okay, let's try again and make it a Queen.

        >>> board.move('C7', 'C8', promotion='Q')
        >>> board['C7'].isEmpty()
        True
        >>> board['C8'].isQueen()
        True

        Now, a black pawn should not be promoted to a white piece.

        >>> board.move('E2', 'E1', promotion='Q')
        Traceback (most recent call last):
        ImpossibleMove...

        Black decides to promote this pawn to a knight because that
        means white is in check.

        >>> board.move('E2', 'E1', promotion='n')
        >>> board['E2'].isEmpty()
        True
        >>> board['E1'].isKnight()
        True
        >>> board.isInCheck(WHITE)
        True



        """
        mover = self[start]
        instructions = self.validateMove(mover, start, target, unconditional)
        state = instructions['state']
        if state == CASTLING:
            for castle in CASTLE_PAIRS:
                if (castle['colour'] == mover.colour and
                    castle['king_end'] == target):
                    rook = self[castle['rook_start']]
                    self[castle['rook_end']] = rook
                    self.empty(castle['rook_start'])
        if state == EN_PASSANT:
            self.empty(instructions['clear'])
        if self.isPromotion(start, target):
            if not promotion and not unconditional:
                raise position.PromotionException, "Please specify what promotion the pawn at %s should get." % target
            if promotion:
                newPiece = self._new_piece(promotion)
                if newPiece.isEnemy(piece.Piece(colour=self.player)) or newPiece.isEmpty():
                    raise position.ImpossibleMove, "Cannot promote pawn of player %s to %s" % (self.player, promotion)
                else:
                    self[target] = newPiece
        else:
            self[target] = mover
            # Allow piece to do any special handling after moving.
            mover.afterMove(start=start, target=target)
        self.empty(start)
        self.switchPlayers()

    def isPromotion(self, start, target):
        """Return True if this is a promotion move.
        We assume that this is a valid move.

        Start with a nice board for testing promotions.

        >>> board = ChessBoard(PROMOTION_BOARD)

        A Rook moving to the last line is not promoted

        >>> board['A7'].isPawn()
        False
        >>> board.isPromotion('A7', 'A8')
        False

        A pawn that reaches the last line is promoted.

        >>> board['C7'].isPawn()
        True
        >>> board.isPromotion('C7', 'C8')
        True

        A Pawn moving to a different line is not promoted.

        >>> board['D6'].isPawn()
        True
        >>> board.isPromotion('D6', 'D7')
        False
        >>> board['A2'].isPawn()
        True
        >>> board.isPromotion('A2', 'A3')
        False

        For Black it should work as well.

        >>> board['E2'].isPawn()
        True
        >>> board.isPromotion('E2', 'E1')
        True
        >>> board['D3'].isPawn()
        True
        >>> board.isPromotion('D3', 'D2')
        False
        >>> board['B7'].isPawn()
        True
        >>> board.isPromotion('B7', 'B5')
        False

        """
        if self[start].isPawn():
            startrow, startcol = position.position(start)
            if startrow in (1, 6):
                targetrow, targetcol = position.position(target)
                if targetrow in (0, 7):
                    return True
        return False

    def findKing(self, ownColour):
        """Return the square where the King if this colour is.

        Let's do this for the boards that we defined already.

        >>> board = ChessBoard()
        >>> board.findKing(WHITE)
        'E1'
        >>> board.findKing(BLACK)
        'E8'

        >>> board = ChessBoard(EMPTY_CHESS_BOARD)
        >>> board.findKing(WHITE) is None
        True
        >>> board.findKing(BLACK) is None
        True

        >>> board = ChessBoard(CASTLING_BOARD)
        >>> board.findKing(WHITE)
        'E1'
        >>> board.findKing(BLACK)
        'E8'

        >>> board = ChessBoard(ENDGAME_BOARD)
        >>> board.findKing(WHITE)
        'G2'
        >>> board.findKing(BLACK)
        'E8'
        """
        kings = self.findPiece('K', ownColour)
        if len(kings) > 0:
            return kings[0]
        return None

    def isInCheck(self, ownColour=None):
        """Return True when the king of this colour is attacked.
        """
        if ownColour is None:
            ownColour = self.player
        square = self.findKing(ownColour)
        if square is None:
            return False
        return self.isAttacked(ownColour, square)

    def isAttacked(self, ownColour, square):
        """Is the square, owned by ownColour, attacked?

        - Mostly used for the King of course.

        Let's start with a castling board.

        >>> board = ChessBoard(CASTLING_BOARD)

        The white and black kings are safe in their starting
        positions.

        >>> board.isAttacked(WHITE, 'E1')
        False
        >>> board.isAttacked(BLACK, 'E8')
        False

        They are even safe in the squares that they would normally use
        for castling.

        >>> for square in ('D1', 'C1', 'F1', 'G1'):
        ...     if board.isAttacked(WHITE, square):
        ...         print True
        >>> for square in ('D8', 'C8', 'F8', 'G8'):
        ...     if board.isAttacked(BLACK, square):
        ...         print True


        They are not safe when they are at the enemy's last line,
        being attacked by the opposite rooks.

        >>> board.isAttacked(WHITE, 'B8')
        True
        >>> board.isAttacked(BLACK, 'D1')
        True

        Now we add some pieces to the board and see what effect they
        have.  First we add a black knight on E3.  That makes D1 and
        F1 unsafe.

        >>> board['E3'] = piece.Knight(BLACK)
        >>> for square in ('C1', 'E1', 'G1'):
        ...     if board.isAttacked(WHITE, square):
        ...         print True
        >>> board.isAttacked(WHITE, 'D1')
        True
        >>> board.isAttacked(WHITE, 'F1')
        True

        We will attack black with a pawn right in front of the King.
        The King should be safe in his current spot, but he cannot
        move one square to the left or the right.

        >>> board['E7'] = piece.Pawn(WHITE)
        >>> for square in ('C8', 'E8', 'G8'):
        ...     if board.isAttacked(BLACK, square):
        ...         print True
        >>> board.isAttacked(BLACK, 'D8')
        True
        >>> board.isAttacked(BLACK, 'F8')
        True

        """
        king = piece.King(ownColour)
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self[row, col].isEnemy(king):
                    attacker = position.squarify(row, col)
                    moves = self.calcMovesForPiece(attacker, unconditional=True)
                    if square in moves:
                        return True
                    # Take a list of squares (without their en passant
                    # friends) that can be attacked by this piece,
                    # presumably a Pawn if anything ends up in this
                    # list.
                    special = [sq for (sq, ep) in
                               self[attacker].attackMoves(attacker)]
                    if square in special:
                        return True
        return False

    def isMate(self):
        """Check to see if the player is mate.

        That is: if no legel moves can be made.  Still can be
        checkmate or stalemate.

        We have a nice board for checking this.  At first there is no
        mate.

        >>> board = ChessBoard(MATE_BOARD)
        >>> board.isMate()
        False
        >>> board.isCheckMate()
        False
        >>> board.isStaleMate()
        False

        White plays and wins.

        >>> board.move('E5', 'F7')
        >>> board.player == BLACK
        True
        >>> board.isMate()
        True
        >>> board.isCheckMate()
        True
        >>> board.isStaleMate()
        False

        If we look at this from White's point of view, there is no
        mate.

        >>> board.switchPlayers()
        >>> board.isMate()
        False
        >>> board.isCheckMate()
        False
        >>> board.isStaleMate()
        False

        Let's try again, but now with black starting.

        >>> board = ChessBoard(MATE_BOARD)
        >>> board.switchPlayers()
        >>> board.isMate()
        False
        >>> board.isCheckMate()
        False
        >>> board.isStaleMate()
        False

        Black thinks he is smart in getting rid of the white knight.

        >>> board.move('D6', 'E5')
        >>> board.isMate()
        True
        >>> board.isCheckMate()
        False
        >>> board.isStaleMate()
        True

        Oops, that was a stalemate.  Let's give black another chance
        by cheating.

        >>> board.switchPlayers()
        >>> board.move('G3', 'G2')
        >>> board.isMate()
        True
        >>> board.isCheckMate()
        True
        >>> board.isStaleMate()
        False

        """
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self[row, col].colour == self.player:
                    friend = position.squarify(row, col)
                    moves = self.calcMovesForPiece(friend)
                    if len(moves) > 0:
                        return False
                    # Take a list of squares (without their en passant
                    # friends) that can be attacked by this piece,
                    # presumably a Pawn if anything ends up in this
                    # list.
                    special = self.specialAttackMoves(friend)
                    if len(special) > 0:
                        return False
        return True

    def isCheckMate(self):
        """True if the current player is checkmate.

        For tests, see isMate().
        """
        if self.isMate():
            return self.isInCheck()
        return False

    def isStaleMate(self):
        """True if the current player is stalemate.

        For tests, see isMate().
        """
        if self.isMate():
            return not self.isInCheck()
        return False

    def freePath(self, start, target):
        """Return True if there are no pieces between the start and
        target square.  The end points themselves need not be empty.

        At the moment this function is only used for castling, so only
        horizontal moves are taken into account.  So vertical or
        diagonal paths are always clear.

        >>> board = ChessBoard()
        >>> board.freePath('A1', 'A8')
        True
        >>> board.freePath('A1', 'H8')
        True

        What happens if start and target are the same square?  We do
        not care actually.

        >>> board.freePath('A1', 'A1')
        True

        Two direct horizontal neighbours always have a free path
        between them, as there are simply no squares in between.

        >>> board.freePath('A1', 'B1')
        True

        But with one square between them, the path will be blocked.
        >>> board.freePath('B1', 'D1')
        False

        It does not matter whether the end points are empty

        >>> board.empty('B1')
        >>> board.empty('D1')
        >>> board.freePath('B1', 'D1')
        False

        And certainly the King cannot castle in the beginning:
        >>> board.freePath('E1', 'A1')
        False

        Let's check that changing the end points around does not
        matter.

        >>> board.freePath('A1', 'E1')
        False

        We have started clearing a path between the King and the Rook
        already.  Removing one more piece should do it.

        >>> board.empty('C1')
        >>> board.freePath('E1', 'A1')
        True
        >>> board.freePath('A1', 'E1')
        True

        A path in between is now also free.

        >>> board.freePath('B1', 'D1')
        True

        """
        path = self._path(start, target)
        # We do not care about the start and end positions, only
        # intermediate positions.
        expected_free = path[1:-1]
        for square in expected_free:
            if not self[square].isEmpty():
                return False
        return True

        startrow, startcol = position.position(start)
        targetrow, targetcol = position.position(target)
        if startrow != targetrow:
            return False
        if startcol == targetcol:
            e =  "Start (%s) and target (%s) square are the same" % \
                (start, target)
            raise position.ChessException, e
        elif startcol > targetcol:
            direction = -1
        else:
            direction = 1
        while abs(startcol - targetcol) != 1:
            startcol += direction
            if not self[startrow, startcol].isEmpty():
                return False
        return True

    def _path(self, start, target):
        """Return all squares from start up until target.

        >>> board = ChessBoard()
        >>> board._path('A1', 'E1')
        ['A1', 'B1', 'C1', 'D1', 'E1']

        Rearranging is allowed.

        >>> board._path('E1', 'A1')
        ['A1', 'B1', 'C1', 'D1', 'E1']

        Only horizontal paths are taken into account here.

        >>> board._path('E1', 'E8')
        []

        There is a path from you to yourself.

        >>> board._path('E1', 'E1')
        ['E1']
        """
        results = []
        startrow, startcol = position.position(start)
        targetrow, targetcol = position.position(target)
        if startrow != targetrow:
            return results
        if startcol > targetcol:
            temp = startcol
            startcol = targetcol
            targetcol = temp
        while targetcol - startcol > -1:
            results.append(piece.squarify(startrow, startcol))
            startcol += 1
        return results

    def castlingMoves(self, start, unconditional=False):
        """Return possible castling moves for the piece at the start position.
        A King is taken as the piece that takes the lead.  For a Rook
        this function will return an empty list.

        We have a predefined chess board with just Kings and Rooks at
        their normal place.

        >>> board = ChessBoard(CASTLING_BOARD)

        Like we said, Rooks cannot initiate castling.

        >>> board.castlingMoves('A1')
        []
        >>> board.castlingMoves('H1')
        []

        But a King can.

        >>> board.castlingMoves('E1')
        ['C1', 'G1']

        Same goes for the black King.
        First we have to switch players though.

        >>> board.switchPlayers()
        >>> board.castlingMoves('E8')
        ['C8', 'G8']

        The path needs to be clear though.  We block first one, then
        the other castling option for white.

        >>> board.switchPlayers()
        >>> bishop = piece.Bishop(colour=WHITE)
        >>> board['C1'] = bishop
        >>> board.castlingMoves('E1')
        ['G1']
        >>> board['F1'] = bishop
        >>> board.castlingMoves('E1')
        []

        And we do the same for black.

        >>> board.switchPlayers()
        >>> board['F8'] = bishop
        >>> board.castlingMoves('E8')
        ['C8']
        >>> board['C8'] = bishop
        >>> board.castlingMoves('E8')
        []

        Now let's remove those blocks again.

        >>> for square in ('C1', 'F1', 'C8', 'F8'):
        ...     board.empty(square)
        >>> board.switchPlayers()
        >>> board.castlingMoves('E1')
        ['C1', 'G1']
        >>> board.switchPlayers()
        >>> board.castlingMoves('E8')
        ['C8', 'G8']

        When a king is attacked, he cannot castle.

        >>> black_queen = piece.Queen(colour=BLACK)
        >>> board['G3'] = black_queen
        >>> board.switchPlayers()
        >>> board.castlingMoves('E1')
        []

        By putting an own piece between the opposing Queen and our
        King, we can at least let him castle with the Rook at A1.

        >>> board['F2'] = bishop
        >>> board.castlingMoves('E1')
        ['C1']

        Now we also block his attack on G1.

        >>> board['G2'] = bishop
        >>> board.castlingMoves('E1')
        ['C1', 'G1']

        Now white starts annoying black, by also blocking him from
        some castling.

        >>> board.switchPlayers()
        >>> board.castlingMoves('E8')
        ['C8', 'G8']
        >>> board['F6'] = bishop
        >>> board.castlingMoves('E8')
        ['G8']

        When pieces move, they are no longer allowed to castle.

        >>> board.switchPlayers()
        >>> board.move('A1', 'A2')
        >>> board.switchPlayers()
        >>> board.castlingMoves('E1')
        ['G1']

        Move the other white Rook.

        >>> board.move('H1', 'H2')
        >>> board.switchPlayers()
        >>> board.castlingMoves('E1')
        []

        Moving back to the right square should not help.

        >>> board.move('A2', 'A1')
        >>> board.switchPlayers()
        >>> board.move('H2', 'H1')
        >>> board.switchPlayers()
        >>> board.castlingMoves('E1')
        []

        In the case of Black, let's move the king.

        >>> board.switchPlayers()
        >>> board.move('E8', 'F7')
        >>> board.switchPlayers()
        >>> board.castlingMoves('F7')
        []

        Moving the King back to the right square also does not help.

        >>> board.move('F7', 'E8')
        >>> board.castlingMoves('E8')
        []

        """
        king = self[start]
        moves = []
        if not king.isKing():
            return moves
        if not king.can_castle:
            return moves
        for castle in CASTLE_PAIRS:
            if (castle['colour'] == king.colour and
                castle['king_start'] == start):
                if self.castlingAllowed(castle, unconditional):
                    moves.append(castle['king_end'])
        return moves

    def castlingAllowed(self, castle, unconditional=False):
        """Return True if the King perform this castling move.
        If unconditional, we do not care if we end up in check.
        """
        rook_start = castle['rook_start']
        king_start = castle['king_start']
        king_middle = castle['king_middle']
        king_end = castle['king_end']
        rook = self[rook_start]
        king = self[king_start]
        if not (rook.isRook() and rook.can_castle and
                self.freePath(king_start, rook_start)):
            return False
        if unconditional:
            return True
        if self.isInCheck(king.colour):
            return False
        if self.moveCausesCheck(king_start, king_middle):
            return False
        if self.moveCausesCheck(king_start, king_end):
            return False
        return True

    def moveCausesCheck(self, start, target):
        """Test if the move causes the own king to be in check, as
        then we would loose.  If the move is impossible for a
        different reason, we also return True.

        We setup an interesting board.

        >>> board = ChessBoard(ENDGAME_BOARD)

        Is white or black in check currently?

        >>> board.isInCheck(WHITE)
        False
        >>> board.isInCheck(BLACK)
        False

        An impossible move also return True
        The king cannot move to G3, as his own pawn is there.

        >>> board.moveCausesCheck('G2','G3')
        True

        Also, trying to move an empty square is also not allowed.

        >>> board.moveCausesCheck('E1', 'E2')
        True

        The white King can move to F1.

        >>> board.moveCausesCheck('G2','F1')
        False

        But the other squares that the white king can reach, are all
        under attack.

        >>> for square in ('F2', 'F3', 'G1', 'H1', 'H2', 'H3'):
        ...     if not board.moveCausesCheck('G2', square):
        ...         print square

        In other words: F1 is the only safe move for the king.

        >>> board._safeMovesForPiece('G2')
        ['F1']

        The white King decides to stay where he is.  Instead, the
        white Queen moves.  Not a very good move, but there you go.

        >>> board.move('A1', 'C3')

        Now it is black's turn.  The black king cannot move to D8 as
        that square is attacked by the knight.

        >>> board.moveCausesCheck('E8','D8')
        True

        So where *can* that king go?

        >>> board._safeMovesForPiece('E8')
        ['F8', 'F7', 'D7', 'G8']

        """
        board = copy.deepcopy(self)
        colour = board[start].colour
        # First we try the move.  This can cause an exception.
        try:
            board.move(start, target, unconditional=True)
        except position.ChessException:
            return True
        return board.isInCheck(colour)

    def _safeMovesForPiece(self, start):
        """Return the moves for this piece that keep the King safe.
        """
        safe = []
        squares = self.calcMovesForPiece(start)
        for target in squares:
            if not self.moveCausesCheck(start, target):
                safe.append(target)
        safe.extend(self.castlingMoves(start))
        return safe


    def calcMovesForPiece(self, start, unconditional=False):
        """Calculate possible moves for piece, given the state of the board.

        First, let us try castling.  We have a special board for that,
        with just kings and rooks.  But castling is not handled by
        this method, so those moves should not be listed here.

        >>> board = ChessBoard(CASTLING_BOARD)
        >>> start = 'E1'
        >>> board.calcMovesForPiece(start)
        ['D2', 'E2', 'F2', 'F1', 'D1']

        The King cannot move to an attacked square.

        >>> black_knight = piece.Knight(BLACK)
        >>> board['E3'] = black_knight
        >>> board.calcMovesForPiece(start)
        ['D2', 'E2', 'F2']

        But when we try a move unconditionally, it is okay if our own
        King ends up in check.  Presumably this is because our
        unconditional move actually kills the enemy king so we have
        already won then.

        >>> board.calcMovesForPiece(start, unconditional=True)
        ['D2', 'E2', 'F2', 'F1', 'D1']

        Now let's try that with a normal starting board.  Then the
        King cannot move at all.

        >>> board = ChessBoard()
        >>> board.calcMovesForPiece(start)
        []

        A Queen cannot move at first.

        >>> start = 'D1'
        >>> board[start].name
        'Queen'
        >>> len(board.calcMovesForPiece(start))
        0

        A Pawn can move forward.  Let's check that for a black pawn.
        We need to switch players for that first.

        >>> board.switchPlayers()
        >>> start = 'A7'
        >>> len(board.calcMovesForPiece(start))
        2

        It can attack diagonally in one direction.  In this case a
        possible en passant target square is also mentioned.

        >>> board[start].attackMoves(start)
        [('B6', 'B7')]

        When we put an enemy pawn in the right spot, our pawn can
        attack it.

        >>> target = 'B6'
        >>> board[target] = piece.Pawn(colour=BLACK)
        >>> board.specialAttackMoves(start)
        []
        >>> board[target] = piece.Pawn(colour=WHITE)
        >>> board.specialAttackMoves(start)
        [('B6', None)]

        Note: None means that there is no en passant move.

        When we put an enemy piece in front of a pawn, it cannot move.
        Let's use unicode for a change.

        >>> board.switchPlayers()
        >>> start = u'B2'
        >>> len(board.calcMovesForPiece(start))
        2
        >>> board[u'B3'] = piece.Pawn(colour=BLACK)
        >>> len(board.calcMovesForPiece(start))
        0

        A Knight can move too.  He has no special attack moves.

        >>> start = 'G1'
        >>> board.calcMovesForPiece(start)
        ['F3', 'H3']
        >>> len(board.calcMovesForPiece(start))
        2
        >>> board[start].attackMoves(start)
        []

        What if we put a Rook somewhere in the middle?

        >>> start = 'D4'
        >>> rook = piece.Rook(colour=WHITE)
        >>> board[start] = rook
        >>> board.calcMovesForPiece(start)
        ['D5', 'D6', 'D7', 'D3', 'C4', 'B4', 'A4', 'E4', 'F4', 'G4', 'H4']


        I saw something strange that I need to test. If a piece is
        attacking your king, you are not allowed to kill that piece.
        That would be bad, so let's check that.

        >>> board = ChessBoard(EMPTY_CHESS_BOARD)
        >>> board['A1'] = piece.King(WHITE)
        >>> board['B3'] = piece.Queen(WHITE)
        >>> board['A8'] = piece.King(BLACK)
        >>> board['D1'] = piece.Rook(BLACK)
        >>> board.calcMovesForPiece('B3')
        ['B1', 'D1']

        Let's try that with the game where I saw the error.  It is
        Black's move.

        >>> board = ChessBoard(DEFEND_KING_BOARD)
        >>> board.switchPlayers()
        >>> board.calcMovesForPiece('F6')
        ['F8', 'D8']

        """
        thisPiece = self[start]
        king = thisPiece.isKing()
        pawn = thisPiece.isPawn()
        good_moves = []
        directions = thisPiece.possibleMoves(start)
        for direction in directions:
            for move in direction:
                if not unconditional and self.moveCausesCheck(start, move):
                    continue
                target = self[move]
                if target.isEmpty():
                    good_moves.append(move)
                elif target.colour == thisPiece.colour:
                    break
                else:
                    # Enemy piece.  Not good for pawns.
                    if not pawn:
                        good_moves.append(move)
                    break
        return good_moves

    def specialAttackMoves(self, start, unconditional=False):
        # Special attack moves, just for the pawn usually.
        good_moves = []
        thisPiece = self[start]
        for move, en_passant in thisPiece.attackMoves(start):
            if not unconditional and self.moveCausesCheck(start, move):
                continue
            if thisPiece.isEnemy(self[move]):
                good_moves.append((move, None))
            elif thisPiece.isEnemy(self[en_passant]) and \
                 self[en_passant].isEnPassantTarget():
                good_moves.append((move, en_passant))
        return good_moves

    def validateMove(self, mover, start, target, unconditional=False):
        instructions = {'state': NORMAL}
        if start == target:
            raise position.ImpossibleMove, 'Cannot move piece onto itself.'
        if mover is None or mover.name == 'Empty':
            raise position.PositionException, 'Cannot move empty square.'
        if mover.colour != self.player:
            raise position.PlayerException, "%s at %s does not belong to current player (%s)." % (mover.name, start, self.player)
        if target in self.castlingMoves(start, unconditional):
            instructions['state'] = CASTLING
            return instructions
        if not mover.canMove(start, target):
            if target not in [move for move, ep in mover.attackMoves(start)]:
                raise position.ImpossibleMove, '%s can never perform this move (%s, %s).' % (mover.name, start, target)
        if target not in self.calcMovesForPiece(start, unconditional):
            for end, ep in self.specialAttackMoves(start, unconditional):
                if target == end:
                    if ep is not None:
                        instructions['state'] = EN_PASSANT
                        instructions['clear'] = ep
                    return instructions
            else:
                raise position.ImpossibleMove, \
                      'Position %s cannot be reached by %s at %s.' % (target, mover.name, start)
        return instructions

    def value(self):
        """Return value of current board.

        Positive: white is in a better position
        Negative: black is in a better position


        An empty chess board is worth nothing

        >>> board = ChessBoard(EMPTY_CHESS_BOARD)
        >>> board.value()
        0

        In the beginning white and black should be equal.  White
        begins first though, so maybe we want to give him a small
        advantage later on.

        >>> board = ChessBoard()
        >>> board.value()
        0

        On our castling board, black and white are equal.

        >>> board = ChessBoard(CASTLING_BOARD)
        >>> board.value()
        0

        Let's inspect our end game board.

        >>> board = ChessBoard(ENDGAME_BOARD)
        >>> board.printPieces()
        KQ----N-P-------
        kqr-b---pp------

        The white knight and black bishop even out, but black has a
        rook and a pawn more.

        >>> board.value()
        -6

        Let's inspect our end promotion board.

        >>> board = ChessBoard(PROMOTION_BOARD)
        >>> board.printPieces()
        K-R---N-PPPP----
        k-r-----ppp-----

        White has a knight and a pawn more.

        >>> board.value()
        4

        """
        total = 0
        for row in range(self.nrows):
            for col in range(self.ncols):
                square = position.squarify(row, col)
                total += self.pieceWorth(square)
        return total


    def pieceWorth(self, square):
        """How much is this piece worth?
        
        >>> board = ChessBoard()

        An empty square is worth nothing.

        >>> board.pieceWorth('A3')
        0

        A white rook is +5 points.  A black rook -5.

        >>> board.pieceWorth('A1')
        5
        >>> board.pieceWorth('A8')
        -5

        Now pawns

        >>> board.pieceWorth('A2')
        1
        >>> board.pieceWorth('A7')
        -1

        """
        p = self[square]
        points = p.value
        return points * p.colour

    def printPieces(self):
        """Print the pieces that are on the board.
        Make this one line for white and one for black.

        This is mostly handy for testing.  We want to see such a list
        to more easily see who has the upper hand.
        
        What does a normal chess board show?

        >>> board = ChessBoard()
        >>> board.printPieces()
        KQRRBBNNPPPPPPPP
        kqrrbbnnpppppppp

        Let's remove some pieces.

        >>> board.empty('C1')
        >>> board.empty('B8')
        >>> board.empty('F2')
        >>> board.empty('D8')
        >>> board.printPieces()
        KQRRB-NNPPPPPPP-
        k-rrbbn-pppppppp

        Let's try our castling board.

        >>> board = ChessBoard(CASTLING_BOARD)
        >>> board.printPieces()
        K-RR----P-------
        k-rr----p-------

        Let's try our end game board.

        >>> board = ChessBoard(ENDGAME_BOARD)
        >>> board.printPieces()
        KQ----N-P-------
        kqr-b---pp------

        An empty chess board will return just two empty lines.

        >>> board = ChessBoard(EMPTY_CHESS_BOARD)
        >>> board.printPieces()
        ----------------
        ----------------

        """
        results = {WHITE: '', BLACK: ''}
        for symbol, number in piece.piece_numbers_list:
            for colour in (WHITE, BLACK):
                found = self.findPiece(symbol, colour)
                results[colour] += symbol * len(found)
                results[colour] += '-' * abs(number - len(found))
        print "%s\n%s" % (results[WHITE], results[BLACK].lower())


    def findPiece(self, symbol, colour):
        """Find a piece with this symbol and colour.

        Find white rooks.

        >>> board = ChessBoard()
        >>> board.findPiece('R', WHITE)
        ['A1', 'H1']

        Lowercase is also acceptable.

        >>> board.findPiece('r', WHITE)
        ['A1', 'H1']

        Give me all black pawns.

        >>> board.findPiece('P', BLACK)
        ['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7']
        """
        symbol = symbol.upper()
        results = []
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self[row, col].symbol == symbol and \
                   self[row, col].colour == colour:
                    results.append(position.squarify(row, col))
        return results

    def hint(self, depth=0):
        """Give a hint for the current player.

        Our hints are pretty lousy currently.

        >>> board = ChessBoard(HINT_BOARD)
        >>> board.hint()
        {'start': 'D7', 'target': 'A7', 'value': 5}
        """
        options = []
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self[row, col].colour == self.player:
                    friend = position.squarify(row, col)
                    moves = self.calcMovesForPiece(friend)
                    moves.extend([x[0] for x in self.specialAttackMoves(friend)])
                    for move in moves:
                        board = copy.deepcopy(self)
                        try:
                            board.move(friend, move)
                        except position.PromotionException:
                            continue
                        if depth > 0:
                            value = board.hint(depth-1)['value']
                        if depth == 0:
                            value = board.value()
                        options.append({'start': friend,
                                        'target': move,
                                        'value': value})
        if self.player == WHITE:
            fun = max
        else:
            fun = min
        if len(options) == 0:
            return None
        best_value = fun([x['value'] for x in options])
        best_move = [x for x in options if x['value'] == best_value]
        return best_move[0]
        

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
