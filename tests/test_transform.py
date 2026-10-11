"""Shifts and rotations of a position (chesscomp.compose.transform)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chesscomp.compose.transform import transform, placements, post_metrics

BEFORE = '2n5/2Np4/1p1p4/3B3R/1Qpk4/1Kpb1R2/2pb3B/8'      # E. Bourd's bench, 11 Oct 2026, before the turn
AFTER = '8/2KQ1p2/1ppp2Nn/1bbkBpp1/8/2R5/8/1B2R3'          # ... and after it


def test_quarter_turn_reproduces_the_bench():
    assert transform(BEFORE, 'rot90') == AFTER
    assert transform(AFTER, 'rot270') == BEFORE


def test_shift_and_edges():
    assert transform('8/8/8/3k4/8/8/8/K7', 'id', 1, 1) == '8/8/4k3/8/8/8/1K6/8'
    assert transform('8/8/8/3k4/8/8/8/K7', 'id', -1, 0) is None          # off the board
    assert transform('8/8/8/3k4/8/2P5/8/K7', 'flip') == 'K7/8/2P5/8/3k4/8/8/8'   # c3 -> c6, d5 -> d4
    assert transform('8/8/8/3k4/8/8/2P5/K7', 'id', 0, -1) is None        # a pawn on the first rank


def test_only_legal_placements_are_solved():
    rows = [(o, f) for o, dx, dy, f in placements(BEFORE) if post_metrics(f) is not None]
    assert ('rot90', AFTER) in rows
    assert all(o == 'rot90' for o, _ in rows)                            # elsewhere the c4 pawn checks the king
