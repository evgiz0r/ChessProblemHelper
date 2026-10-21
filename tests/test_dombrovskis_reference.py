"""The Dombrovskis theme reference (daily No. 16) cites archive positions; each must solve to the key it names and
the solver must report the paradox on the defences it names, so the reference cannot drift from the solver."""
import os
from chesscomp.core import Problem
from chesscomp.analysis import analyse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, '.claude/skills/themes/references/dombrovskis.md')

CASES = [   # FEN (as printed in the reference), key, defences with the paradox
    ('3n1KB1/3p1n2/2p1k3/8/5P1B/2PQ4/8/8', 'Ke8', {'d6', 'd5'}),              # Slesarenko & Gvozdjak
    ('7n/2K1P3/3B4/3kN3/R2N1r2/5P2/2P2b1Q/7B', 'Qh3', {'Bxd4', 'Rxd4'}),       # Manolescu
    ('8/p2B4/3pN1p1/2Pkpr1Q/4R3/3Kp3/3N4/8', 'Sc4', {'Rf3', 'dxc5'}),          # Onkoud
]


def test_reference_examples_show_the_paradox():
    text = open(REF).read().replace('\n', '').replace(' ', '')
    for fen, key, defs in CASES:
        assert fen in text, fen
        r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), time_limit=60)
        assert r['keys'] == [key], (fen, r['keys'])
        got = {p.get('defence') for p in (r.get('relations') or {}).get('patterns', [])
               if p['name'] == 'Dombrovskis (refutation)'}
        assert defs <= got, (fen, got)
