"""Why a check is (not) mate, square by square - so hand construction stops relying on board sight.

During construction (8 Oct 2026) Claude claimed a white pawn on e6 protects d5 (it guards d7/f7) and that 2.Rc4
mates (it did not): two board-sight errors a square-by-square listing catches at once.

    python3 -m chesscomp.compose.matecheck FEN "MOVE ..."     # moves from the FEN, White first unless 'b' given

For the last move (a white check) it lists every square of the black king's field with the white units that
cover it (or 'FREE'), every black interposition, and every black capture of the checking unit.
"""
from __future__ import annotations
import sys
import chess

NAMES = {chess.PAWN: 'P', chess.KNIGHT: 'S', chess.BISHOP: 'B', chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'}


def explain(board: chess.Board) -> list[str]:
    """board: Black to move, in check (or not). Lines of the analysis."""
    out = []
    bk = board.king(chess.BLACK)
    out.append('mate' if board.is_checkmate() else ('check, not mate' if board.is_check() else 'no check'))
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[bk]):
        p = board.piece_at(sq)
        if p and p.color == chess.BLACK:
            out.append(f'  {chess.square_name(sq)}: own {NAMES[p.piece_type]} (self-block)'); continue
        b = board.copy(); b.remove_piece_at(bk); b.set_piece_at(bk, None) if False else None
        # attackers with the king removed from its square (x-ray along the checking line counts)
        t = board.copy(); t.remove_piece_at(bk)
        att = [NAMES[t.piece_type_at(a)] + chess.square_name(a) for a in t.attackers(chess.WHITE, sq)]
        cap = f' (white {NAMES[p.piece_type]} there)' if p else ''
        out.append(f'  {chess.square_name(sq)}{cap}: ' + (', '.join(att) if att else 'FREE'))
    for m in board.legal_moves:
        if m.from_square == bk:
            continue
        if board.is_capture(m) and m.to_square in board.checkers():
            out.append(f'  capture of the checker: {board.san(m)}')
        elif board.is_check():
            out.append(f'  interposition: {board.san(m)}')
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    fen = argv[0] if ' ' in argv[0] else argv[0] + ' w - - 0 1'
    b = chess.Board(fen)
    for san in (argv[1].split() if len(argv) > 1 else []):
        b.push_san(san)
    for line in explain(b):
        print(line)


if __name__ == '__main__':
    main()
