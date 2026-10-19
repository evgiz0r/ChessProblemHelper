"""compose.legrand: the fast Le Grand scorer (daily No. 14)."""
import chess
from chesscomp.compose.legrand import evaluate


def test_labai_is_a_hit():
    # Z. Labai (psis-bdd8420216): 1.Kb3? (2.Qe5#) Kd6 2.Qd4#, 1.Sf3! (2.Qd4#) Kd6 2.Qe5#
    s, summ, hit = evaluate(chess.Board('8/1R5n/2p5/2k3N1/4Q3/K7/8/8 w - - 0 1'))
    assert hit
    assert 'key Sf3!' in summ and "LG=['c5d6']" in summ


def test_unprovided_flight_is_no_hit():
    # E. Bourd (psis-7323fac2ab): the Le Grand is found, but 1...Ke4 has no set mate
    s, summ, hit = evaluate(chess.Board('1n3Q2/5b2/p7/1P1k1P2/2Nn1B2/1B3R2/8/K2R2b1 w - - 0 1'))
    assert "LG=['d5e4']" in summ and not hit


def test_mate_in_one_scores_lowest():
    s, summ, hit = evaluate(chess.Board('6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1'))
    assert summ == 'mate in one' and not hit


def test_pairs_layer_finds_the_le_grand_pair():
    # daily No. 14: around this kernel one Black unit already gives the try/key pair 1.Be3?/1.Be2! on 1...Kd5
    from chesscomp.compose.legrand import pairs
    res = pairs('7K/8/Q1N2R2/4p3/4k3/8/6N1/2BB2b1', 'b', 2)
    assert any("LG=['e4d5']" in summ for s, fen, summ, hit in res)
