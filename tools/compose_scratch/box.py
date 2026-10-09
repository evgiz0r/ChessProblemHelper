"""Step 1 of 'strong pieces, then black stoppers': White K,Q,R,B,N around a black king, no check, no flights,
no battery (no white line piece behind another white piece aimed at the king), as many distinct mates as possible."""
import chess, random, sys
random.seed(int(sys.argv[1])); KS = chess.parse_square(sys.argv[2])
def mates(b):
    w = b.copy(); w.turn = chess.WHITE; out = []
    for m in list(w.legal_moves):
        if not w.gives_check(m): continue
        w.push(m)
        if w.is_checkmate(): out.append(m)
        w.pop()
    return out
def battery(b):
    for s, p in b.piece_map().items():
        if p.color and p.piece_type in (2, 3, 4):
            for t in chess.SquareSet(chess.between(s, KS)):
                q = b.piece_at(t)
                if q and q.color and not (chess.BB_SQUARES[KS] & b.attacks_mask(s)): return True
    return False
best = []
for it in range(int(sys.argv[3])):
    b = chess.Board(None); b.turn = chess.BLACK; b.set_piece_at(KS, chess.Piece(chess.KING, chess.BLACK))
    sq = [s for s in chess.SQUARES if chess.square_distance(s, KS) >= 2]; random.shuffle(sq)
    for p in 'KQRBN':
        b.set_piece_at(sq.pop(), chess.Piece.from_symbol(p))
    if not b.is_valid() or b.is_check(): continue
    if any(m.from_square == KS for m in b.legal_moves): continue
    if battery(b): continue
    ms = mates(b)
    w = b.copy(); w.turn = chess.WHITE
    names = sorted({w.san(m) for m in ms})
    movers = {m.from_square for m in ms}
    best.append((len(movers), len(names), b.board_fen(), names))
best.sort(reverse=True)
for r in best[:6]: print(r)
