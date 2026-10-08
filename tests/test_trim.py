"""trim: removal sets, not single removals (E. Bourd: bPh6 was an artifact of bRh5)."""
from chesscomp.compose.trim import trim


def test_recursive_trim_finds_the_artifact_pair():
    key, board, found = trim('2B3nK/8/2pR3p/2rpkN1r/1Qbp4/2np1P2/6N1/8', max_removed=3)
    assert key == 'Rg6'
    assert '2B3nK/8/2pR4/2rpkN2/1Qbp4/2np1P2/6N1/8' in [f for _, f in found]
