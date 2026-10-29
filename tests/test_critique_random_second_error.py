"""E. Bourd (29 Oct 2026) on 1...Re4 2.Sxf5#/Rd3# in his rook correction: a move of the correcting piece that keeps
the random error and adds another corrects nothing, so its second mate is not a flaw."""
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique

BOURD = '1B6/2Q1p3/1p5N/1p2rp2/1N1k4/4R3/5K2/b7 w - - 0 1'


def _items(fen):
    p = Problem.from_fen(fen, '#2')
    res = analyse(p, max_refutations=1, include_tries=True, include_set=True, time_limit=60)
    return critique(p, res, necessity=False)['findings']


def test_random_move_with_a_second_error_is_a_note_not_a_dual():
    items = _items(BOURD)
    assert not any(i['rule'] == 'dual' for i in items)
    note = [i for i in items if i['rule'] == 'random move with a second error']
    assert note and note[0]['severity'] == 'note' and 'Re4' in note[0]['msg']
