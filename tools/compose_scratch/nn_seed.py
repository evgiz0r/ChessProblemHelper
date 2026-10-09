"""Two black knights to one square next to Kd4, no white queen. Core units (argv[2] FEN, '-' for none) stay
fixed; the climb adds/moves the rest. Every good post-key hit is keyed at once (unique key, no flight taken)."""
import chess, random, sys
from same_sq_lib import score_nn, keys_for
random.seed(int(sys.argv[1]))
core = chess.Board(None) if sys.argv[2] == '-' else chess.Board(sys.argv[2] + ' b - - 0 1')
core.turn = chess.BLACK
FIX = set(core.piece_map())
WHITE_POOL, BLACK_POOL = 'RRBBNNPP', 'pppbrn'
SEED = sys.argv[3] if len(sys.argv) > 3 else None
def rand_pos():
    if SEED: b = chess.Board(SEED + ' b - - 0 1'); return b
    b = core.copy(); b.turn = chess.BLACK
    if not b.king(chess.BLACK): b.set_piece_at(chess.D4, chess.Piece(chess.KING, chess.BLACK))
    free = [s for s in chess.SQUARES if not b.piece_at(s)]; random.shuffle(free)
    add = ('K' if not b.king(chess.WHITE) else '') + ('nn' if len(b.pieces(chess.KNIGHT, chess.BLACK)) < 2 else '')
    add += ''.join(random.sample(WHITE_POOL, 4))
    for p in add: b.set_piece_at(free.pop(), chess.Piece.from_symbol(p))
    return b
def mutate(b):
    c = b.copy(); pm = [s for s in c.piece_map() if s not in FIX and c.piece_at(s).piece_type != chess.KING or (s not in FIX and c.piece_at(s).color)]
    pm = [s for s in c.piece_map() if s not in FIX and not (c.piece_at(s).piece_type == chess.KING and c.piece_at(s).color == chess.BLACK)]
    free = [s for s in chess.SQUARES if not c.piece_at(s)]; r = random.random()
    if r < 0.6 and pm:
        s = random.choice(pm); p = c.remove_piece_at(s); c.set_piece_at(random.choice(free), p)
    elif r < 0.78 and len(pm) < 10:
        c.set_piece_at(random.choice(free), chess.Piece.from_symbol(random.choice(WHITE_POOL + BLACK_POOL)))
    elif pm:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING: c.remove_piece_at(s)
    for s, p in c.piece_map().items():
        if p.piece_type == chess.PAWN and chess.square_rank(s) in (0, 7): return b
    for col in (True, False):
        if any(len(c.pieces(t, col)) > 2 for t in (chess.KNIGHT, chess.ROOK, chess.BISHOP)): return b
    if len(c.pieces(chess.KNIGHT, chess.BLACK)) < 2 or c.pieces(chess.QUEEN, chess.WHITE): return b
    return c
seen = set()
while True:
    b = rand_pos(); sc = score_nn(b)
    while sc is None: b = rand_pos(); sc = score_nn(b)
    for it in range(600):
        c = mutate(b); s2 = score_nn(c)
        if s2 is not None and s2[0] <= sc[0]: b, sc = c, s2
    print("ROUND", round(sc[0], 1), b.board_fen(), sc[1], flush=True)
    if sc[0] < 8 and b.board_fen() not in seen:
        seen.add(b.board_fen())
        print('POST', round(sc[0], 1), b.board_fen(), sc[1], sc[2], flush=True)
        for k in keys_for(b, sc[1]): print('  KEY', k, flush=True)
