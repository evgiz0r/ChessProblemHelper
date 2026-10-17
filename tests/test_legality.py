import chess
from chesscomp.core import illegal_position


def test_pawn_captures_beyond_lost_units_are_illegal():
    # E. Bourd (17 Oct 2026): "the position is illegal, so its a fatal flaw" - bourd-pawn-battery-queen-sd2 v1:
    # Black pawns c4 f2 g3 g5 h4 beside e7/h7 need 9 captures, White has lost 3 units
    b = chess.Board('1B4nK/4p1rp/2B1PP1R/R5p1/2p1N1kp/1qPP2p1/4PpP1/3Qbr2 w - - 0 1')
    assert illegal_position(b) == ['Black pawns need at least 9 captures, but White has lost only 3 units']


def test_legal_positions_pass():
    assert not illegal_position(chess.Board())
    assert not illegal_position(chess.Board('8/B2r1B2/2b5/4p3/1P2k1Kn/4pp2/2P5/1Q4N1 w - - 0 1'))


def test_eight_pawns_need_eight_home_files():
    # psis-1ea964d9a5: Black pawns b7 d7 f7 g7 c6 f6 d4 b3, the h-pawn cannot reach any of them
    b = chess.Board('8/qp1pKpp1/2p2p2/3N4/R1Qpk1P1/1p1Nb2r/4P3/1n3R2 w - - 0 1')
    assert illegal_position(b) == ['Black pawns stand where no home files can bring them']
