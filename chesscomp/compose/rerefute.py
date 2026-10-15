"""Re-guard a try so that its refutation becomes thematic (E. Bourd, 15 Oct 2026: "how would you find that
improvement, its not just trimming").

A try fails because it lacks one guard the key has (anatomy: "Sc2+: flight e4"). If the only guard in the try is a
pawn or a short-range unit, the refutation can only capture it (1.Qf7? Bxf3!). Replace that guard by a line piece
whose line to the square crosses the line of a thematic Black unit, and the refutation becomes a quiet interference
by that unit (1.Qf7? Rf5!, the Grimshaw rook cutting Bg6-e4). This enumerates exactly that: remove one White unit (or
none), add one White unit on any empty square, and keep the positions where

  * the key still answers every Black move (and keeps its threat),
  * the thematic defences keep their mates in the key and the try,
  * the try has exactly one refutation, made by a thematic unit (THEME squares), not a capture.

python-chess only; confirm every hit with chesscomp.report (cooks other than the key are not checked here).

    python -m chesscomp.compose.rerefute FEN KEY TRY THEME [DEFS]
    e.g. ... q7/2p1Q1p1/2b5/r1r4p/p1Pk4/3NNP2/3K4/8 e7e6 e7f7 c5,c6 c6d5,c5d5
"""
from __future__ import annotations
import sys
import chess
from .trychange import mates, promoted

TYPES = [chess.BISHOP, chess.ROOK, chess.KNIGHT, chess.PAWN]


def _phase(b, move, defs):
    """(refutations, {def: mates}, threat mates) after White's move, or None if illegal."""
    if move not in b.legal_moves:
        return None
    p = b.copy(); p.push(move)
    n = p.copy(); n.push(chess.Move.null())
    thr = tuple(sorted(mates(n))) if n.is_valid() and not n.is_check() else ()
    refs, dm = [], {}
    for d in list(p.legal_moves):
        p.push(d)
        ms = () if p.is_checkmate() else tuple(sorted(mates(p)))
        if not p.is_checkmate() and not ms:
            refs.append(d)
        if d in defs:
            dm[d] = ms
        p.pop()
    return refs, dm, thr


def rerefute(fen, key, trym, theme, defs=()):
    b0 = chess.Board(fen if ' ' in fen else fen + ' w - - 0 1')
    key, trym = chess.Move.from_uci(key), chess.Move.from_uci(trym)
    theme = {chess.parse_square(s) for s in theme}
    defs = [chess.Move.from_uci(d) for d in defs]
    k0, t0 = _phase(b0, key, defs), _phase(b0, trym, defs)
    removable = [None] + [s for s, pc in b0.piece_map().items()
                          if pc.color and pc.piece_type != chess.KING and s not in (key.from_square,)]
    hits = []
    for rem in removable:
        for sq in chess.SQUARES:
            for t in TYPES:
                b = b0.copy()
                if rem is not None:
                    b.remove_piece_at(rem)
                if b.piece_at(sq) or (t == chess.PAWN and chess.square_rank(sq) in (0, 7)):
                    continue
                b.set_piece_at(sq, chess.Piece(t, chess.WHITE))
                if not b.is_valid() or promoted(b) or mates(b):
                    continue
                kp = _phase(b, key, defs)
                if not kp or kp[0] or kp[2] != k0[2] or any(kp[1].get(d) != k0[1].get(d) for d in defs):
                    continue
                tp = _phase(b, trym, defs)
                if not tp or len(tp[0]) != 1 or any(tp[1].get(d) != t0[1].get(d) for d in defs):
                    continue
                r = tp[0][0]
                p = b.copy(); p.push(trym)
                if r.from_square not in theme or p.is_capture(r):
                    continue
                change = ('-' + b0.piece_at(rem).symbol().upper() + chess.square_name(rem) + ' ') if rem is not None else ''
                change += '+' + chess.Piece(t, chess.WHITE).symbol().upper() + chess.square_name(sq)
                hits.append((change, p.san(r), b.board_fen()))
    return hits


def main(argv=None):
    a = argv or sys.argv[1:]
    hits = rerefute(a[0], a[1], a[2], a[3].split(','), a[4].split(',') if len(a) > 4 else ())
    for change, ref, fen in hits:
        print(f'{change:14} try refuted only by {ref:6} {fen}')
    print(f'{len(hits)} hits')


if __name__ == '__main__':
    main()
