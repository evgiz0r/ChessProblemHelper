"""Text views of a position for a model to read (tools/board_views.py, from the 9 Oct 2026 experiment).

    pytest tests/test_board_views.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import chess
import board_views as bv

# E. Bourd, bourd-selfpin-changed-mates-2 (1.Qh5!): the example in knowledge/experiments/board_views_2026-10-09.md
FEN = '3rN2b/7b/8/n1Q5/1R1Pk1P1/4P3/4K3/8 w - - 0 1'


def test_every_view_renders():
    b = chess.Board(FEN)
    for name, view in bv.VIEWS.items():
        text = view(b)
        assert text.strip(), name
        assert b.fen() == FEN, f'{name} changed the board'


def test_line_views_see_the_half_battery():
    b = chess.Board(FEN)
    assert 'x-ray→ e4[k ENEMY]' in bv.v_annotated(b)                     # Rb4 through d4 to the king
    assert 'BATTERY (discovery possible): wRb4 → through wPd4 to bKe4' in bv.v_salient(b)
    assert 'rank 4: a4=. b4=R c4=. d4=P e4=k' in bv.v_lines(b)


def test_tree1_lists_replies_to_every_check():
    t = bv.v_tree1(chess.Board(FEN))
    assert 'd5+: 3 replies: Bd4 Ke5 Nc4' in t                              # the would-be cook and its refutation
    assert 'Qd5+: 2 replies: Kxd5 Rxd5' in t


def test_cli_accepts_a_bare_fen(capsys):
    bv.main([FEN.split()[0], 'fen'])
    assert 'FEN: ' + FEN in capsys.readouterr().out
