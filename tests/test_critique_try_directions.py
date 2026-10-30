"""E. Bourd (30 Oct 2026), his knight correction 6Q1/8/4RBn1/5k2/2R5/8/2K4b/8, 1.Bh8!: the bishop's tries along one ray
(1.Bc3?/Bb2?/Ba1? Se5!) are one direction, not three tries with the same refutation."""
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique


def test_tries_along_one_ray_are_one_try():
    p = Problem.from_fen('6Q1/8/4RBn1/5k2/2R5/8/2K4b/8 w - - 0 1', '#2')
    f = critique(p, analyse(p, include_tries=True), necessity=False)['findings']
    assert not any(x['rule'] == 'same refutation' for x in f)
