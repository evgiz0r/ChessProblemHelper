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


def test_self_pin_by_capture_reported_per_defence():
    # Avner & Retter, Israel Ring Tourney 2000, 4th Prize (psis-30b58be7a5): 1.Qb3! Bxd6 2.Se4# (Bd6 pinned
    # by Rd8, cannot interpose on e5), Bxf4 2.Sd7# (Bf4 pinned by Rh4); daily No. 8
    sp = [p for p in _patterns('3R3B/1b5K/3N1Np1/4b3/3k1P1R/Q7/3Pnp2/3n3B') if p['name'] == 'Self-pin']
    assert sorted(p['defence'] for p in sp) == ['Bxd6', 'Bxf4']


def test_half_pin_is_not_a_direct_self_pin():
    # in Barnes' half-pin the pinned unit is the one that stayed, not the defender
    assert not [p for p in _patterns('7b/8/1K1p2Q1/3N4/1Nknr2R/P6R/2rp4/B7') if p['name'] == 'Self-pin']


def test_schiffmann_reported_per_defence():
    # Aliovsadzade, Problemesis 2005 (psis-248d80a8fd): 1.Be3! (2.Sf5#) Sxd5 and cxd5 pin themselves on Qh5's rank;
    # 2.Sf5 would close it and the knight could take e3 or the pawn interpose on d4. Not Self-pin-only: the pinner is
    # the line piece beyond the White pawn b5 on the same rank in Kovacevic & Subotic (2000, psis-3f6a82c74a).
    sf = [p for p in _patterns('4B1b1/7R/1pp2nRr/1pkP3Q/1p1NPBp1/1P3N2/2K1P3/8') if p['name'] == 'Schiffmann']
    assert sorted(p['defence'] for p in sf) == ['Sxd5', 'cxd5'] and {p['pinner'] for p in sf} == {'Qh5'}
    sf = [p for p in _patterns('1r1R4/1p1Bp2K/nB1N1bN1/1PpkP2R/3q2P1/1PPn1P2/8/1b1Q4') if p['name'] == 'Schiffmann']
    assert {'Qxe5', 'Sxe5'} <= {p['defence'] for p in sf} and {p['pinner'] for p in sf} == {'Rh5'}


def test_avner_self_pin_is_not_schiffmann():
    # the threat 2.Sd5 lands on no pin line: the self-pins are exploited, not answered by an unpinning threat
    assert not [p for p in _patterns('3R3B/1b5K/3N1Np1/4b3/3k1P1R/Q7/3Pnp2/3n3B') if p['name'] == 'Schiffmann']


def test_knowledge_jsonl_has_no_merge_markers():
    # 12 Oct 2026: a merge left <<<<<<< / ======= / >>>>>>> lines in lessons.jsonl on main
    for name in ('lessons.jsonl',):
        for i, line in enumerate(open(os.path.join(ROOT, 'knowledge', name)), 1):
            assert not line.startswith(('<<<<<<<', '=======', '>>>>>>>')), (name, i)
            if line.strip():
                json.loads(line)


def test_knowledge_files_not_truncated():
    # 18 Oct 2026: a merge resolution written as open(p, 'w').write(f(open(p).read())) emptied lessons.jsonl and
    # session_log.md (the write truncates before the read); never let an empty knowledge file reach main
    import os
    root = os.path.join(os.path.dirname(__file__), '..', 'knowledge')
    for name, least in (('lessons.jsonl', 300), ('session_log.md', 500), ('problems.json', 1000)):
        with open(os.path.join(root, name)) as f:
            assert sum(1 for _ in f) >= least, name
