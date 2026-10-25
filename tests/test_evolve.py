"""The evolutionary search: its Black correction mode scores and recognises a correction problem."""
import os, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROBE = """
import chess, chesscomp.compose.evolve as e
for fen in ('2BkNK2/N2p4/3n4/8/8/4p3/4QB2/4b3', '2BkNK2/N2p4/3n4/8/8/4p3/4Q3/4b3'):
    s, summ, hit = e.score(chess.Board(fen + ' w - - 0 1'))
    print(hit, summ)
"""


def _probe(ncorr):
    env = dict(os.environ, CORR='d6', NCORR=str(ncorr), DEFS='', PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.splitlines()


def test_correction_mode_hits_marin_with_one_correction():
    # Marin y Llovet 1921: 1.Qd2! S~ 2.Qxd7#, 1...Sxc8! 2.Sc6#
    sound, unsound = _probe(1)
    assert sound.startswith('True') and 'S~ Qxd7#' in sound and 'Sxc8:Sc6#' in sound
    assert unsound.startswith('False')          # without Bf2 there is no key


def test_correction_mode_demands_ncorr_corrections():
    assert _probe(2)[0].startswith('False')


KEYROLE_PROBE = """
import chess, chesscomp.compose.evolve as e
s, summ, hit = e.score(chess.Board('3R4/8/6K1/4P3/3bk3/N1p3Q1/8/8 w - - 0 1'))
print(hit, round(s, 1), summ)
"""


def _keyrole(flag):
    env = dict(os.environ, CORR='d4', NCORR='2', DEFS='', KEYROLE=flag, PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', KEYROLE_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    hit, sc = r.stdout.split()[:2]
    return hit == 'True', float(sc)


def test_out_of_play_key_is_no_hit():
    # daily No. 2: 1.Sc4! by the a3 knight, out of play (E. Bourd: fatal). The search returned it as a HIT.
    old_hit, old_score = _keyrole('0')
    new_hit, new_score = _keyrole('1')
    assert old_hit and not new_hit and new_score < old_score - 20


SB_PROBE = """
import chess, chesscomp.compose.evolve as e
for fen in ('2R5/3n1p2/1B6/1K1kP1Q1/1P4B1/4rP2/8/8', '8/3N3K/2b4p/kBR2p2/1p1Q4/8/8/5q2'):
    s, summ, hit = e.score(chess.Board(fen + ' w - - 0 1'))
    print(hit, summ)
"""


def _selfblock(n):
    env = dict(os.environ, SELFBLOCK=str(n), SBSECOND='0', DEFS='', PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', SB_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.splitlines()


def test_selfblock_mode_counts_functional_self_blocks():
    # daily No. 3: 1.Qe7! Rxe5 2.Qxd7# needs the rook on e5 (the king would take it); Sxe5 2.Qc5# is an unguard
    no3, ceskova = _selfblock(1)
    assert no3.startswith('True') and 'SB Qxd7#' in no3
    # Ceskova 1901: the captures on b5 stand next to the king but Rc5 guards b5 anyway, so no self-block
    assert ceskova.startswith('False') and 'SB  ' in ceskova


def test_selfblock_mode_demands_n_mates():
    assert _selfblock(2)[0].startswith('False')


def test_selfblock_mode_wants_a_second_layer():
    # daily No. 17's capture threat: 1.Qc3! Rxd4... a self-block mate (Qe5#) but a single phase, which the gate fails;
    # SBSECOND (default) refuses it as a HIT, as FSECOND does in FLIGHT mode
    fen = '8/B7/8/5p2/2Prkp2/1Q3N1K/6P1/8'
    hit, sc, summ = _score(fen, SELFBLOCK='1', SBSECOND='0')
    assert hit and 'SB Qe5#' in summ
    hit, sc, summ = _score(fen, SELFBLOCK='1')
    assert not hit and 'changed=0 tries=-' in summ
    # daily No. 5: the try 1.Sd6? Rxd6! is answered after the key (2.Qf5#): a second layer, still a HIT
    hit, sc, summ = _score('3r1r2/4p3/5pR1/3PkNBp/2R4P/5B1Q/4n2K/8', SELFBLOCK='1')
    assert hit and 'Sd6?Rxd6' in summ


HALFPIN = """
import chess, chesscomp.compose.evolve as e
s, summ, hit = e.score(chess.Board('b2N4/Q3K3/8/3kpp2/4n1p1/1P3r2/3P4/2R4B w - - 0 1'))
print(hit)
"""


def test_pattern_mode_without_defs_counts_distinct_half_pin_mates():
    # daily No. 7: 1.Qa6! Sd6/Sxd2 Qd3#, Rc3 Qd6# - two distinct half-pin mates, not three
    out = {}
    for n in (2, 3):
        env = dict(os.environ, PATTERN='Half-pin', DEFS='', NPAT=str(n), PYTHONPATH=ROOT)
        r = subprocess.run([sys.executable, '-c', HALFPIN], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
        assert r.returncode == 0, r.stderr
        out[n] = r.stdout.split()[-1]
    assert out == {2: 'True', 3: 'False'}


KEYPROBE = """
import chess, chesscomp.compose.evolve as e
s, summ, hit = e.score(chess.Board('3R4/4P1B1/8/4Pp2/4k1n1/6Q1/8/1K6 w - - 0 1'))
print(summ, hit)
"""


def test_key_mode_fixes_the_key_and_counts_mates():
    # daily No. 9 search: 1.e8=S! S~ 2.Sf6#, 1...Sf6 2.Sxf6#, 1...f4 2.Qd3# - three distinct mates; 1.e8=Q? Se3!
    out = {}
    for key, n in (('e7e8n', 3), ('e7e8n', 4), ('e7e8q', 1)):
        env = dict(os.environ, KEY=key, NVAR=str(n), DEFS='', PYTHONPATH=ROOT)
        r = subprocess.run([sys.executable, '-c', KEYPROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
        assert r.returncode == 0, r.stderr
        out[(key, n)] = r.stdout.split()[-1]
    assert out == {('e7e8n', 3): 'True', ('e7e8n', 4): 'False', ('e7e8q', 1): 'False'}


BRISTOL_PROBE = """
import chess, chesscomp.compose.evolve as e
s, summ, hit = e.score(chess.Board('1Q6/R1Bpb3/2p5/6p1/1p1P4/1k6/N7/2K2B2 w - - 0 1'))
print(hit, summ)
"""


def _bristol(key):
    env = dict(os.environ, KEY=key, BRISTOL='1', NVAR='2', DEFS='', PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', BRISTOL_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_bristol_mode_hits_bourd_prototype_with_thematic_tries():
    # E. Bourd's Bristol prototype: 1.Bh2! (2.Qg3#), tries 1.Bd8? Bd6! and 1.Bb6? d6!, both answered after the key
    out = _bristol('c7h2')
    assert out.startswith('True') and 'bristol=yes' in out and 'thematic-tries=Bd6/d6' in out


def test_bristol_mode_refuses_a_non_bristol_threat():
    # 1.Bb6? also threatens 2.Qg3#, but the queen does not follow the bishop's line
    assert _bristol('c7b6').startswith('False')


def _tries(key, n):
    env = dict(os.environ, KEY=key, TRIES=str(n), NVAR='2', DEFS='', PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', BRISTOL_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_tries_mode_counts_answered_refutations_without_bristol():
    # daily No. 12: TRIES=N scores the key piece's tries on their own (Bd8? Bd6!, Bb6? d6!), whatever the threat's line
    out = _tries('c7h2', 2)
    assert out.startswith('True') and 'tries=Bd6/d6' in out
    assert _tries('c7h2', 3).startswith('False')


DEFS_PROBE = "import chesscomp.compose.evolve as e; print(','.join(e.DEFS))"


def _defs(**env_extra):
    env = {k: v for k, v in os.environ.items() if k not in ('DEFS', 'PATTERN', 'CORR', 'WCORR', 'KEY', 'DEFSQ', 'SELFBLOCK')}
    env.update(env_extra, PYTHONPATH=ROOT, BUDGET_S='0')
    r = subprocess.run([sys.executable, '-c', DEFS_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''


def test_modes_without_defs_start_with_none():
    # daily No. 16: PATTERN=... NPAT=2 with DEFS unset searched for the default d6,d5
    assert _defs(PATTERN='Dombrovskis (refutation)') == ''
    assert _defs(SELFBLOCK='2') == ''
    assert _defs() == 'd6,d5'                                   # the plain mode keeps its documented default
    assert _defs(PATTERN='Dombrovskis (refutation)', DEFS='e6,e5') == 'e6,e5'


BLOCK_PROBE = """
import chess, chesscomp.compose.evolve as e
s, summ, hit = e.score(chess.Board('{fen} w - - 0 1'))
print(hit, round(s, 1), summ)
"""


def _score(fen, **env):
    env = dict(os.environ, DEFS='', PYTHONPATH=ROOT, **env)
    r = subprocess.run([sys.executable, '-c', BLOCK_PROBE.format(fen=fen)], capture_output=True, text=True, env=env,
                       cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    hit, sc, summ = r.stdout.strip().split(' ', 2)
    return hit == 'True', float(sc), summ


def test_simple_block_is_no_hit():
    # daily No. 17: 1.Qb5! (zugzwang) R~ 2.Sxd2#, Rd5 2.Qe2#, Rc4 2.Qxc4#, the rook the only Black unit with moves: the gate
    # fails it as a 'simple block', and the search returned it as a HIT
    fen = '8/B7/8/4PpP1/3rkp2/1Q3N2/3p4/3K3B'
    old_hit, old_score, _ = _score(fen, CORR='d4', NCORR='2', CTHREAT='0')
    new_hit, new_score, _ = _score(fen, CORR='d4', NCORR='2')
    assert old_hit and not new_hit and new_score < old_score


def test_try_refuted_by_correction_scores():
    # claude-knight-correction: 1.Qc4! S~ 2.Qc7#, Sxd4 2.Qxd4#; the try 1.Qc2? fails only to the correction Sxd4!
    fen = 'b3N3/8/ppn1p3/4k3/3R2P1/4P3/7K/2Q5'
    _, base, _ = _score(fen, CORR='c6', NCORR='1')
    _, s1, summ = _score(fen, CORR='c6', NCORR='1', CTRY='1')
    assert 'try Qc2? Sxd4!' in summ and s1 == base + 12
    assert not _score(fen, CORR='c6', NCORR='1', CTRY='2')[0]


SETDUAL_PROBE = """
import chess, chesscomp.compose.evolve as e
from chesscomp import Problem
from chesscomp.analysis import analyse
for fen in ('8/8/5R2/K3p3/1N1Pk3/2Q3p1/5n2/8', '8/8/5R2/K3p3/1N1Pk3/6p1/3Q1n2/8'):
    r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_set=True, include_tries=False)
    sp = [ph for ph in r['phases'] if ph['type'] == 'set'][0]
    print(','.join(e.set_duals(e.var_map(sp), ['exd4', 'Sd3'])) or '-')
"""


def test_changed_mode_sees_set_duals():
    # claude-knight-swap-c2: set 1...exd4 2.Qe1# alone; with the queen on d2 the set mate splits into Qf4/Qe2/Qe1
    env = dict(os.environ, CHANGED='1', DEFS='exd4,Sd3', PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', SETDUAL_PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ['-', 'exd4']


def test_flight_mode_counts_given_flights_and_wants_a_second_layer():
    # claude-two-flight-knight-sacrifice: 1.Se4! (2.Qc4#) Kxe6 2.Qc6#, Kxe4 2.Qd3#: two flights given by the key, each
    # with its own mate. It has neither a set change nor a thematic try, so FSECOND (the gate's single phase) refuses it.
    fen = '2R2B1b/8/4P1bN/2Nkp3/p4p2/2Q5/3K4/8'
    hit, sc, summ = _score(fen, FLIGHT='2', FSECOND='0')
    assert hit and 'Kxe6:Qc6#' in summ and 'Kxe4:Qd3#' in summ
    assert not _score(fen, FLIGHT='2')[0]
    assert not _score(fen, FLIGHT='3', FSECOND='0')[0]


def test_flight_mode_hits_kisis_with_a_try_and_a_change():
    # Kisis, Heureka! 1992-93, 3rd Prize: 1.Bb1! (2.Rd2#) Kd5 2.Rc5#, Bg4 2.Rf2#; try 1.Rd2? Bg4! - the gate's second phase
    hit, sc, summ = _score('1b6/5N1n/1B2p3/1p3b1Q/4k3/4P3/B1R5/2N4K', FLIGHT='1')
    assert hit and 'Kd5:Rc5#' in summ and 'Rd2?Bg4' in summ


def test_flight_mode_ignores_a_change_between_two_tries():
    # daily No. 19: bPf6 added to claude-two-flight-knight-sacrifice changes 1...e4 between 1.Sf5? (Qd4#) and 1.Sa6? (Sc7#)
    hit, sc, summ = _score('2R2B1b/8/4PpbN/2Nkp3/p4p2/2Q5/3K4/8', FLIGHT='2')
    assert not hit and 'changed=0' in summ


def test_flight_mode_refuses_promotion_tries_and_thin_play():
    # daily No. 19's first hit: 1.Qc3! (zugzwang) Kf4/d4 2.Qf3#, its 'change' against the try 1.c8=B? (d4 Bb7#)
    hit, sc, summ = _score('7B/2P5/4p1K1/3pN3/2p1k3/8/3Q4/8', FLIGHT='1')
    assert not hit and 'changed=0' in summ
