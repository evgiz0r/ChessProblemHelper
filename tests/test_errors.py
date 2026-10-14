from chesscomp.compose.errors import classify, report
import chess


def _cls(fen, key, san):
    b = chess.Board(fen + ' w - - 0 1')
    if key:
        b.push_uci(key)
    b.turn = chess.BLACK
    return classify(b, b.parse_san(san))


def test_one_unit_two_squares_is_departure_in_both_phases():
    fen = '8/2pK2nQ/5N2/4k1P1/7p/2nBP3/2r1p3/8'          # claude-changed-type1-unique-qg8
    assert _cls(fen, None, 'Ne6') == {'Qf5': 'departure'}
    assert _cls(fen, 'h7g8', 'Ne6') == {'Qxe6': 'departure'}


def test_two_errors_split_between_departure_and_arrival():
    fen = '8/3BB1nQ/1nP2N2/p3k1Pp/r7/p2KP1P1/8/8'        # claude-changed-type1-qg8-two-errors
    assert _cls(fen, None, 'Nc4') == {'Qe4': 'arrival'}
    assert _cls(fen, 'h7g8', 'Nc4') == {'Qd5': 'departure'}
    pawn = '2Q2K2/1B1N4/3p4/1p6/1n1k1P2/1Ppp2R1/2b2N2/2b5'  # bourd-changed-type1-pawn-errors
    assert _cls(pawn, None, 'd2') == {'Qxc3': 'departure'}
    assert _cls(pawn, 'c8e8', 'd2') == {'Qe3': 'arrival'}
    assert '1...Sc4: Qe4# (arrival)' in report(fen, ['Sc4'], 'h7g8')
