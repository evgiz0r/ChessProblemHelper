"""Picture views (tools/board_pictures.py): the text views drawn on the board. SVG only; PNG rendering needs Chromium.

    pytest tests/test_board_pictures.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import chess
import board_pictures as bp

FEN = '3rN2b/7b/8/n1Q5/1R1Pk1P1/4P3/4K3/8 w - - 0 1'   # E. Bourd, bourd-selfpin-changed-mates-2


def test_rays_draw_lines_of_sight_and_xrays():
    s = bp.svg(chess.Board(FEN), 'rays')
    assert s.count('<line') > 30
    assert 'stroke-dasharray' in s                              # Rb4 x-ray through d4 to the king


def test_arrows_only_between_units():
    b = chess.Board(FEN)
    n = sum(1 for s, p in b.piece_map().items() for t in b.attacks(s) if b.piece_at(t))
    assert bp.svg(b, 'arrows').count('<line') == n


def test_field_marks_flights_under_the_pieces():
    b = chess.Board('4k3/R7/8/8/8/8/8/4K3 w - - 0 1')          # king e8: the rook guards d7 e7 f7; d8 f8 free
    s = bp.svg(b, 'field')
    assert s.count('fill="#ffd400"') == 2
    assert s.index('fill="#ffd400"') < s.index('<use ')         # shading drawn before the pieces
