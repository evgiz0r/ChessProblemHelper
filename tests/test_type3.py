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
