"""White correction score (daily No. 10): the key piece's random move fails to one defence, its corrections to
others; a try refuted by a king move is fatal for us, so it is never a hit."""
import chess
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.compose.white_correction import wcorr_score


def _score(fen, sq):
    b = chess.Board(fen + ' w - - 0 1')
    r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=4, include_tries=True, time_limit=30)
    return wcorr_score(b, r, sq)


def test_loustau_fourth_degree_correction_is_a_hit():
    # Loustau, Phenix 1999, 2nd Prize: 1.B~? Qxg1!, 1.Bc5? Bc7!, 1.Bd4? Bc5!, 1.Be3!
    sc, summ, ok = _score('4R3/3N4/1BNb1R1r/1K1k1p2/1p4q1/3P4/4r3/6Q1', 'b6')
    assert ok and 'random Qxg1x4' in summ and 'Bc5?Bc7' in summ and 'Bd4?Bc5' in summ


def test_king_refutation_is_no_hit():
    # Narayanan 1997: the correction 1.Se8? fails to 1...Kxd7!
    sc, summ, ok = _score('B4R2/3Np3/b2Nk3/3r4/1Q5B/8/3R4/7K', 'd6')
    assert not ok and 'random Rc5x2' in summ and 'kingref=' in summ and 'kingref=0' not in summ
