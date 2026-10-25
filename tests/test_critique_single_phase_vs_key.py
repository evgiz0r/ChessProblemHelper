"""The gate's second phase: a changed mate counts only against the key (daily No. 19, 24 Oct 2026)."""
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique


def _rules(fen):
    p = Problem.from_fen(fen + ' w - - 0 1', '#2')
    res = analyse(p, include_tries=True, include_set=True)
    return res['keys'], {f['rule'] for f in critique(p, res)['findings']}


def test_change_between_two_tries_is_no_second_phase():
    # bPf6 added to claude-two-flight-knight-sacrifice: 1...e4 2.Qd4# after 1.Sf5?, 2.Sc7# after 1.Sa6?; key 1.Se4!
    keys, rules = _rules('2R2B1b/8/4PpbN/2Nkp3/p4p2/2Q5/3K4/8')
    assert keys == ['Se4'] and 'single phase' in rules


def test_change_against_the_key_still_counts():
    # Kisis, Heureka! 1992-93, 3rd Prize: 1...Bg4 2.Rf2# (key 1.Bb1!) against 2.Bb1# (try 1.Rf2?)
    keys, rules = _rules('1b6/5N1n/1B2p3/1p3b1Q/4k3/4P3/B1R5/2N4K')
    assert keys == ['Bb1'] and 'single phase' not in rules


def test_change_against_a_king_refuted_try_is_no_second_phase():
    # daily No. 20's draft: 1.Qc8! (2.Qe6#) Sd6 2.Sc7#, Se5 2.Se7#; the knight's 1.Scd4? changes both mates (Qd6#) but
    # fails to 1...Ke5!, which is no try (CLAUDE.md), and the gate had passed the single phase on it
    keys, rules = _rules('6b1/5n2/Q1N5/pN1k1P2/8/5P2/5b2/2R4K')
    assert keys == ['Qc8'] and 'single phase' in rules
