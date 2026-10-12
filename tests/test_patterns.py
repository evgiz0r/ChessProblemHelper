"""Theme detectors reported in the solver's Patterns list (chesscomp.analysis + chesscomp.motives)."""
import json, os
from chesscomp.core import Problem
from chesscomp.analysis import analyse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _patterns(fen):
    res = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_tries=False, include_set=False, time_limit=60)
    return res['relations']['patterns']


def test_half_pin_reported_per_defence():
    # Barnes, StrateGems 2002, 1st Prize (psis-25e8021eff): Rh4 half-pins Re4 and Sd4 against Kc4;
    # 1.Qf7! Re6 2.Qc7# (Sd4 pinned), Se6 2.Qf1# (Re4 pinned); 1...Rb2 2.Rc3# is not half-pin play.
    hp = [p for p in _patterns('7b/8/1K1p2Q1/3N4/1Nknr2R/P6R/2rp4/B7') if p['name'] == 'Half-pin']
    assert sorted(p['defence'] for p in hp) == ['Re6', 'Se6']
    assert all(p['line'] == 'Rh4-c4' for p in hp)


def test_no_half_pin_in_grimshaw():
    # daily No. 6 (Grimshaw on e7): no two black units on one white line to the king
    assert not [p for p in _patterns('3Q1bb1/2N3r1/1N3Rpp/1pP1k3/3p4/3P4/5K2/8') if p['name'] == 'Half-pin']


def test_knowledge_jsonl_has_no_merge_markers():
    # 12 Oct 2026: a merge left <<<<<<< / ======= / >>>>>>> lines in lessons.jsonl on main
    for name in ('lessons.jsonl',):
        for i, line in enumerate(open(os.path.join(ROOT, 'knowledge', name)), 1):
            assert not line.startswith(('<<<<<<<', '=======', '>>>>>>>')), (name, i)
            if line.strip():
                json.loads(line)
