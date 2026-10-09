import chess
def natt(s): return chess.SquareSet(chess.BB_KNIGHT_ATTACKS[s])
def qatt(q, occ):
    b = chess.Board(None)
    for s in occ: b.set_piece_at(s, chess.Piece(chess.PAWN, chess.BLACK)) if False else None
    return None
def sees(q, t, occ):  # queen on q attacks t given occupied set occ
    if q == t: return False
    r = chess.ray(q, t)
    if not r: return False
    return not (chess.SquareSet(chess.between(q, t)) & occ)
out = []
for K in chess.SQUARES:
    for S in chess.SquareSet(chess.BB_KING_ATTACKS[K]):
        fl = len(chess.SquareSet(chess.BB_KING_ATTACKS[S]))          # king on S: neighbour count (edge = few)
        origins = [o for o in natt(S) if o != K and chess.square_distance(o, K) > 0]
        for i, k1 in enumerate(origins):
            for k2 in origins[i + 1:]:
                occ = chess.SquareSet([K, k1, k2])
                for X1 in natt(k1):
                    for X2 in natt(k2):
                        if X1 == X2 or X1 in natt(k2) or X2 in natt(k1) or {X1, X2} & {K, S, k1, k2}: continue
                        good = True
                        for X, other in ((X1, k2), (X2, k1)):
                            occX = chess.SquareSet([K, S, other])
                            if not sees(X, K, occX): good = False; break                       # gives check
                            line = chess.SquareSet(chess.between(X, K))
                            if X in natt(S) or line & (natt(S) | natt(other)): good = False; break
                            # queen must not see S (also x-ray through the king)
                            if sees(X, S, chess.SquareSet([other])) or (chess.ray(X, S) and K in chess.SquareSet(chess.between(X, S))): good = False; break
                        if not good: continue
                        for Q in chess.SQUARES:
                            if Q in occ or Q in (S, X1, X2): continue
                            o = chess.SquareSet([K, k1, k2])
                            if sees(Q, K, o) or sees(Q, S, o): continue
                            if sees(Q, X1, o) and sees(Q, X2, o):
                                out.append((fl, chess.square_name(K), chess.square_name(S), chess.square_name(k1), chess.square_name(X1), chess.square_name(k2), chess.square_name(X2), chess.square_name(Q)))
out.sort()
seen = set()
for r in out:
    if r[1:7] in seen: continue
    seen.add(r[1:7]); print(r)
    if len(seen) > 25: break
print(len(out))
