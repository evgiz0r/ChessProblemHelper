"""Add one unit (or two with --two) so every black move has a mate and the thematic mates stay unique."""
import chess, sys, itertools
from same_sq_lib import m1
base = chess.Board(sys.argv[1] + ' b - - 0 1'); WANT = dict(a.split('=') for a in sys.argv[2].split(','))
def ok(b):
    if not b.is_valid() or b.is_check(): return None
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check() or not m1(w): return None
    duals = 0
    for m in list(b.legal_moves):
        u = m.uci(); b.push(m); ms = {b.san(x) for x in m1(b)}; b.pop()
        if not ms: return None
        if u in WANT and ms != {WANT[u]}: return None
        duals += len(ms) - 1
    return duals
res = []
for sq in chess.SQUARES:
    if base.piece_at(sq): continue
    for sym in 'RBNPprbn':
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7): continue
        b = base.copy(); b.set_piece_at(sq, chess.Piece.from_symbol(sym)); d = ok(b)
        if d is not None: res.append((d, sym + chess.square_name(sq), b.board_fen()))
for r in sorted(res)[:12]: print(r)
print(len(res), 'found')
