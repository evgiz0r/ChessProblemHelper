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
