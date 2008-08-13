ROWS = 3
COLS = 3
CHESS_ROWS = 8
CHESS_COLS = 8

PLAIN = 0
WHITE = 1
BLACK = -1

# Standard Chess board.
# Black is at the top (lowercase), white at the bottom (uppercase)
CHESS_BOARD = """
rnbqkbnr
pppppppp
........
........
........
........
PPPPPPPP
RNBQKBNR
"""

# Empty chess board.
EMPTY_CHESS_BOARD = """
........
........
........
........
........
........
........
........
"""

# Simple board for hint
HINT_BOARD = """
k.......
p..R....
........
........
........
........
........
.......K
"""

# Board for testing castling.
CASTLING_BOARD = """
r...k..r
.p......
........
........
........
........
.P......
R...K..R
"""

# Board for testing end games.
ENDGAME_BOARD = """
....k..r
pp......
.bN.....
........
........
.q....P.
......K.
Q.......
"""

# Board for testing promotions.
PROMOTION_BOARD = """
.......r
RpP..kP.
...P..N.
........
........
...p....
P...p.K.
........
"""

# Board for testing mates.
MATE_BOARD = """
......rk
......pp
...p....
....N...
........
......q.
r.......
.......K
"""

# Black should be able to hit the white queen here.
DEFEND_KING_BOARD = """
..k..Qnr
ppp....p
..nppq.B
........
.....P..
..N.....
PPP..PPP
R....RK.
"""

# When castling, the with a Rook at A1, the white King moves from E1
# to C1 and the Rook moves to D1.

CASTLE_PAIRS = (
    {'colour': WHITE,
     'king_start': 'E1',
     'king_middle': 'D1',
     'king_end': 'C1',
     'rook_start': 'A1',
     'rook_end': 'D1'},
    {'colour': WHITE,
     'king_start': 'E1',
     'king_middle': 'F1',
     'king_end': 'G1',
     'rook_start': 'H1',
     'rook_end': 'F1'},
    {'colour': BLACK,
     'king_start': 'E8',
     'king_middle': 'D8',
     'king_end': 'C8',
     'rook_start': 'A8',
     'rook_end': 'D8'},
    {'colour': BLACK,
     'king_start': 'E8',
     'king_middle': 'F8',
     'king_end': 'G8',
     'rook_start': 'H8',
     'rook_end': 'F8'},
    )
