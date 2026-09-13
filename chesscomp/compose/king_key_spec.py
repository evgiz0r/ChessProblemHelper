import sys, chess
sys.path.insert(0,'/home/claude'); sys.path.insert(0,'/home/claude/chesscomp')
from kingkey import solves, threatens, king_profile, unique_solution, blocks_white_line
from chesscomp import san
from chesscomp.compose.scheme_search import mates_after

def defences_with_mates(b, key):
    """After the key: each Black move with exactly one mate that is not the threat."""
    t = b.copy(); t.push(key)
    t0 = t.copy(); t0.push(chess.Move.null())
    threat = {m.uci() for m in mates_after(t0)}
    out = {}
    for d in list(t.legal_moves):
        t.push(d); ms = mates_after(t); t.pop()
        if len(ms) == 1 and ms[0].uci() not in threat:
            out[d] = ms[0]
    return out, threat

def essential_lines(b, key, d, m):
    """White line pieces without which the mate m (after defence d) is no longer mate."""
    t = b.copy(); t.push(key); t.push(d); t.push(m)
    out = []
    for sq in chess.SquareSet(t.occupied_co[chess.WHITE]):
        if t.piece_type_at(sq) not in (chess.QUEEN, chess.ROOK, chess.BISHOP): continue
        if sq == m.to_square: continue
        x = t.copy(); x.remove_piece_at(sq)
        if not x.is_checkmate(): out.append(chess.square_name(sq))
    return set(out)

def analyse_king_key(b):
    """Return the full three-way structure if it exists, else None."""
    sol, thr = king_profile(b)
    if len(sol) != 1 or len(thr) < 2: return None
    key = sol[0]; kf = b.king(chess.WHITE)
    if blocks_white_line(b, kf, key.to_square): return None
    defs, threat = defences_with_mates(b, key)
    if len(defs) < 2: return None
    ess = {d: essential_lines(b, key, d, m) for d, m in defs.items()}
    hits = []
    for t in thr:
        cut = {p for p, _ in blocks_white_line(b, kf, t.to_square)}
        if not cut: continue
        # which defence refutes this try, and does it need exactly a cut line?
        tb = b.copy(); tb.push(t)
        refs = []
        for d in list(tb.legal_moves):
            tb.push(d); ok = bool(mates_after(tb)); tb.pop()
            if not ok: refs.append(d)
        if len(refs) != 1: continue
        r = refs[0]
        match = [d for d in defs if d.from_square == r.from_square and d.to_square == r.to_square]
        if match and ess[match[0]] & cut:
            hits.append((san(b, t), san(b, r), sorted(ess[match[0]] & cut)))
    return {'key': san(b, key), 'defs': {san(b.copy(), d): None for d in defs}, 'hits': hits} if len(hits) >= 2 else None
