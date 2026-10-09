"""Rank key retractions of a post-key position by number of extra keys (cooks), flight change shown."""
import chess, sys
def m1(b):
    r = []
    for m in list(b.legal_moves):
        if not b.gives_check(m): continue
        b.push(m)
        if b.is_checkmate(): r.append(m)
        b.pop()
    return r
post = chess.Board(sys.argv[1] + ' b - - 0 1')
def flights(b):
    x = b.copy(); x.turn = chess.BLACK; k = x.king(chess.BLACK)
    return len([m for m in x.legal_moves if m.from_square == k])
def refuted(b):
    if not any(True for _ in b.legal_moves): return not b.is_checkmate()
    for r in list(b.legal_moves):
        b.push(r); ok = bool(m1(b)); b.pop()
        if not ok: return True
    return False
res = []
for psq, pc in post.piece_map().items():
    if pc.color != chess.WHITE: continue
    for frm in chess.SQUARES:
        if post.piece_at(frm) or (pc.piece_type == chess.PAWN and chess.square_rank(frm) in (0, 7)): continue
        pre = post.copy(); pre.remove_piece_at(psq); pre.set_piece_at(frm, pc); pre.turn = chess.WHITE
        mv = chess.Move(frm, psq)
        if not pre.is_valid() or mv not in pre.legal_moves or pre.is_check() or pre.gives_check(mv): continue
        pre.push(mv); works = not refuted(pre); pre.pop()
        if not works: continue
        cooks = []
        for m in list(pre.legal_moves):
            if m == mv: continue
            pre.push(m); r = refuted(pre); pre.pop()
            if not r: cooks.append(pre.san(m))
            if len(cooks) > 4: break
        res.append((len(cooks), pre.san(mv), chess.square_name(frm), flights(pre), flights(post), cooks, pre.board_fen()))
for r in sorted(res)[:8]: print(r)
