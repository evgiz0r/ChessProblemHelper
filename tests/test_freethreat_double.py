"""freethreat DOUBLE mode counts mates that are double checks (E. Bourd, 21 Oct 2026: "double check mates")."""
import chess
from chesscomp.compose import freethreat as ft
from chesscomp.compose.keyfind import post_spec


def test_double_check_mates_are_counted():
    # Bie, Springaren 2001, 3rd Prize, after 1.Qa1!: every mate is a rook double check
    post = '3r3B/6R1/N1Bnp3/p7/3k1b2/Np1p3r/1R3P1p/Q6K'
    _, d = post_spec(post)
    b = chess.Board(post + ' b - - 0 1')
    names = {b.san(chess.Move.from_uci(u)): m for u, m in d.items()}
    dbl = ft.double_mates(b, names)
    assert {'Rb2c2', 'Rg7g5', 'Rg7g4', 'Rb2d2', 'Rg7d7'} <= dbl
