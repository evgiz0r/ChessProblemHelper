"""E. Bourd, 28 Oct 2026, on his bPf6 in the rotated half-pin (the critique had called it 'not needed'): "i put the f6
pawn to avoid the nf6 defense as a thematic 'dual', and somewhat nasty recapture qxf6. i thought it was worth a pawn"."""
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import piece_necessity

BOURD = 'b7/3p1K2/Q4pB1/R1bnkN2/7R/q1np4/5N2/3r4 w - - 0 1'   # 1.Qc4! Se3 Qd4#, Bxf2 Qf4#, Bd4 Qxd4#


def test_unit_that_keeps_a_defence_unique_is_needed():
    p = Problem.from_fen(BOURD, '#2')
    nec = piece_necessity(p, analyse(p, include_tries=True, include_set=True))
    assert nec['f6'].startswith('needed for the CONTENT')
    assert '1...Sf6 repeats the mate of 1...Se3' in nec['f6']
    assert nec['a8'].startswith('not needed')            # the bishop a8 changes nothing


def test_unit_that_holds_the_set_play_dual_avoidance_says_so():
    # bQa3: the bishop's departure from c5 opens a3-d6, so 1...Bxf2 meets 2.Qxf6# alone (E. Bourd, 28 Oct 2026:
    # "the queen is part of the mechanism ... it serves the dual avoidance in the set play"); it also stops cooks
    p = Problem.from_fen(BOURD, '#2')
    nec = piece_necessity(p, analyse(p, include_tries=True, include_set=True))
    assert "set play's dual avoidance" in nec['a3'] and 'Qd6#' in nec['a3']
