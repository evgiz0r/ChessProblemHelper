"""Add one unit to the post-key position, keep the play, retract a key that does not take a flight."""
import chess, sys
POST = sys.argv[1]
WANT = {'d3': 'Rc4#', 'd5': 'Nc2#'}
def m1(b):
    r = []
    for m in list(b.legal_moves):
        b.push(m); ok = b.is_checkmate(); b.pop()
        if ok: r.append(m)
    return r
def flights(b):
    k = b.king(chess.BLACK); c = b.copy(); c.turn = chess.BLACK
    return {chess.square_name(m.to_square) for m in c.legal_moves if m.from_square == k}
def postok(b):
    if b.is_check(): return False
    w = b.copy(); w.turn = chess.WHITE
    if w.is_check(): return False
    for m in list(b.legal_moves):
        b.push(m); ms = m1(b); names = {b.san(x) for x in ms}; b.pop()
        if not ms: return False
        if m.from_square == chess.F4 and chess.square_name(m.to_square) in WANT:
            if names != {WANT[chess.square_name(m.to_square)]}: return False
    return True
def solves(b, m):
    b.push(m)
    if b.is_check() and False: pass
    ok = bool(list(b.legal_moves)) or b.is_checkmate()
    if ok:
        for r in list(b.legal_moves):
            b.push(r); good = bool(m1(b)); b.pop()
            if not good: ok = False; break
    b.pop(); return ok
def keys(b):
    return [m for m in list(b.legal_moves) if solves(b, m)]
base = chess.Board(POST + ' b - - 0 1')
out = []
for sq in chess.SQUARES:
    if base.piece_at(sq): continue
    for sym in 'QRBNPpnbrq':
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7): continue
        post = base.copy(); post.set_piece_at(sq, chess.Piece.from_symbol(sym))
        if not post.is_valid() or not postok(post): continue
        for psq, pc in post.piece_map().items():
            if pc.color != chess.WHITE: continue
            for frm in chess.SQUARES:
                if post.piece_at(frm): continue
                pre = post.copy(); pre.remove_piece_at(psq); pre.set_piece_at(frm, pc); pre.turn = chess.WHITE
                if pc.piece_type == chess.PAWN and chess.square_rank(frm) in (0, 7): continue
                mv = chess.Move(frm, psq)
                if mv not in pre.legal_moves or not pre.is_valid(): continue
                if pre.is_check(): continue
                c = pre.copy(); c.turn = chess.BLACK
                if c.is_check(): continue
                f0 = flights(pre); f1 = flights(post)
                if len(f1) < len(f0): continue
                ks = keys(pre)
                if ks == [mv]:
                    out.append((pre.board_fen(), sym + chess.square_name(sq), pre.san(mv), chess.square_name(frm), sorted(f0), sorted(f1)))
                    print(out[-1], flush=True)
