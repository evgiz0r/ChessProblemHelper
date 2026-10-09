"""One added unit so the block is complete: no White mate now, no flights, every black move mated. Ranked by
duals, then (more) distinct mates."""
import chess, sys
from lm_lib import m1
base = chess.Board(sys.argv[1] + ' b - - 0 1')
def ev(b):
    if not b.is_valid() or b.is_check(): return None
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check() or m1(w): return None
    if any(m.from_square == b.king(chess.BLACK) for m in b.legal_moves): return None
    duals, mates = 0, set()
    for m in list(b.legal_moves):
        b.push(m); ms = {b.san(x) for x in m1(b)}; b.pop()
        if not ms: return None
        duals += len(ms) - 1; mates |= ms
    return duals, -len(mates)
res = []
for s in chess.SQUARES:
    if base.piece_at(s): continue
    for sym in 'QRBNPqrbnp':
        if sym in 'Pp' and chess.square_rank(s) in (0, 7): continue
        b = base.copy(); b.set_piece_at(s, chess.Piece.from_symbol(sym)); r = ev(b)
        if r: res.append((r, sym + chess.square_name(s), b.board_fen()))
for r in sorted(res)[:10]: print(r)
print(len(res), 'found')
