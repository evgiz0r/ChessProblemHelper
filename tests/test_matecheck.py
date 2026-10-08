"""matecheck: the square-by-square reason a check is not mate (the unprotected d5 rook)."""
import chess
from chesscomp.compose.matecheck import explain


def test_unprotected_rook_shows_free():
    b = chess.Board('8/8/4P1N1/3R3B/4k3/r7/6P1/b1RN3K w - - 0 1'); b.push_san('Rc4')
    lines = explain(b)
    assert lines[0] == 'check, not mate'
    assert any(l.strip().startswith('d5 (white R there): FREE') for l in lines)
    assert any('interposition: Bd4' in l for l in lines)
