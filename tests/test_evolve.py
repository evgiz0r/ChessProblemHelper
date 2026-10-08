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
