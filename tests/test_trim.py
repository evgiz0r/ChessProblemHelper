"""trim: removal sets, not single removals (E. Bourd: bPh6 was an artifact of bRh5)."""
from chesscomp.compose.trim import trim


def test_recursive_trim_finds_the_artifact_pair():
    key, board, found = trim('2B3nK/8/2pR3p/2rpkN1r/1Qbp4/2np1P2/6N1/8', max_removed=3)
    assert key == 'Rg6'
    assert '2B3nK/8/2pR4/2rpkN2/1Qbp4/2np1P2/6N1/8' in [f for _, f in found]


def test_trim_works_for_a_zugzwang_key():
    # 15 Oct 2026: the empty '(threat)' entry of a block made every removal look like a refuted defence
    key, board, found = trim('8/2n5/2B2RK1/4k3/3R4/2P1P1n1/8/8', max_removed=2)
    assert key == 'Bd7'
    assert {f for _, f in found} == {'8/2n5/2B2RK1/4k3/3R4/4P1n1/8/8', '8/2n5/2B2RK1/4k3/3R4/2P3n1/8/8'}


def test_trim_allow_flight_keeps_a_structural_flight():
    # 24 Oct 2026, his masked pin 1.Bf2!: e4 is the only answer to the free knight's checks, so the diagram flight
    # is the price of the scheme; without --allow-flight trim refused the diagram, with it wPc2 or bPd3 can go
    fen = 'b2r4/2Q1R3/1p3n1q/1N1kPpnp/r1NB3K/1P1p1pP1/2P5/8'
    key, board, found = trim(fen, max_removed=1, allow_flight=True)
    assert key == 'Bf2'
    assert {f for _, f in found} == {'b2r4/2Q1R3/1p3n1q/1N1kPpnp/r1NB3K/1P1p1pP1/8/8',
                                     'b2r4/2Q1R3/1p3n1q/1N1kPpnp/r1NB3K/1P3pP1/2P5/8'}
