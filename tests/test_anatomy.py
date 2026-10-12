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
    assert 'needed in no mate' in r['Pg2']
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


def test_links_between_variations():
    # Bourd (bench, 11 Oct 2026): the two mating units hold c5 for each other, so the variations are connected
    t = anatomy('nK6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8', tries=1)
    assert 'Sa6 and Qe2 hold c5 for each other: Qe2 alone after Bf6, Sa6 alone after Bg6' in t
    assert 'Sa6 works in the mate after Bg6 (by Qe2): c5' in t


def test_plug_and_occupier_are_needed():
    # Bourd, Sredba 2003-05 1st HM: Pb4 guards nothing but blocks Qa3-d6 (after 1...Se7 2.Sxd6# the queen would take)
    t = anatomy('2n5/1KNp1r2/3p1Q2/pN3br1/1Pp1k1p1/qR4P1/3P1b2/B3nB2', tries=0)
    assert 'needed only as plug/protector/line' in _roles(t)['Pb4']
    assert 'needed in no mate' in _roles(t)['Bf1']              # Bf1 is there for the try 1.Bxc4?
    # Bourd, StrateGems 2007 2nd HM: Pf6 stands on f6, protected by Rf8
    assert 'on f6' in _roles(anatomy('B4R2/2K5/1N2pP2/4k3/2Pr3p/2P2Q2/1b1N4/2B5', tries=0))['Pf6']
