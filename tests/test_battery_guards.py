import chess
from chesscomp.compose.battery_guards import configurations


def test_queen_holds_the_d_file_battery_two_ways():
    # E. Bourd's bench idea on Kd4 / Sd5 / Rd8: the queen interposes and captures the c4 or the e4 guard
    found = {(chess.square_name(p), chess.square_name(a[1]), chess.square_name(b[1]))
             for p, a, b in configurations(chess.D4, chess.D5, chess.D8, chess.C4, chess.E4)}
    assert found == {('f5', 'c2', 'f2'), ('b5', 'b2', 'e2')}
    assert not configurations(chess.D4, chess.D5, chess.D8, chess.C4, chess.E4, chess.ROOK)


def test_pawn_front_piece():
    # pawn battery Bb1/Pc2 against Ke4: c3 guards d4, c4 guards d5
    found = configurations(chess.E4, chess.C2, chess.B1, chess.D4, chess.D5, chess.QUEEN, chess.PAWN)
    assert found and all(chess.square_distance(p, chess.E4) > 1 for p, _, _ in found)


def test_no_knight_holds_the_pawn_battery():
    assert not configurations(chess.E4, chess.C2, chess.B1, chess.D4, chess.D5, chess.KNIGHT, chess.PAWN)


def test_holder_attacking_the_rear():
    # E. Bourd's fix (bench mvcop42d): the holder attacks the rear piece instead of interposing. For the bishop-knight
    # battery Bb1/Sc2 v Ke4 (Sb4 guards d5, Se1 guards f3) a knight on d2 does it with Bb3 and Rf1
    found = {(chess.square_name(p), chess.square_name(a[1]), chess.square_name(b[1]))
             for p, a, b in configurations(chess.E4, chess.C2, chess.B1, chess.D5, chess.F3, chess.KNIGHT, chess.KNIGHT, 'rear')}
    assert ('d2', 'b3', 'f1') in found
