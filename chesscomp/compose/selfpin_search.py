import sys, chess
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'/home/claude/chesscomp')
from kingkey import solves, threatens, king_profile, unique_solution
from chesscomp import san
from chesscomp.compose.scheme_search import mates_after

def self_pins(b, king_to):
    """White pieces that become pinned when the White king moves to `king_to`."""
    t = b.copy(); t.remove_piece_at(t.king(chess.WHITE))
    t.set_piece_at(king_to, chess.Piece(chess.KING, True))
    out = []
    for sq in chess.SquareSet(t.occupied_co[chess.WHITE]):
        if t.piece_type_at(sq) == chess.KING: continue
        if t.is_pinned(chess.WHITE, sq):
            out.append(chess.square_name(sq))
    return out

def refutations(b, mv):
    t = b.copy(); t.push(mv); out = []
    for d in list(t.legal_moves):
        t.push(d)
        ok = bool(mates_after(t)) if not (t.is_game_over() and not t.is_checkmate()) else False
        t.pop()
        if not ok: out.append(d)
    return out

def key_answers(b, key):
    """defence uci -> mate move, for the solution."""
    t = b.copy(); t.push(key)
    t0 = t.copy(); t0.push(chess.Move.null())
    threat = {m.uci() for m in mates_after(t0)}
    out = {}
    for d in list(t.legal_moves):
        t.push(d); ms = mates_after(t); t.pop()
        if len(ms) == 1 and ms[0].uci() not in threat:
            out[d.uci()] = ms[0]
    return out

def evaluate(b):
    """Return the structure if: unique king key with no self-pin, >=2 tries that self-pin a White piece
    which the answering mate needs."""
    sol, thr = king_profile(b)
    if len(sol) != 1 or len(thr) < 2: return None
    key = sol[0]
    if self_pins(b, key.to_square): return None
    ans = key_answers(b, key)
    if len(ans) < 2: return None
    hits = []
    for t in thr:
        pinned = self_pins(b, t.to_square)
        if not pinned: continue
        refs = refutations(b, t)
        if not refs: continue
        for r in refs:
            m = ans.get(r.uci())
            if m and chess.square_name(m.from_square) in pinned:
                hits.append((san(b, t), san(b, r), chess.square_name(m.from_square), pinned))
                break
    return hits if len(hits) >= 2 else None
