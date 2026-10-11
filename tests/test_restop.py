"""Re-placing a cook-stopper (chesscomp.compose.restop) on E. Bourd's 1.Qb5! (11 Oct 2026)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chesscomp.compose.restop import check, candidates
import chess

FEN = 'nK6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8'
WANT = {'Bf6': 'Sb4#', 'Bg6': 'Qb3#'}


def test_knight_on_e8_adds_a_third_cut():
    fen, setm, extra = check(('1K2n3/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8', 'Qb5', WANT))
    assert extra == {'Sf6': 'Sc7#'}
    assert setm == {'Bf6': '-', 'Bg6': 'Qa2#'}


def test_without_the_stopper_it_fails():
    assert check(('1K6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8', 'Qb5', WANT)) is None   # double threat Sc7#


def test_candidates_skip_pawns_on_the_edge():
    cs = list(candidates(FEN, [chess.A8]))
    assert all('P' not in c.split('/')[0] and 'p' not in c.split('/')[-1] for c in cs)
    assert '1K2n3/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8' in cs
