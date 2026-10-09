"""One added unit so KEY is the only key, post-key thematic mates unique, and White never guards FREE after the key."""
import chess, sys
from same_sq_lib import m1
fen, key, want, free, part = sys.argv[1], sys.argv[2], dict(a.split('=') for a in sys.argv[3].split(',')), chess.parse_square(sys.argv[4]), int(sys.argv[5])
base = chess.Board(fen + ' w - - 0 1')
def refuted(b):
    if not any(True for _ in b.legal_moves): return not b.is_checkmate()
    for r in list(b.legal_moves):
        b.push(r); ok = bool(m1(b, True) if False else m1(b)); b.pop()
        if not ok: return True
    return False
def check(d):
    if not d.is_valid() or d.is_check(): return None
    x = d.copy(); x.turn = chess.BLACK
    if x.is_check(): return None
    k = chess.Move.from_uci(key)
    if k not in d.legal_moves: return None
    post = d.copy(); post.push(k)
    if post.is_attacked_by(chess.WHITE, free): return None
    duals = 0
    for m in list(post.legal_moves):
        u = m.uci(); post.push(m); ms = {post.san(z) for z in m1(post)}; post.pop()
        if not ms: return None
        if u in want and ms != {want[u]}: return None
        duals += len(ms) - 1
    for m in list(d.legal_moves):
        if m == k: continue
        d.push(m); r = refuted(d); d.pop()
        if not r: return None
    return duals
sqs = [s for s in chess.SQUARES if not base.piece_at(s) and s % 3 == part]
for s in sqs:
    for sym in 'RBNPprbn':
        if sym in 'Pp' and chess.square_rank(s) in (0, 7): continue
        d = base.copy(); d.set_piece_at(s, chess.Piece.from_symbol(sym)); r = check(d)
        if r is not None: print(r, sym + chess.square_name(s), d.board_fen(), flush=True)
