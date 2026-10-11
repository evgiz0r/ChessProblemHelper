"""The anatomy view (chesscomp.anatomy): guard fields, essential pins, idle units, refutation reasons.

    pytest tests/test_anatomy.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chesscomp.anatomy import anatomy


def _roles(text):
    return {l.split()[0]: l for l in text.split('ROLES')[1].splitlines()[1:] if l.strip()}


def test_try_only_pawn_is_flagged():
    # Bourd: Pg2 covers f3 only together with the queen in the solution; it is there for 1.Be3? (2.Qe6#)
    r = _roles(anatomy('8/2K5/B7/8/4k3/7Q/6P1/6B1', tries=1))
    assert 'never needed alone' in r['Pg2']
    assert 'Kc7' in r and 'no part' not in r['Kc7']      # the white king guards d6 after 1...Ke5


def test_pinner_has_a_role():
    # Milewski (Boros): Bh2 guards nothing alone, but pins the defender that self-pins on c7
    t = anatomy('1k1b4/1r1P4/Q7/4R2K/5Rp1/8/7B/8', tries=1)
    assert 'pin: Bh2 holds bd8 on c7' in t and 'pin: Bh2 holds rb7 on c7' in t
    assert 'pin@c7' in _roles(t)['Bh2']


def test_unit_only_for_a_try():
    # Slesarenko & Gvozdjak: Pc3 works only in the try 1.c4?
    assert 'no part' in _roles(anatomy('3n1KB1/3p1n2/2p1k3/8/5P1B/2PQ4/8/8', tries=1))['Pc3']


def test_refutation_reason_and_stalemate():
    t = anatomy('8/1R5n/2p5/2k3N1/4Q3/K7/8/8', tries=1)     # Labai: 1.Kb3? Sf6! interposes on d5
    assert 'sh7 interposes on d5' in t
    t = anatomy('R7/4N3/4p3/1k1nR3/3B3Q/1PP5/8/5K2', tries=1)  # Rice: Black has no move in the diagram
    assert 'stalemate: Black has no move' in t
    assert 'pin: Re5 holds sd5 on d5' in t                   # 1...Kxc5 walks into the pin
