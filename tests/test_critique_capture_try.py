"""E. Bourd, 27 Oct 2026, on daily No. 21 (1.S~? Rd6!, 1.Se6? Rxe6!, 1.Bxh6? Bd6!, 1.Sf3!): "Bxh6 is a non-try, cannot
just captre a rook like that ... the whole try looks too forced and not unified, almost random"."""
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique

NO21 = '1b1RQ3/8/7r/2p1p1B1/3Nk3/4N3/2K2nP1/8 w - - 0 1'


def _rules(fen):
    p = Problem.from_fen(fen, '#2')
    return {f['rule']: f for f in critique(p, analyse(p, include_tries=True), necessity=False)['findings']}


def test_capture_try_is_no_try_and_the_extension_is_one_sided():
    r = _rules(NO21)
    assert 'capture try' in r and 'Bxh6' in r['capture try']['msg']
    assert 'one-sided extension' in r and r['one-sided extension']['severity'] == 'major'


def test_correction_refuted_by_a_capture_makes_the_correction_random():
    r = _rules(NO21)
    assert 'white correction' not in r and 'random white correction' in r
