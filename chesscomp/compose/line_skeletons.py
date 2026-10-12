"""Skeletons for "one black knight, several defences, each closing a different black line" (E. Bourd's theme,
12 Oct 2026), before any unit is placed.

For a black king square K it lists: the threat square T (where White's mate lands: next to the king, a knight
check square, or on a line to the king), the knight's square O, two arrival squares A1, A2 that are knight moves
from O and both guard T (the defence), and for each Ai the black lines through it that guard a square Mi of the
king's field beyond Ai (closing the line at Ai is the error; White mates on or through Mi). Arrival squares and O
are kept off the king's field (E. Bourd: keep the mechanism apart).

    python3 -m chesscomp.compose.line_skeletons d5 [--t e3]

Example (12 Oct 2026): T e3, O e1, A c2/g2: Sc2 closes Rc1's file (c3 unguarded: 2.Sxc3#), Sg2 closes Bh1's
diagonal (e4 unguarded: 2.Qe4#) -> 4Q3/6p1/8/2Pk4/2R5/1Pp3K1/3N4/1Nr1n2b, 1.Sf1! (2.Se3#).
"""
from __future__ import annotations
import argparse, itertools
import chess

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def knight(s: int) -> set[int]:
    return set(chess.SquareSet(chess.BB_KNIGHT_ATTACKS[s]))


def field(k: int) -> set[int]:
    return set(chess.SquareSet(chess.BB_KING_ATTACKS[k]))


def lines_through(a: int, k: int) -> list[tuple[str, int]]:
    """(line kind R/B, first square of the king's field beyond a) for every line through a that reaches the field."""
    out = []
    for dx, dy in DIRS:
        x, y = chess.square_file(a) + dx, chess.square_rank(a) + dy
        while 0 <= x < 8 and 0 <= y < 8:
            s = chess.square(x, y)
            if s == k:
                break
            if s in field(k):
                bx, by = chess.square_file(a) - dx, chess.square_rank(a) - dy
                if 0 <= bx < 8 and 0 <= by < 8:            # room behind a for the black line piece
                    out.append(('R' if dx == 0 or dy == 0 else 'B', s))
                break
            x, y = x + dx, y + dy
    return out


def checks_from(t: int, k: int) -> bool:
    df, dr = chess.square_file(t) - chess.square_file(k), chess.square_rank(t) - chess.square_rank(k)
    return t in field(k) or t in knight(k) or df == 0 or dr == 0 or abs(df) == abs(dr)


def skeletons(k: int, only_t: int | None = None):
    for t in chess.SQUARES:
        if t == k or not checks_from(t, k) or (only_t is not None and t != only_t):
            continue
        for o in chess.SQUARES:
            if o in (k, t) or o in field(k):
                continue
            arr = sorted(a for a in knight(o) & knight(t) if a != k and a not in field(k))
            for a1, a2 in itertools.combinations(arr, 2):
                pairs = sorted({(k1, m1, k2, m2) for k1, m1 in lines_through(a1, k) for k2, m2 in lines_through(a2, k)
                                if m1 != m2})
                if pairs:
                    yield t, o, a1, a2, pairs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('king'); ap.add_argument('--t', help='only this threat square')
    a = ap.parse_args(argv)
    k = chess.parse_square(a.king)
    n = chess.square_name
    for t, o, a1, a2, pairs in skeletons(k, chess.parse_square(a.t) if a.t else None):
        print(f"T {n(t)}  S{n(o)} -> {n(a1)},{n(a2)}  errors: "
              + ' '.join(f"{k1}->{n(m1)}/{k2}->{n(m2)}" for k1, m1, k2, m2 in pairs))


if __name__ == '__main__':
    main()
