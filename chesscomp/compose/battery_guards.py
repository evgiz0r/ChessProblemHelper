"""Where can a black piece hold a battery and lose it by capturing one of two White guards? (E. Bourd's bench idea,
mvcc8z65, 17 Oct 2026: "a battery which is defended by a piece. when that black piece defends twice, it makes some kind
of unguard. that unguard forces a specific battery move, that guards that square".)

The battery (REAR behind FRONT against the black king) is fixed. For every square of the black piece P and every pair of
White guards W1 (guards SQ1, not SQ2) and W2 (guards SQ2, not SQ1) of the given types it keeps the configurations where:
P reaches a square of the battery line after the front piece leaves (it interposes), W1 and W2 do not attack P (no
capturing key), P captures each, and from the capture square P no longer reaches the line. Only these units are on the
board, so blockers added later can still help.

    python -m chesscomp.compose.battery_guards d4 d5 d8 c4 e4 [q|r|b|n] [n|p|b|r]   (black holder, White front piece)
Found for Kd4, Sd5, Rd8 (c4/e4): queen f5 with Rc2/Sf2, queen b5 with Sb2/Re2; no rook or bishop configuration.
"""
from __future__ import annotations
import itertools
import sys
import chess

TYPES = (chess.ROOK, chess.BISHOP, chess.KNIGHT)


def _board(king, front, rear, units, wk, ftype=chess.KNIGHT):
    b = chess.Board(None)
    b.set_piece_at(king, chess.Piece(chess.KING, chess.BLACK))
    b.set_piece_at(rear, chess.Piece(chess.ROOK if chess.square_file(rear) == chess.square_file(king)
                                      or chess.square_rank(rear) == chess.square_rank(king) else chess.BISHOP, chess.WHITE))
    b.set_piece_at(front, chess.Piece(ftype, chess.WHITE))
    b.set_piece_at(wk, chess.Piece(chess.KING, chess.WHITE))
    for sq, pc in units:
        b.set_piece_at(sq, pc)
    return b


def _interposes(b, p, front, line):
    b2 = b.copy(); b2.remove_piece_at(front)
    return any(p in b2.attackers(chess.BLACK, s) for s in line)


def configurations(king, front, rear, sq1, sq2, ptype=chess.QUEEN, ftype=chess.KNIGHT):
    line = [s for s in chess.SquareSet(chess.between(rear, king))]
    taken = {king, front, rear}
    wk = next(s for s in (chess.A8, chess.H8, chess.A1, chess.H1) if chess.square_distance(s, king) > 2 and s not in taken)
    taken.add(wk)
    out = []
    for p in chess.SQUARES:
        if p in taken or chess.square_distance(p, king) <= 1:
            continue
        for t1, s1, t2, s2 in itertools.product(TYPES, chess.SQUARES, TYPES, chess.SQUARES):
            if len({p, s1, s2} | taken) < 3 + len(taken) or min(chess.square_distance(s, king) for s in (s1, s2)) <= 1:
                continue
            b = _board(king, front, rear, [(p, chess.Piece(ptype, chess.BLACK)), (s1, chess.Piece(t1, chess.WHITE)),
                                           (s2, chess.Piece(t2, chess.WHITE))], wk, ftype)
            if not b.is_valid() or b.is_attacked_by(chess.WHITE, king):
                continue
            a1, a2 = b.attacks(s1), b.attacks(s2)
            if not (sq1 in a1 and sq2 not in a1 and sq2 in a2 and sq1 not in a2):
                continue
            if b.is_attacked_by(chess.WHITE, p) or not _interposes(b, p, front, line):
                continue
            ok = True
            for s in (s1, s2):
                b2 = b.copy(); b2.remove_piece_at(p); b2.set_piece_at(s, chess.Piece(ptype, chess.BLACK))
                if s not in b.attacks(p) or _interposes(b2, s, front, line):
                    ok = False
                    break
            if ok:
                out.append((p, (t1, s1), (t2, s2)))
    return out


def main(argv=None):
    a = argv or sys.argv[1:]
    king, front, rear, sq1, sq2 = (chess.parse_square(x) for x in a[:5])
    ptype = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}[a[5] if len(a) > 5 else 'q']
    ftype = {'n': chess.KNIGHT, 'p': chess.PAWN, 'b': chess.BISHOP, 'r': chess.ROOK}[a[6] if len(a) > 6 else 'n']
    for p, (t1, s1), (t2, s2) in configurations(king, front, rear, sq1, sq2, ptype, ftype):
        print(chess.square_name(p), chess.piece_symbol(t1).upper() + chess.square_name(s1),
              chess.piece_symbol(t2).upper() + chess.square_name(s2))


if __name__ == '__main__':
    main()
