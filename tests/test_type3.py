import chess
from chesscomp.compose.type3 import evaluate

KEY, MP = chess.Move.from_uci('d2e2'), chess.D1


def test_specific_defence_scores_above_random_knights():
    # claude-type3-queen-lines: 1.Ke2! (2.Qd4#) Sd7 Qd5# (set Qg4#), Se1-c2/f3/d3 Qd3# (set Qf3#)
    sc, summ = evaluate(chess.Board('2B5/8/2N2n2/8/2P1k3/1p2P3/3K4/1R1Qn1N1 w - - 0 1'), KEY, MP)
    assert summ.startswith("keys ['Ke2']") and "good ['e1:3/3', 'f6:1/1']" in summ and 'duals 0' in summ
    # the scheme stage: every move of the f6 knight defends (Bh8 opens to d4)
    sc0, summ0 = evaluate(chess.Board('7b/8/5n2/R7/4k3/1p2P3/3K4/1R1Qn1N1 w - - 0 1'), KEY, MP)
    assert "'f6:5/7'" in summ0 and sc > sc0


def test_pawn_selector_with_a_threat_off_the_queen_lines():
    # claude-type3-pawn-g5: 1.g5! (2.Sd3#) Rxc8 Qf4# (set Qg5#), Sb4 Qd4# (set Qe7#)
    b = chess.Board('2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8 w - - 0 1')
    k, mp = chess.Move.from_uci('g4g5'), chess.H4
    sc, summ = evaluate(b, k, mp, noqthr=True)
    assert summ.startswith("keys ['g5']") and "thr ['c5d3']" in summ and "good ['c6:1/1', 'f8:1/2']" in summ
    assert "'f8" not in evaluate(b, k, mp, noqthr=True, quiet=True)[1]     # 1...Rxc8 is a capture


def test_pawny_charges_officers():
    b = chess.Board('2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8 w - - 0 1')
    k, mp = chess.Move.from_uci('g4g5'), chess.H4
    assert evaluate(b, k, mp, noqthr=True)[0] - evaluate(b, k, mp, noqthr=True, pawny=3)[0] == 3 * 6   # Q B S S r s
