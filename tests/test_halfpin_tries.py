"""compose.halfpin_tries scores a half-pin diagram by the solver: one defence per half-pinned unit, pin-using mates,
and tries refuted by one thematic defence alone (a pure pair)."""
from chesscomp.compose import halfpin_tries as ht

SPEC = {'rook': 'e6', 'bishop': 'e5'}


def test_kapros_pure_pair_found():
    # J. Kapros, Problemesis 2002 (psis-0dd597ba62): 1.Sxb5! Rc6 2.Sc3#, Bd4 2.Sd6#; 1.Sf5? Rc6!, 1.Se2? Bd4!
    s, info = ht.score('5K2/1Bn1R3/4rp2/1p1rb3/1RqNkpP1/nP2pN2/2P3P1/3Q4', SPEC)
    assert "'Sf5?Rc6'" in info and "'Se2?Bd4'" in info, info


def test_file_half_pin_without_tries():
    # claude-halfpin-file-sf7: 1.Sf7! Rg6 2.Rd4#, Bf6 2.Sxd6#, both mates use the pin, no thematic try
    s, info = ht.score('4R3/3p4/3pr2N/3Rb2p/2K1kp1N/8/3B4/8', SPEC)
    assert "('e6g6', 'd5d4', 'Rg6', 'Rd4#', True)" in info and "('e5f6', 'f7d6', 'Bf6', 'Sxd6#', True)" in info, info
    assert 'tries=[]' in info
