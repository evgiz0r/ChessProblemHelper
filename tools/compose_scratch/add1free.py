import sys, chess
import add1
base = add1.base
res = []
for sq in chess.SQUARES:
    if base.piece_at(sq) or sq == chess.C3: continue
    for sym in 'RBNPprbnq':
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7): continue
        b = base.copy(); b.set_piece_at(sq, chess.Piece.from_symbol(sym))
        if b.is_attacked_by(chess.WHITE, chess.C3): continue
        d = add1.ok(b)
        if d is not None: res.append((d, sym + chess.square_name(sq), b.board_fen()))
for r in sorted(res): print(r)
print(len(res), 'found')
