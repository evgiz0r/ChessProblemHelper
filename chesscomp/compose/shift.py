"""Move a whole scheme: every translation (and the file mirror) that keeps all units on the board.

E. Bourd (session 30): "the line/row rotation should be in your toolset" - shifting a scheme one row up can
let a black pawn plug a square that sat on the first rank (b1 -> b2). Pawns may not land on rank 1 or 8, so
only translations and the left-right mirror are offered (a rotation turns pawns sideways).

    python3 -m chesscomp.compose.shift FEN            # list every legal placement
    python3 -m chesscomp.compose.shift FEN 0 1        # one file right 0, one row up 1
    python3 -m chesscomp.compose.shift FEN 0 0 mirror
"""
from __future__ import annotations
import sys
import chess


def shifted(fen: str, df: int, dr: int, mirror: bool = False) -> str | None:
    b = chess.Board(fen.split()[0] + ' w - - 0 1')
    out = chess.Board(None)
    for sq, p in b.piece_map().items():
        f, r = chess.square_file(sq), chess.square_rank(sq)
        if mirror:
            f = 7 - f
        f, r = f + df, r + dr
        if not (0 <= f < 8 and 0 <= r < 8):
            return None
        if p.piece_type == chess.PAWN and r in (0, 7):
            return None
        out.set_piece_at(chess.square(f, r), p)
    return out.board_fen()


def placements(fen: str):
    for mirror in (False, True):
        for df in range(-7, 8):
            for dr in range(-7, 8):
                s = shifted(fen, df, dr, mirror)
                if s:
                    yield df, dr, mirror, s


def main(argv=None):
    a = argv or sys.argv[1:]
    if len(a) >= 3:
        print(shifted(a[0], int(a[1]), int(a[2]), len(a) > 3 and a[3] == 'mirror'))
        return
    for df, dr, m, s in placements(a[0]):
        print(f"{'mirror ' if m else ''}{df:+d} files {dr:+d} rows  {s}")


if __name__ == '__main__':
    main()
