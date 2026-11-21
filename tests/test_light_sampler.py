import chess
from chesscomp.compose.light_sampler import boxed, examine


def test_light_sampler_reads_the_quick_qc6_miniature():
    # claude-quick-qc6-pawns (21 Nov 2026): the sampler's own find, re-examined
    b = chess.Board('8/1Q6/8/2p1p3/3k4/1P3p2/3K4/2N5 w - - 0 1')
    assert boxed(b)
    d, nk, du, line = examine(b)
    assert (d, nk, du) == (3, 3, 0)
    assert 'key Qc6' in line and "f2:['c1e2']" in line


def test_light_sampler_drops_a_cooked_diagram():
    # 6K1/8/2Q1p3/4k3/3N4/2P2R2/5PB1/8: protecting d4 makes 1.Qxe6 mate in one (the king-star dead end)
    assert examine(chess.Board('6K1/8/2Q1p3/4k3/3N4/2P2R2/5PB1/8 w - - 0 1')) is None
