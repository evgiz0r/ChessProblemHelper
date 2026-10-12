"""Skeletons for E. Bourd's knight theme with the try pair (12 Oct 2026: "Se6 sounds like almost a must, once having
the Sb5 try"): a black knight O defends the threat square T from A1/A2, each arrival closing the line of a black rook
or bishop that guarded a knight-check square m1/m2. White's knight stands on T in the diagram: the key T->K reaches
m1 and m2, the try T->t1 reaches m1 only (refuted by the defence that needs m2), T->t2 reaches m2 only.

ESCAPES are the line pieces' other moves that land on a square attacking T (1...Rd1 guarding d4 down the d-file in
8/Q1BB4/2P2r2/K2k4/p1pNp3/4n3/8/2r5): such a by-play repeats a thematic mate AND refutes a try, so the pair cannot
exist. An escape is counted only if no black self-block on the king's field can stop it (on the landing square,
on the way to it, or between it and T); --max sets how many are allowed.

    python3 -m chesscomp.compose.knight_pair_skeletons d5 [--max 1]

Result (12 Oct 2026): T e5, Sf6 -> g4/d7, rooks h4 and b7 (c7 attacked the try square c6), key Se5-g6, tries Sd3/Sc6:
8/1r6/1p1PRn2/1KpkNB2/2p1p2r/2Q5/b2P4/8.
"""
import sys, itertools, argparse, chess
N = lambda s: set(chess.SquareSet(chess.BB_KNIGHT_ATTACKS[s]))
F = lambda s: set(chess.SquareSet(chess.BB_KING_ATTACKS[s]))
DIRS = {'R': [(1,0),(-1,0),(0,1),(0,-1)], 'B': [(1,1),(1,-1),(-1,1),(-1,-1)]}
def ray(s, d, occ):
    x, y = chess.square_file(s), chess.square_rank(s); out = []
    while True:
        x += d[0]; y += d[1]
        if not (0 <= x < 8 and 0 <= y < 8): return out
        q = chess.square(x, y); out.append(q)
        if q in occ: return out
def attacks(kind, s, t, occ):
    return any(t in ray(s, d, occ) for d in DIRS[kind])
def between(a, b):
    return set(chess.SquareSet(chess.between(a, b)))
def escapes(kind, p, t, occ, field):
    """Destinations of the piece on p that attack t and cannot be stopped by a black self-block on the king's field
    (a field square strictly between the destination and t)."""
    bad = []
    for d in DIRS[kind]:
        for q in ray(p, d, occ):
            if q in occ: break
            if attacks(kind, q, t, occ | {q}) and not (between(q, t) & field) and q not in field \
                    and not (between(p, q) & field):
                bad.append(q)
    return bad
def central(*sq): return sum(max(abs(chess.square_file(s)-3.5), abs(chess.square_rank(s)-3.5)) for s in sq)
def main():
    _ap = argparse.ArgumentParser(); _ap.add_argument('king', nargs='?', default='d5'); _ap.add_argument('--max', type=int, default=1)
    _a = _ap.parse_args()
    k = chess.parse_square(_a.king)
    KC = N(k)                                # knight-check squares: knight mates
    rows = []
    for T in chess.SQUARES:
        if T == k or T in F(k) and False: pass
        if not (T in F(k)): continue         # threat lands next to the king (Q/R) and the White knight stands there first
        ring = N(T) - {k} - F(k)
        for O in chess.SQUARES:
            if O in (k, T) or O in F(k): continue
            arr = sorted((N(O) & N(T)) - {k} - F(k))
            for A1, A2 in itertools.combinations(arr, 2):
                for m1 in KC:
                    for m2 in KC:
                        if m1 == m2 or T in (m1, m2): continue
                        keys = (N(m1) & N(m2) & N(T)) - {k, A1, A2}
                        t1s = (N(m1) & N(T)) - N(m2) - {k, A1, A2, m1, m2}
                        t2s = (N(m2) & N(T)) - N(m1) - {k, A1, A2, m1, m2}
                        if not (keys and t1s and t2s): continue
                        # lines: A1 between P1 and m1 on a straight line
                        def pieces(A, m):
                            out = []
                            df, dr = chess.square_file(m) - chess.square_file(A), chess.square_rank(m) - chess.square_rank(A)
                            if not (df == 0 or dr == 0 or abs(df) == abs(dr)): return out
                            d = ((df > 0) - (df < 0), (dr > 0) - (dr < 0)); kind = 'R' if 0 in d else 'B'
                            occ0 = {k, O, A}
                            if any(q in (k, T) for q in ray(A, d, {m})[:-1]): return out      # A..m must be clear
                            for p in ray(A, (-d[0], -d[1]), {k}):
                                if p in (k, T, O): break
                                esc = escapes(kind, p, T, {k, O, T}, F(k) - {T})
                                out.append((kind, p, esc))
                            return out
                        for (k1, p1, e1) in pieces(A1, m1):
                            for (k2, p2, e2) in pieces(A2, m2):
                                if p1 == p2: continue
                                if len(e1) + len(e2) > _a.max: continue
                                rows.append((len(e1)+len(e2), central(O, A1, A2, p1, p2), T, O, A1, A2, m1, m2, k1, p1, e1, k2, p2, e2, keys, t1s, t2s))
    rows.sort(key=lambda r: (r[0], r[1]))
    n = chess.square_name
    seen = set()
    for r in rows:
        ne, c, T, O, A1, A2, m1, m2, k1, p1, e1, k2, p2, e2, keys, t1s, t2s = r
        sig = (T, O, A1, A2, m1, m2, k1, p1, k2, p2)
        if sig in seen: continue
        seen.add(sig)
        print(f"esc={ne} T {n(T)} S{n(O)}->{n(A1)}/{n(A2)} mates {n(m1)}/{n(m2)} {k1}{n(p1)}[{','.join(map(n,e1))}] {k2}{n(p2)}[{','.join(map(n,e2))}] key->{','.join(map(n,keys))} tries {','.join(map(n,t1s))}|{','.join(map(n,t2s))} c={c:.1f}")
    print(len(seen), 'skeletons')


if __name__ == '__main__':
    main()
