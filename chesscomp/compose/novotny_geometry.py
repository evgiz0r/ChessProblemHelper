"""Geometries for a Novotny with a single threat (daily No. 13, 18 Oct 2026), before any unit is placed.

The classic #2 Novotny threatens two mates, one stopped by each capture; the gate calls a double threat fatal, so
the single-threat form needs another reason for each mate to fail before its capture. Shire (The Problemist 1997,
psis-1e6c532522) uses the capturer's departure opening a white line through its origin. This tool lists the other
reason, a double guard: each mating square is held by both black pieces. Square A is guarded by the rook along its OTHER line (lost when the rook leaves r0 along its line to X) and
by the bishop through X (cut when the rook stands on X); square B the same way with the colours swapped. So
1...RxX allows only the mate on A and 1...BxX only the mate on B, and before either capture both squares are held:
the separation is built in, and the threat can be anything the white unit on X makes (it is captured in both).

For a black king square it lists K, r0, b0, X, A, B with A and B knight-check squares (default) or, with --lines,
any square on a line to the king (a line piece mates there; check the path yourself). X is kept off the king's
field, and neither guard may pass through the king.

    python3 -m chesscomp.compose.novotny_geometry e4 [--lines]

Example: e4 c6 e7 d6 c5 f6 -> Ke4, bRc6, bBe7, white unit on d6, a knight on d7 reaching both:
1...Rxd6 2.Sc5#, 1...Bxd6 2.Sf6# (daily No. 13).
"""
from __future__ import annotations
import argparse
import chess

ROOK = [(1, 0), (-1, 0), (0, 1), (0, -1)]
BISHOP = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def ray(sq: int, d: tuple[int, int]) -> list[int]:
    f, r, out = chess.square_file(sq), chess.square_rank(sq), []
    while True:
        f += d[0]; r += d[1]
        if not (0 <= f < 8 and 0 <= r < 8):
            return out
        out.append(chess.square(f, r))


def _reaches(rays: list[list[int]], s: int, king: int) -> bool:
    for ry in rays:
        for t in ry:
            if t == s:
                return True
            if t == king:
                break
    return False


def mating_squares(king: int, lines: bool = False) -> set[int]:
    out = set(chess.SquareSet(chess.BB_KNIGHT_ATTACKS[king]))
    if lines:
        for d in ROOK + BISHOP:
            out |= set(ray(king, d))
    return out


def geometries(king: int, lines: bool = False) -> list[tuple[int, int, int, int, int, int]]:
    """(K, r0, b0, X, A, B): A is held by the rook's other line from r0 and the bishop through X, B by the bishop's
    other diagonal from b0 and the rook through X."""
    field = set(chess.SquareSet(chess.BB_KING_ATTACKS[king]))
    mates = mating_squares(king, lines) - field if lines else mating_squares(king)
    out = []
    for r0 in chess.SQUARES:
        if r0 == king or r0 in field:
            continue
        for dr in ROOK:
            pr = ray(r0, dr)
            for i, x in enumerate(pr):
                if x == king:
                    break
                if x in field:
                    continue
                perp_r = [ray(r0, d) for d in ROOK if d not in (dr, (-dr[0], -dr[1]))]
                for b0 in chess.SQUARES:
                    if b0 in (r0, king, x) or b0 in field:
                        continue
                    for db in BISHOP:
                        pb = ray(b0, db)
                        if x not in pb:
                            continue
                        j = pb.index(x)
                        if king in pb[:j] or r0 in pb[:j] or b0 in pr[:i]:
                            continue
                        perp_b = [ray(b0, d) for d in BISHOP if d not in (db, (-db[0], -db[1]))]
                        for a in pb[j + 1:]:
                            if a == king:
                                break
                            if a not in mates or not _reaches(perp_r, a, king):
                                continue
                            for b in pr[i + 1:]:
                                if b == king:
                                    break
                                if b in mates and b != a and _reaches(perp_b, b, king):
                                    out.append((king, r0, b0, x, a, b))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('king')
    ap.add_argument('--lines', action='store_true', help='also mating squares on lines to the king')
    a = ap.parse_args(argv)
    gs = geometries(chess.parse_square(a.king), a.lines)
    print('K   rook bishop X   A(after RxX) B(after BxX)')
    for g in gs:
        print('   '.join(chess.square_name(s) for s in g))
    print(len(gs), 'geometries')


if __name__ == '__main__':
    main()
