"""compose.halfpin_pair scores a half-pin post-key position: one defence per half-pinned unit, each with its mate."""
from chesscomp.compose import halfpin_pair as hp

# J. Kapros, Problemesis 2002 (psis-0dd597ba62) after 1.Sxb5!: Rc6 2.Sc3#, Bd4 2.Sd6#
KAPROS_POST = '5K2/1Bn1R3/4rp2/1N1rb3/1Rq1kpP1/nP2pN2/2P3P1/3Q4'
SPEC = {'key': 'd4b5', 'rook': 'e6', 'bishop': 'e5', 'mr': 'Nb5c3', 'mb': 'Nb5d6', 'tr': 'd4f5', 'tb': 'd4e2'}


def test_kapros_post_key_defences():
    s, ok, r, b, info = hp.post_check(KAPROS_POST, SPEC)
    assert r == 'e6c6' and b == 'e5d4', info


def test_diagram_puts_key_piece_back():
    assert hp.diagram_of(KAPROS_POST, SPEC) == '5K2/1Bn1R3/4rp2/3rb3/1RqNkpP1/nP2pN2/2P3P1/3Q4'
