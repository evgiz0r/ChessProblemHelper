"""Keep my mate, kill the others: one added unit that leaves only the wanted mate after each defence.

You have the mates you want but each defence still allows rivals. This tries every single unit (pawn or
piece, either colour, every empty square) and keeps the additions after which, in every phase you name,
each defence is answered by the wanted mate and nothing else. Mates are named by piece and target square,
so Qe5 also matches Qxe5 (the added unit may be what the mate captures).

    python3 -m chesscomp.compose.keepkill FEN "Ke4: c6=Sf5 c5=Qh6" "Be6: c6=Sc8 c5=Qe5"

A phase is a white first move ("-" for the set play, Black to move as if White passed). Results are ranked
by the number of new black moves the unit brings (each one a possible hole or refutation for the solver to
check). E. Bourd, session 29: the black pawn e5 "eliminated the rest of the mates and I could keep my h6
mate. Maybe it was a bit lucky this worked."
"""
from __future__ import annotations
import sys
import chess
from .separate import _s


def mate_ids(board: chess.Board) -> set[str]:
    out = set()
    for m in board.legal_moves:
        p = board.piece_at(m.from_square)
        board.push(m)
        if board.is_checkmate():
            out.add(('' if p.piece_type == chess.PAWN else _s(p.symbol().upper())) + chess.square_name(m.to_square))
        board.pop()
    return out


def parse_phase(spec: str):
    head, _, body = spec.partition(':')
    wants = dict(item.split('=') for item in body.split())
    return head.strip(), wants


def phase_ok(board: chess.Board, move: str, wants: dict) -> bool:
    b = board.copy()
    if move == '-':
        b.push(chess.Move.null())
    else:
        try:
            b.push(b.parse_san(move.replace('S', 'N')))
        except ValueError:
            return False
    for d, want in wants.items():
        try:
            b.push(b.parse_san(d.replace('S', 'N')))
        except ValueError:
            return False
        ok = mate_ids(b) == {want}
        b.pop()
        if not ok:
            return False
    return True


def search(fen: str, phases):
    base = chess.Board(fen if ' ' in fen else fen + ' w - - 0 1')
    n_black = len(list(chess.Board(base.fen().replace(' w ', ' b ')).legal_moves))
    hits = []
    for sq in chess.SQUARES:
        if base.piece_at(sq):
            continue
        for sym in 'PSBRQpsbrq':
            if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
                continue
            b = base.copy()
            b.set_piece_at(sq, chess.Piece.from_symbol(sym.replace('S', 'N').replace('s', 'n')))
            if not b.is_valid():
                continue
            if all(phase_ok(b, mv, w) for mv, w in phases):
                bb = chess.Board(b.fen().replace(' w ', ' b '))
                extra = len(list(bb.legal_moves)) - n_black
                hits.append((extra, ('w' if sym.isupper() else 'b') + sym.upper() + chess.square_name(sq), b.board_fen()))
    return sorted(hits)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    fen, phases = argv[0], [parse_phase(s) for s in argv[1:]]
    hits = search(fen, phases)
    print(f'{len(hits)} single units keep only the wanted mates in every named phase:')
    for extra, unit, f in hits:
        print(f'   {unit:6}  +{extra} black moves   {f}')


if __name__ == '__main__':
    main()
