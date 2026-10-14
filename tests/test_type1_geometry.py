"""Type-1 geometry (E. Bourd's type 1, 14 Oct 2026): rook + bishop defenders exist only with queen posts, not lines."""
import chess
from chesscomp.compose.type1_geometry import line_pairs, post_pairs, threats


def test_rook_and_bishop_never_share_two_queen_lines():
    assert line_pairs('d4', 'RB') == []
    assert line_pairs('e5', 'RB') == []
    assert line_pairs('d4', 'RR')          # two rooks do: ranks 3 and 5 with rooks on the c- and e-files


def test_one_step_posts_and_their_knight_threats():
    pp = post_pairs('d4', 'RB', maxkey=1)
    keys = {(chess.square_name(p['pa']), chess.square_name(p['pb'])) for p in pp}
    assert {('g3', 'g2'), ('c7', 'b7')} <= keys
    g = next(p for p in pp if (p['pa'], p['pb']) == (chess.G3, chess.G2)
             and {d[1] for d in p['defenders']} == {chess.H5, chess.H7})
    th = threats('d4', g)
    assert any(t['x'] == 'Nd2' and t['t'] == 'b3' for t in th)
