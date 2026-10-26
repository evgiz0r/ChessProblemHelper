"""Black correction: a random move must defend before anything can correct it."""
from chesscomp.analysis import analyse
from chesscomp.core import Problem


def _phase(fen, kind):
    r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_tries=False, include_set=True, time_limit=10)
    return next(p for p in r['phases'] if p['type'] == kind)


def test_non_defending_moves_are_not_a_random_move():
    # E. Bourd (24 Oct 2026): "its not a correction btw, if a piece doesnt defend, its not anything. correction of
    # what? of non defending move?" Here 2.Rf6# works whatever Black does, so 1...B~ and 1...S~ do not defend.
    st = _phase('8/2p5/1b5R/7B/K1N3r1/5kP1/3n3Q/4R3', 'set')
    assert st['corrections'] == []


def test_a_real_correction_is_still_found():
    key = _phase('b3N3/8/ppn1p3/4k3/3R2P1/4P3/7K/2Q5', 'key')
    assert [x['move'] for c in key['corrections'] for x in c['corrections']] == ['Sxd4']


def test_a_threat_that_captures_the_piece_makes_its_moves_random():
    # E. Bourd (26 Oct 2026), on daily No. 17's attempt 1.Qc3! (2.Qxd4#): "correction might be neuanced, but if we are
    # attacking it, a random of it defends. thats for sure a random move"
    key = _phase('8/B7/8/5p2/2Prkp2/1Q3N1K/6P1/8', 'key')
    assert [c['random']['mate'] for c in key['corrections']] == ['Sg5#']
    assert sorted(x['move'] for c in key['corrections'] for x in c['corrections']) == ['Rd3', 'Rxc4']
