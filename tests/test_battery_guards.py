import chess
from chesscomp.compose.battery_guards import configurations


def test_queen_holds_the_d_file_battery_two_ways():
    # E. Bourd's bench idea on Kd4 / Sd5 / Rd8: the queen interposes and captures the c4 or the e4 guard
    found = {(chess.square_name(p), chess.square_name(a[1]), chess.square_name(b[1]))
             for p, a, b in configurations(chess.D4, chess.D5, chess.D8, chess.C4, chess.E4)}
    assert found == {('f5', 'c2', 'f2'), ('b5', 'b2', 'e2')}
    assert not configurations(chess.D4, chess.D5, chess.D8, chess.C4, chess.E4, chess.ROOK)
