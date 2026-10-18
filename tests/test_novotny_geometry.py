"""Single-threat Novotny geometry (daily No. 13, 18 Oct 2026): each mating square is held by both black line pieces."""
import chess
from chesscomp.compose.novotny_geometry import geometries
from chesscomp.core import Problem
from chesscomp.analysis import analyse


def names(g):
    return tuple(chess.square_name(s) for s in g)


def test_daily_13_geometry_is_listed_and_symmetric():
    gs = {names(g) for g in geometries(chess.E4)}
    assert ('e4', 'c6', 'e7', 'd6', 'c5', 'f6') in gs
    assert len(gs) == 8                          # one geometry, its eight images around the king
    assert all(g[3] not in {'d3', 'd4', 'd5', 'e3', 'e5', 'f3', 'f4', 'f5'} for g in gs)


def test_lines_option_adds_line_mates():
    assert len(geometries(chess.E4, lines=True)) > len(geometries(chess.E4))


def test_daily_13_position_separates_the_captures():
    r = analyse(Problem.from_fen('8/1p1Nb3/1Nr3R1/8/4k1P1/4P3/4PPK1/B7 w - - 0 1', '#2'),
                include_tries=False, include_set=False, time_limit=20)
    assert r['keys'] == ['Rd6']
