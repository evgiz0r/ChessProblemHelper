"""Hill-climb post-key #2 positions: Kd4, Sf4; threat Rb4#; Sd3/Sd5 self-blocks with own mates."""
import chess, random, sys
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
KS, NS = chess.D4, chess.F4
def mates(b):
    out = []
    for m in list(b.legal_moves):
        b.push(m)
        if b.is_checkmate(): out.append(m)
        b.pop()
    return out
def score(b):
    # b: Black to move (post-key)
    if b.is_check() or not b.is_valid(): return None
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check(): return None
    th = [m for m in mates(w)]
    thn = {w.san(m) for m in th}
    if not any(s.startswith('Rb4') for s in thn): return None
    bad = 0; info = {}
    for m in list(b.legal_moves):
        b.push(m)
        ms = mates(b)
        b.pop()
        if not ms: bad += 1; continue
        if m.from_square == NS and m.to_square in (chess.D3, chess.D5):
            b.push(m); names = {b.san(x) for x in ms}
            # does each mate rely on the block?
            uses = set()
            for x in ms:
                c = b.copy(); c.remove_piece_at(m.to_square)
                c.push(x)
                if not c.is_checkmate(): uses.add(b.san(x))
            b.pop()
            info[chess.square_name(m.to_square)] = (names, uses)
    pen = bad * 10
    for sq in ('d3', 'd5'):
        if sq not in info: pen += 30; continue
        names, uses = info[sq]
        pen += 3 * (len(names) - 1)
        if not uses: pen += 8
        if names & thn: pen += 8
    if 'd3' in info and 'd5' in info and info['d3'][0] & info['d5'][0]: pen += 8
    pen += 2 * (len(thn) - 1)
    pen += len(b.piece_map()) * 0.3
    return pen, info, thn
WP = 'QRBBNNP'
def rand_pos():
    b = chess.Board(None); b.turn = chess.BLACK
    b.set_piece_at(KS, chess.Piece(chess.KING, chess.BLACK))
    b.set_piece_at(NS, chess.Piece(chess.KNIGHT, chess.BLACK))
    free = [s for s in chess.SQUARES if not b.piece_at(s)]
    random.shuffle(free)
    b.set_piece_at(free.pop(), chess.Piece(chess.KING, chess.WHITE))
    b.set_piece_at(chess.square(1, random.choice([0,1,2,6,7])), chess.Piece(chess.ROOK, chess.WHITE))
    for p in random.sample(WP, random.randint(3, 5)):
        s = free.pop()
        if b.piece_at(s): continue
        b.set_piece_at(s, chess.Piece.from_symbol(p))
    return b
def mutate(b):
    c = b.copy()
    pm = [s for s, p in c.piece_map().items() if s not in (KS, NS)]
    r = random.random()
    free = [s for s in chess.SQUARES if not c.piece_at(s)]
    if r < 0.5:
        s = random.choice(pm); p = c.remove_piece_at(s); c.set_piece_at(random.choice(free), p)
    elif r < 0.7 and len(pm) < 11:
        c.set_piece_at(random.choice(free), chess.Piece.from_symbol(random.choice('QRBNPpppbnr' )))
    elif r < 0.85 and len(pm) > 3:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING: c.remove_piece_at(s)
    else:
        s = random.choice(pm)
        if c.piece_at(s).piece_type != chess.KING:
            c.set_piece_at(s, chess.Piece.from_symbol(random.choice('QRBNPpbnr')))
    for s, p in c.piece_map().items():
        if p.piece_type == chess.PAWN and chess.square_rank(s) in (0, 7): return b
    if len(c.pieces(chess.QUEEN, chess.WHITE)) > 1 or len(c.pieces(chess.KNIGHT, chess.WHITE)) > 2: return b
    return c
best = None
for restart in range(40):
    b = rand_pos(); sc = score(b)
    while sc is None: b = rand_pos(); sc = score(b)
    for it in range(3000):
        c = mutate(b); s2 = score(c)
        if s2 is None: continue
        if s2[0] <= sc[0]: b, sc = c, s2
    if best is None or sc[0] < best[1][0]: best = (b, sc)
    if sc[0] < 6: print(round(sc[0],1), b.board_fen(), sc[1], sc[2], flush=True)
print('BEST', best[1][0], best[0].board_fen(), best[1][1], best[1][2])
