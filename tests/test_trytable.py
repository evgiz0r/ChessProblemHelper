"""compose.trytable: the hand try table (daily No. 12)."""
from chesscomp.compose.trytable import table

DAILY12 = '8/8/K2p4/8/N2k1P1p/1P3B1R/2P4R/3Nb3'


def test_daily12_bishop_moves():
    sp, rows = table(DAILY12, ['f3'])
    assert sp['Bg3'] == ['Rd2#'] and sp['Bd2'] == ['Rxd2#']
    by = {r['san']: r for r in rows}
    keys = [s for s, r in by.items() if not r['refutations'] and not r['mate1']]
    assert keys == ['Bh1']
    assert by['Bh1']['threats'] == ['Rd3#'] and by['Bh1']['variations']['Bg3'] == ['Rd2#']
    assert by['Bg2']['refutations'] == ['Bg3']          # the bishop on g2 shuts Rh2 off d2
    assert by['Bc6']['refutations'] == ['d5']           # the pawn cuts c6-e4
    assert by['Bd5']['refutations'] == ['Kxd5']


def test_knight_version_has_two_refutations():
    # the published attempt: a knight f1 interposes on g3 and e3, both refuting 1.Bg2?
    _, rows = table('8/8/K2p4/8/1P1k1P1p/5B1R/1N5R/3N1n2', ['f3'])
    by = {r['san']: r for r in rows}
    assert sorted(by['Bg2']['refutations']) == ['Ne3', 'Ng3']
