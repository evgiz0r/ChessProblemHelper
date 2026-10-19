"""The front piece of a battery plays the mate: it takes part even when it neither checks nor guards the field
(19 Oct 2026: wPd2 of the rook-pawn battery, 2.d3# and 2.d4#, was called a cook-stopper that takes part in no mate)."""
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique


def test_pawn_front_piece_takes_part():
    p = Problem.from_fen('8/6b1/7N/1b4P1/7K/5P2/R2P1N1k/6R1 w - - 0 1', '#2')
    res = analyse(p)
    assert res['keys'] == ['Sh3']
    text = ' '.join(f['msg'] for f in critique(p, res)['findings'])
    assert 'wPd2 takes part in no mate' not in text
    assert 'wPf3 takes part in no mate' in text      # a real cook-stopper is still named


def test_try_refuted_by_the_king_is_no_second_phase():
    # E. Bourd's 1.Bh2! (19 Oct 2026): 1.Sg3? cuts Rg6 and is refuted by 1...Kg2!; it is not a thematic try
    p = Problem.from_fen('8/K7/4bbR1/2n5/5B2/p3Pp2/R1P2k2/3Q1N2 w - - 0 1', '#2')
    res = analyse(p)
    assert res['keys'] == ['Bh2']
    rules = {f['rule'] for f in critique(p, res)['findings']}
    assert 'thematic tries' not in rules and 'single phase' in rules
