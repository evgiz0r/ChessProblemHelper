"""Hill-climb whole #2 diagrams: unique key, after it two different black pieces block the same square next to
the king (no capture) with their own mates; the key must not take flights. Seeds from a FEN (White to move)."""
import chess, random, sys
random.seed(int(sys.argv[2])); KS = chess.D4
ADJ = [s for s in chess.SQUARES if chess.square_distance(s, KS) == 1]
def m1(b, first=False):
    r = []
    for m in list(b.legal_moves):
        if not b.gives_check(m): continue
        b.push(m); ok = b.is_checkmate(); b.pop()
        if ok:
            r.append(m)
            if first: break
    return r
def flights(b):
    c = b.copy(); c.turn = chess.BLACK
    return {m.to_square for m in c.legal_moves if m.from_square == KS}
def refuts(b, cap=2):
    n = 0
    if not any(True for _ in b.legal_moves): return 0 if b.is_checkmate() else 9
    for r in list(b.legal_moves):
        b.push(r); ok = bool(m1(b, True)); b.pop()
        if not ok:
            n += 1
            if n >= cap: break
    return n
def theme(b):
    w = b.copy(); w.turn = chess.WHITE
    th = {w.san(m) for m in m1(w)}
    if not th: return 30, None
    per = {}
    for m in list(b.legal_moves):
        if m.to_square not in ADJ or b.is_capture(m) or m.from_square == KS: continue
        b.push(m); ms = m1(b); names = {b.san(x) for x in ms}; uses = set()
        for x in ms:
            c = b.copy(); c.remove_piece_at(m.to_square); c.push(x)
            if not c.is_checkmate(): uses.add(b.san(x))
        b.pop()
        per.setdefault(m.to_square, []).append((m, names, uses))
    best, info = 30, None
    for sq, l in per.items():
        for i in range(len(l)):
            for j in range(i + 1, len(l)):
                a, c = l[i], l[j]
                if b.piece_at(a[0].from_square).piece_type != chess.KNIGHT or b.piece_at(c[0].from_square).piece_type != chess.KNIGHT: continue
                p = 4 * (abs(len(a[1]) - 1) + abs(len(c[1]) - 1))
                p += (0 if a[2] else 8) + (0 if c[2] else 8)
                if a[1] & c[1]: p += 10
                if (a[1] | c[1]) & th: p += 8
                if p < best: best, info = p, (a[0].uci(), a[1], c[0].uci(), c[1], th)
    return best + 2 * (len(th) - 1), info
def score(d):
    if not d.is_valid() or d.is_check(): return None
    x = d.copy(); x.turn = chess.BLACK
    if x.is_check(): return None
    keys, near = [], 0
    for m in list(d.legal_moves):
        d.push(m); r = refuts(d); d.pop()
        if r == 0: keys.append(m)
        elif r == 1: near += 1
    if not keys: return 60 + 0.3 * len(d.piece_map()), None
    pen = 12 * (len(keys) - 1)
    k = keys[0]
    if d.gives_check(k) or d.is_capture(k): pen += 15
    f0 = flights(d); post = d.copy(); post.push(k); f1 = flights(post)
    pen += 6 * max(0, len(f0) - len(f1))
    pen += 2 * len(f0)  # unprovided-ish: flights in the diagram cost a little
    t, info = theme(post)
    pen += t + 0.3 * len(d.piece_map())
    return pen, (d.san(k), info, sorted(chess.square_name(s) for s in f0), sorted(chess.square_name(s) for s in f1), len(keys))
def mutate(b):
    c = b.copy(); pm = [s for s in c.piece_map() if s != KS]
    free = [s for s in chess.SQUARES if not c.piece_at(s)]; r = random.random()
    if r < 0.6:
        s = random.choice(pm); p = c.remove_piece_at(s); c.set_piece_at(random.choice(free), p)
    elif r < 0.75 and len(pm) < 12:
        c.set_piece_at(random.choice(free), chess.Piece.from_symbol(random.choice('QRBNPPppprbn')))
    elif r < 0.9 and len(pm) > 4:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING: c.remove_piece_at(s)
    else:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING: c.set_piece_at(s, chess.Piece.from_symbol(random.choice('QRBNPprbnq')))
    for s, p in c.piece_map().items():
        if p.piece_type == chess.PAWN and chess.square_rank(s) in (0, 7): return b
    for col in (True, False):
        if len(c.pieces(chess.QUEEN, col)) > 1 or len(c.pieces(chess.KNIGHT, col)) > 2 or (not col and len(c.pieces(chess.KNIGHT, col)) < 2) or len(c.pieces(chess.ROOK, col)) > 2 or len(c.pieces(chess.BISHOP, col)) > 2: return b
    return c
seed = chess.Board(sys.argv[1] + ' w - - 0 1')
while True:
    b = seed.copy(); sc = score(b)
    for it in range(1500):
        c = mutate(b); s2 = score(c)
        if s2 is not None and s2[0] <= sc[0]:
            if s2[0] < sc[0] and s2[0] < 8: print(round(s2[0], 1), c.board_fen(), s2[1], flush=True)
            b, sc = c, s2
