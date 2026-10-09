"""Finish a post-key scheme: keep CORE units, never let White guard FREE, thematic mates unique; minimise
black moves without mate (x10), threat duals (x2) and units (x0.3). Prints every improvement."""
import chess, random, sys
from same_sq_lib import m1
seed, start, core, want, free = int(sys.argv[1]), sys.argv[2], sys.argv[3], dict(a.split('=') for a in sys.argv[4].split(',')), chess.parse_square(sys.argv[5])
random.seed(seed)
FIX = set(chess.Board(core + ' w - - 0 1').piece_map())
def score(b):
    if not b.is_valid() or b.is_check() or b.is_attacked_by(chess.WHITE, free): return None
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check(): return None
    th = m1(w)
    if not th: return None
    pen = 2 * (len(th) - 1) + 0.3 * len(b.piece_map())
    for m in list(b.legal_moves):
        u = m.uci(); b.push(m); ms = {b.san(x) for x in m1(b)}; b.pop()
        if u in want:
            if want[u] not in ms: return None
            pen += 6 * (len(ms) - 1)
        elif not ms: pen += 10
    return pen
def mutate(b):
    c = b.copy(); pm = [s for s in c.piece_map() if s not in FIX]
    freeq = [s for s in chess.SQUARES if not c.piece_at(s) and s != free]; r = random.random()
    if r < 0.55 and pm:
        s = random.choice(pm); p = c.remove_piece_at(s); c.set_piece_at(random.choice(freeq), p)
    elif r < 0.8:
        c.set_piece_at(random.choice(freeq), chess.Piece.from_symbol(random.choice('RBNPPpppbn')))
    elif pm:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING: c.remove_piece_at(s)
    for s, p in c.piece_map().items():
        if p.piece_type == chess.PAWN and chess.square_rank(s) in (0, 7): return b
    for col in (True, False):
        if any(len(c.pieces(t, col)) > 2 for t in (chess.KNIGHT, chess.ROOK, chess.BISHOP)) or len(c.pieces(chess.QUEEN, col)) > 1: return b
    return c
b = chess.Board(start + ' b - - 0 1'); sc = score(b); print('START', sc, flush=True)
while True:
    c = mutate(b); s2 = score(c)
    if s2 is not None and s2 <= sc:
        if s2 < sc: print(round(s2, 1), c.board_fen(), flush=True)
        b, sc = c, s2
