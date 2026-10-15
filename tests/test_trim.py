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
