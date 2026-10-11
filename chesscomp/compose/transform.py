"""Shift, rotate or flip a position, and solve every placement of it (E. Bourd, 11 Oct 2026: "notice that im
using shifts and rotations, they do not ruin the base of the theme").

A shift or a rotation keeps the geometry of the line pieces (the thematic lines, the interference squares, the
king's field), so the theme survives it. What it changes is everything that depends on the board's
orientation: pawns (their direction, captures and promotion; a c-file chain becomes a 6th-rank chain), the
colour of each bishop (both swap together under a quarter turn, so the pair survives), and the edges (room
for the White king, out-of-play corners). On his bench (11 Oct 2026, session mv4dvvuh) a quarter turn turned
a black c2/c3/c4 chain, which checked the White king, captured on b3 and promoted, into a static b6/c6/d6
chain whose pawns became the targets of the thematic queen mates; three changes later the problem was sound.

    python3 -m chesscomp.compose.transform FEN --rot 90 [--shift 1,-1] [--flip]   # one placement, printed
    python3 -m chesscomp.compose.transform FEN --all --post                         # rank every placement
    python3 -m chesscomp.compose.transform FEN --all --pre [--top 12]

--rot 90 is a clockwise quarter turn (a1 -> a8), --rot 270 the other way, --rot 180 the half turn. --flip is
the top/bottom flip (rank 1 <-> rank 8, pawns keep their colour and change direction); the left/right mirror
changes nothing in orthodox play and is never generated.

--all generates the four orientations that differ in play (as is, flipped, the two quarter turns) times
every shift that keeps all units on the board with no pawn on the first or last rank, and solves each one:
--post (Black to move, a post-key position) counts threats, holes and dual defences, --pre (White to move,
a diagram) counts the keys. The units' roles are unchanged only up to the orientation, so a placement is a
proposal to look at, not a result.
"""
from __future__ import annotations
import sys, argparse
import chess

from .keyfind import post_spec

ORIENTATIONS = {                        # (file, rank) -> (file, rank), 0-based
    'id': lambda f, r: (f, r),
    'flip': lambda f, r: (f, 7 - r),
    'rot90': lambda f, r: (r, 7 - f),   # clockwise: a1 -> a8, h1 -> a1
    'rot270': lambda f, r: (7 - r, f),
    'rot180': lambda f, r: (7 - f, 7 - r),
}


def transform(board_fen: str, orient: str = 'id', dx: int = 0, dy: int = 0) -> str | None:
    """The placement of `board_fen` turned by `orient` then shifted by (dx, dy); None if a unit leaves the
    board or a pawn lands on the first or last rank."""
    src = chess.BaseBoard(board_fen)
    dst = chess.BaseBoard(None)
    fn = ORIENTATIONS[orient]
    for sq, pc in src.piece_map().items():
        f, r = fn(chess.square_file(sq), chess.square_rank(sq))
        f, r = f + dx, r + dy
        if not (0 <= f < 8 and 0 <= r < 8):
            return None
        if pc.piece_type == chess.PAWN and r in (0, 7):
            return None
        dst.set_piece_at(chess.square(f, r), pc)
    return dst.board_fen()


def placements(board_fen: str, orients=('id', 'flip', 'rot90', 'rot270')):
    """Every (orient, dx, dy, fen) that keeps the position on the board, the given placement first."""
    seen = set()
    for o in orients:
        for dx in range(-7, 8):
            for dy in range(-7, 8):
                fen = transform(board_fen, o, dx, dy)
                if fen and fen not in seen:
                    seen.add(fen)
                    yield o, dx, dy, fen


def post_metrics(fen: str):
    """(threats, holes, duals, checks) of a post-key placement, Black to move; None if illegal."""
    b = chess.Board(fen + ' b - - 0 1')
    if not b.is_valid():                # also rejects White in check with Black to move
        return None
    threat, defs = post_spec(fen)
    holes = [u for u, m in defs.items() if not m]
    duals = [u for u, m in defs.items() if len(m) > 1]
    checks = [m.uci() for m in b.legal_moves if b.gives_check(m)]
    return len(threat), len(holes), len(duals), len(checks), defs


def pre_keys(fen: str, time_limit: float = 20):
    from ..core import Problem
    from ..analysis import analyse
    b = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid():
        return None
    try:
        res = analyse(Problem.from_fen(b.fen(), '#2'), include_tries=False, include_set=False,
                      time_limit=time_limit)
    except Exception:
        return None
    return res.get('keys') or []


def _san(fen: str, uci: str) -> str:
    b = chess.Board(fen + ' b - - 0 1')
    return b.san(chess.Move.from_uci(uci))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('fen', help='board part of a FEN (anything after the first space is ignored)')
    ap.add_argument('--rot', choices=['0', '90', '180', '270'], default='0')
    ap.add_argument('--flip', action='store_true')
    ap.add_argument('--shift', default='0,0', help='dx,dy in files and ranks, e.g. 1,-1')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--post', action='store_true')
    ap.add_argument('--pre', action='store_true')
    ap.add_argument('--top', type=int, default=12)
    a = ap.parse_args(argv)
    fen = a.fen.split()[0]
    if not a.all:
        out = fen
        if a.flip:
            out = transform(out, 'flip')
        if a.rot != '0' and out:
            out = transform(out, 'rot' + a.rot)
        dx, dy = (int(x) for x in a.shift.split(','))
        if out:
            out = transform(out, 'id', dx, dy)
        if not out:
            print('off the board (or a pawn on the first or last rank)')
            return 1
        print(out)
        if a.post:
            m = post_metrics(out)
            print('illegal' if m is None else f'threats {m[0]}, holes {m[1]}, duals {m[2]}, black checks {m[3]}')
        if a.pre:
            print('keys:', pre_keys(out))
        return 0
    rows = []
    for o, dx, dy, f in placements(fen):
        if a.pre:
            k = pre_keys(f)
            if k is None:
                continue
            rows.append(((len(k) != 1, len(k)), o, dx, dy, f, f"keys {', '.join(k) or 'none'}"))
        else:
            m = post_metrics(f)
            if m is None:
                continue
            t, h, d, c, defs = m
            hole = [_san(f, u) for u, mm in defs.items() if not mm]
            rows.append(((t != 1, h, d, c, t), o, dx, dy, f,
                         f"threats {t}, holes {h}{' (' + ' '.join(hole[:6]) + ')' if hole else ''}, "
                         f"duals {d}, black checks {c}"))
    rows.sort(key=lambda r: r[0])
    for r in rows[:a.top]:
        print(f"{r[1]:6} shift {r[2]:+d},{r[3]:+d}  {r[4]}  {r[5]}")
    print(f"({len(rows)} legal placements)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
