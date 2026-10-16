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
    env = dict(os.environ, SELFBLOCK=str(n), DEFS='', PYTHONPATH=ROOT)
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
