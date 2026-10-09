"""Step 2: add black units that stop the white mates (a block). Each black move should then release a mate,
and different black units should release different mates. Random combos of candidate stoppers, best printed."""
import chess, random, sys, itertools
random.seed(int(sys.argv[2])); base = chess.Board(sys.argv[1] + ' b - - 0 1'); KS = base.king(chess.BLACK)
def wmates(b):
    w = b.copy(); w.turn = chess.WHITE; out = set()
    for m in list(w.legal_moves):
        if not w.gives_check(m): continue
        w.push(m)
        if w.is_checkmate(): out.add(w.peek() and w.pop() and None or m); continue
        w.pop()
    return out
def names(b, ms):
    w = b.copy(); w.turn = chess.WHITE; return {w.san(m) for m in ms}
def ok_board(b):
    if not b.is_valid() or b.is_check(): return False
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check(): return False
    return not any(m.from_square == KS for m in b.legal_moves)
M0 = names(base, wmates(base)); print('mates', sorted(M0))
cands = []
for s in chess.SQUARES:
    if base.piece_at(s): continue
    for sym in 'pnbr':
        if sym == 'p' and chess.square_rank(s) in (0, 7): continue
        b = base.copy(); b.set_piece_at(s, chess.Piece.from_symbol(sym))
        if not ok_board(b): continue
        left = names(b, wmates(b)); killed = M0 - left
        if killed and not (left - M0): cands.append((sym, s, frozenset(killed)))
print(len(cands), 'candidate stoppers')
def evaluate(units):
    b = base.copy()
    for sym, s, _ in units:
        if b.piece_at(s): return None
        b.set_piece_at(s, chess.Piece.from_symbol(sym))
    if not ok_board(b) or wmates(b): return None
    per, bad, duals = {}, 0, 0
    for m in list(b.legal_moves):
        b.push(m); ms = {b.san(x) for x in wmates_after(b)}; b.pop()
        if not ms: bad += 1; continue
        duals += len(ms) - 1
        if len(ms) == 1: per.setdefault(m.from_square, set()).update(ms)
    distinct = set().union(*per.values()) if per else set()
    return (bad, -len(distinct), duals, len(units)), b.board_fen(), sorted(distinct)
def wmates_after(b):
    out = []
    for m in list(b.legal_moves):
        if not b.gives_check(m): continue
        b.push(m)
        if b.is_checkmate(): out.append(m)
        b.pop()
    return out
res = []
for t in range(int(sys.argv[3])):
    random.shuffle(cands); need = set(M0); pick = []
    for c in cands:
        if c[2] & need and all(c[1] != p[1] for p in pick):
            pick.append(c); need -= c[2]
        if not need: break
    if need or len(pick) > 6: continue
    r = evaluate(pick)
    if r: res.append(r)
res.sort()
seen = set()
for r in res:
    if r[1] in seen: continue
    seen.add(r[1]); print(r)
    if len(seen) >= 8: break
