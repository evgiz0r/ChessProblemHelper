"""Geometry for 'unguard + self-block' with a queen: two knights k1,k2 -> S (next to Kd4); k1 guards X1, k2 guards
X2; a queen on Xi checks d4 but does NOT see S (so the block on S is needed); neither knight is pinned."""
import chess
K = chess.D4
def natt(s): return chess.SquareSet(chess.BB_KNIGHT_ATTACKS[s])
def q_sees(x, s, k=K):
    b = chess.Board(None); b.set_piece_at(x, chess.Piece(chess.QUEEN, chess.WHITE))
    if b.is_attacked_by(chess.WHITE, s): return True
    # x-ray through the king: s lies beyond the king on the queen's line
    return chess.square_distance(s, k) == 1 and s in chess.SquareSet(chess.between(x, s) | chess.BB_SQUARES[s]) and k in chess.SquareSet(chess.between(x, s)) if False else (
        k in chess.SquareSet(chess.between(x, s)) and chess.SquareSet(chess.ray(x, s)) & chess.BB_SQUARES[k] != 0)
def checks(x):
    b = chess.Board(None); b.set_piece_at(x, chess.Piece(chess.QUEEN, chess.WHITE)); b.set_piece_at(K, chess.Piece(chess.KING, chess.BLACK))
    return b.is_attacked_by(chess.WHITE, K)
out = []
for S in chess.SquareSet(chess.BB_KING_ATTACKS[K]):
    origins = [o for o in natt(S) if o != K]
    for i in range(len(origins)):
        for j in range(i + 1, len(origins)):
            k1, k2 = origins[i], origins[j]
            for X1 in natt(k1):
                if X1 in natt(k2) or X1 == K or X1 == S or not checks(X1) or q_sees(X1, S): continue
                for X2 in natt(k2):
                    if X2 in natt(k1) or X2 in (K, S, X1) or not checks(X2) or q_sees(X2, S): continue
                    if X1 in (k1, k2) or X2 in (k1, k2): continue
                    out.append((chess.square_name(S), chess.square_name(k1), chess.square_name(X1), chess.square_name(k2), chess.square_name(X2),
                                chess.square_distance(X1, K) + chess.square_distance(X2, K)))
seen = set()
for r in sorted(out, key=lambda r: r[5]):
    key = (r[0], r[1], r[3])
    if key in seen: continue
    seen.add(key); print(r[:5])
print(len(out), 'combos', len(seen), 'knight placements')
