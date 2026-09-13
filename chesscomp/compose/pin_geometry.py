"""Geometry for self-pinning king moves (task from E. Bourd, session 15).

A try by the White king fails because the king's destination completes a pin of one of White's OWN pieces:
    Black line piece P  ...  White piece W  ...  King destination t      (collinear, in that order)
If W is the unit that would mate after the refuting defence, the try is refuted by that defence.

For a given White king square this enumerates every (destination, pinned square, pinner square) triple,
so a composer can pick two destinations whose pins use DIFFERENT White units, plus one destination that
completes no pin at all - which becomes the key.
"""
from __future__ import annotations
import chess

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def _ray(sq, d, maxlen=7):
    f, r = chess.square_file(sq), chess.square_rank(sq)
    out = []
    for i in range(1, maxlen + 1):
        nf, nr = f + d[0] * i, r + d[1] * i
        if not (0 <= nf < 8 and 0 <= nr < 8):
            break
        out.append(chess.square(nf, nr))
    return out


def pin_geometry(king_sq: str, destinations: list[str] | None = None):
    """(destination, pinned White square, pinner Black square, pinner type) for every pin the king
    could walk into."""
    k = chess.parse_square(king_sq)
    dests = [chess.parse_square(x) for x in destinations] if destinations else \
            [s for s in chess.SquareSet(chess.BB_KING_ATTACKS[k])]
    out = []
    for t in dests:
        for d in DIRS:
            ray = _ray(t, d)
            for i, w in enumerate(ray[:-1]):
                for p in ray[i + 1:]:
                    kind = 'B' if d[0] and d[1] else 'R'
                    out.append({'dest': chess.square_name(t), 'pinned': chess.square_name(w),
                                'pinner': chess.square_name(p), 'pinner_type': kind + '/Q'})
    return out


def plan(king_sq: str, pinned_units: list[str]):
    """Given the White units you want pinnable, report which king destinations pin which unit,
    and which destinations pin nothing (candidate keys)."""
    g = pin_geometry(king_sq)
    want = set(pinned_units)
    by_dest = {}
    for e in g:
        if e['pinned'] in want:
            by_dest.setdefault(e['dest'], []).append((e['pinned'], e['pinner'], e['pinner_type']))
    all_dests = {chess.square_name(s) for s in chess.SquareSet(chess.BB_KING_ATTACKS[chess.parse_square(king_sq)])}
    return {'pinning': by_dest, 'clean': sorted(all_dests - set(by_dest))}
