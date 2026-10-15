import chess
from chesscomp.compose.keysel import evaluate, keys

M = chess.Move.from_uci
ARGS = (chess.D5, M('c5c4'), M('d1d4'), M('d8d4'))


def test_scheme_has_one_key_and_the_change():
    # claude-type2-d4-scheme: set 1...c4 2.Rd4#, 1.Sc7! (2.Qd3#) c4 2.Qd4#; 1.Se7? Rd7!
    b = chess.Board('3Q1R2/1r6/8/2pNN3/4kP2/2P5/8/3RK3 w - - 0 1')
    sc, summ = evaluate(b, *ARGS)
    assert summ.startswith("keys ['Nc7']") and "thr ['d8d3']" in summ and sc > 0


def test_without_the_rook_every_knight_move_solves():
    b = chess.Board('3Q1R2/8/8/2pNN3/4kP2/2P5/8/3RK3 w - - 0 1')
    assert {b.san(k) for k in keys(b)} >= {'Nc7', 'Ne7', 'Nb6'}
