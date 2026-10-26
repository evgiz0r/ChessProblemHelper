"""E. Bourd (15 Oct 2026): zugzwang + random knight moves + symmetry = a scheme; the gate fails a 'simple block'."""
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique


def rules(fen):
    p = Problem.from_fen(fen + ' w - - 0 1', '#2')
    return {f['rule']: f['severity'] for f in critique(p, analyse(p, time_limit=60), necessity=False)['findings']}


def test_type2_mutate_is_a_simple_block():
    r = rules('b7/1pn5/1PB2R2/4k1P1/3R2P1/3K2n1/8/8')
    assert r.get('simple block') == 'major'
    assert 'random defences' in r and 'zugzwang key' in r and 'symmetric play' in r


def test_threat_problem_is_not_a_block():
    r = rules('K2N4/4B1nQ/3p1P2/p1p1k3/r7/1n2P1N1/6B1/3r4')   # claude-changed-type1-double-closing
    assert 'simple block' not in r and 'zugzwang key' not in r


def test_random_moves_are_not_counted_as_defences():
    # E. Bourd (26 Oct 2026), daily No. 20: "those S~ are not defenses" - 1...Sh8/Sh6/Sg5 2.Qd7# leave two defences
    p = Problem.from_fen('3B2b1/5n2/Q1N5/pN1k1P2/8/5P2/2R5/6bK w - - 0 1', '#2')
    f = {x['rule']: x for x in critique(p, analyse(p, time_limit=60), necessity=False)['findings']}
    assert 'random defences' in f and 'varied play' not in f
