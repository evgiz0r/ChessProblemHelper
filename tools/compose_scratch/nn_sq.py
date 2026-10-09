"""Hill-climb post-key #2: two different black pieces move (no capture) to the SAME square next to the king,
each defeating the threat, each answered by its own mate that needs the block."""
import chess, random, sys
random.seed(int(sys.argv[1])); KS = chess.D4
ADJ = [s for s in chess.SQUARES if chess.square_distance(s, KS) == 1]
def m1(b):
    r = []
    for m in list(b.legal_moves):
        b.push(m); ok = b.is_checkmate(); b.pop()
        if ok: r.append(m)
    return r
def score(b):
    if b.is_check() or not b.is_valid(): return None
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check(): return None
    th = {w.san(m) for m in m1(w)}
    if not th: return None
    bad = 0; per = {}
    for m in list(b.legal_moves):
        cap = b.is_capture(m)
        b.push(m); ms = m1(b)
        if not ms: bad += 1
        elif m.to_square in ADJ and not cap and b.piece_at(m.to_square).piece_type != chess.KING:
            names = {b.san(x) for x in ms}; uses = set()
            for x in ms:
                c = b.copy(); c.remove_piece_at(m.to_square); c.push(x)
                if not c.is_checkmate(): uses.add(b.san(x))
            per.setdefault(m.to_square, []).append((m.from_square, names, uses))
        b.pop()
    pen = bad * 10 + 2 * (len(th) - 1) + 0.3 * len(b.piece_map())
    best, bpair = 40, None
    for sq, lst in per.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, c = lst[i], lst[j]
                if b.piece_at(a[0]).piece_type != chess.KNIGHT or b.piece_at(c[0]).piece_type != chess.KNIGHT: continue
                p = 3 * (len(a[1]) - 1) + 3 * (len(c[1]) - 1)
                p += 0 if a[2] else 8; p += 0 if c[2] else 8
                if a[1] & c[1]: p += 10
                if a[1] & th or c[1] & th: p += 8
                if p < best: best, bpair = p, (chess.square_name(sq), a, c)
    return pen + best, bpair, th
def rand_pos():
    b = chess.Board(None); b.turn = chess.BLACK
    b.set_piece_at(KS, chess.Piece(chess.KING, chess.BLACK))
    free = [s for s in chess.SQUARES if s != KS]; random.shuffle(free)
    for p in 'K' + ''.join(random.sample('QRRBBNNP', 4)) + random.choice(['nn', 'nnp', 'nnb', 'nnr']):
        b.set_piece_at(free.pop(), chess.Piece.from_symbol(p))
    return b
def mutate(b):
    c = b.copy(); pm = [s for s in c.piece_map() if s != KS]
    free = [s for s in chess.SQUARES if not c.piece_at(s)]; r = random.random()
    if r < 0.55:
        s = random.choice(pm); p = c.remove_piece_at(s); c.set_piece_at(random.choice(free), p)
    elif r < 0.72 and len(pm) < 12:
        c.set_piece_at(random.choice(free), chess.Piece.from_symbol(random.choice('QRBNPPpprbn')))
    elif r < 0.88 and len(pm) > 4:
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
while True:
    b = rand_pos(); sc = score(b)
    while sc is None: b = rand_pos(); sc = score(b)
    for it in range(4000):
        c = mutate(b); s2 = score(c)
        if s2 is not None and s2[0] <= sc[0]: b, sc = c, s2
    if sc[0] < 6: print(round(sc[0], 1), b.board_fen(), sc[1], sc[2], flush=True)
