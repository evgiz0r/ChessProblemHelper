"""E. Bourd (14 Oct 2026): guard-only defences are pure single moves when the mates change between phases ("I don't
think it's a flaw, it's somewhat pure single moves"), and a mate that recaptures the defender on its arrival square is
the flaw ("I didn't like the recapture of the queen on the defense squares")."""
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique


def _findings(fen):
    p = Problem.from_fen(fen + ' w - - 0 1', '#2')
    return {f['rule']: f['severity'] for f in critique(p, analyse(p), necessity=False)['findings']}


def test_guard_defences_with_changed_mates_are_pure():
    f = _findings('B1RK3b/1Q1Pp3/1P6/7r/2pkpB2/8/3nP3/3N4')      # bourd-changed-diag-file-qc7: Rh3/Sf1 guard e3
    assert f.get('pure guard defences') == 'note' and 'guard/unguard play' not in f
    assert 'mate captures defender' not in f


def test_mate_capturing_the_defender_is_flagged():
    f = _findings('8/2pK2nQ/5N2/4k1P1/7p/2nBP3/2r1p3/8')          # claude-changed-type1-unique-qg8: 1...Se6 2.Qxe6#
    assert f.get('mate captures defender') == 'minor'


def test_single_phase_guard_play_stays_weak():
    f = _findings('3b4/6n1/N2R4/2RP1p2/3Pkp2/K3pN2/BB2P3/7r')    # the session-2 example
    assert f.get('guard/unguard play') == 'minor'
