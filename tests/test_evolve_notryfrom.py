"""NOTRYFROM (E. Bourd, 30 Oct 2026): tries by the units on those squares do not count for CTRY or DEFTRIES, so a search
is not paid for tries that only take a guard away (1.Qd8? Sf3! in claude-knight-selfblock-kh5)."""
import os, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROBE = """
import chesscomp.compose.evolve as e
key = {'type': 'key', 'first_move': {'uci': 'g6h5', 'san': 'Kh5'},
       'variations': [{'defence': {'uci': 'g5f3', 'san': 'Sf3'}, 'continuations': [{'san': 'Be3#'}], 'threat_repeat': False}]}
qtry = {'type': 'try', 'first_move': {'uci': 'g8d8', 'san': 'Qd8'}, 'refutations': [{'uci': 'g5f3', 'san': 'Sf3'}]}
print(e.corr_tries([key, qtry])[0], sorted(e.def_tries([key, qtry], ['Sf3'])[0]))
"""


def _probe(notry):
    env = dict(os.environ, CORR='g5', NOTRYFROM=notry, PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, '-c', PROBE], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_notryfrom_drops_tries_by_that_unit():
    assert _probe('') == "1 ['Sf3']"
    assert _probe('g8') == "0 []"
