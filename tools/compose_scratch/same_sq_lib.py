"""Hill-climb post-key #2: two different black pieces move (no capture) to the SAME square next to the king,
each defeating the threat, each answered by its own mate that needs the block."""
import chess, random, sys, os
BAD_MOVERS = os.environ.get('BAD_MOVERS', '')
KS = chess.D4
ADJ = [s for s in chess.SQUARES if chess.square_distance(s, KS) == 1]
def m1(b):
    r = []
    for m in list(b.legal_moves):
        b.push(m); ok = b.is_checkmate(); b.pop()
        if ok: r.append(m)
    return r
def score_nn(b):
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
                p += 6 * sum(1 for n in a[1] | c[1] if n[0] in BAD_MOVERS)
                if a[1] & th or c[1] & th: p += 8
                if p < best: best, bpair = p, (chess.square_name(sq), a, c)
    return pen + best, bpair, th

def keys_for(post, info):
    """Unique keys (non-capture retractions) that keep both thematic mates and take no flight."""
    sq, a, c = info
    want = {chess.Move(a[0], chess.parse_square(sq)).uci(): a[1], chess.Move(c[0], chess.parse_square(sq)).uci(): c[1]}
    def flights(b):
        x = b.copy(); x.turn = chess.BLACK; k = x.king(chess.BLACK)
        return {m.to_square for m in x.legal_moves if m.from_square == k}
    def refuted(b):
        for r in list(b.legal_moves):
            b.push(r); ok = bool(m1(b)); b.pop()
            if not ok: return True
        return not any(True for _ in b.legal_moves) and not b.is_checkmate()
    out = []
    for psq, pc in post.piece_map().items():
        if pc.color != chess.WHITE: continue
        for frm in chess.SQUARES:
            if post.piece_at(frm) or (pc.piece_type == chess.PAWN and chess.square_rank(frm) in (0, 7)): continue
            pre = post.copy(); pre.remove_piece_at(psq); pre.set_piece_at(frm, pc); pre.turn = chess.WHITE
            mv = chess.Move(frm, psq)
            if not pre.is_valid() or mv not in pre.legal_moves or pre.is_check(): continue
            if len(flights(post)) < len(flights(pre)): continue
            ok = True
            for m in list(pre.legal_moves):
                pre.push(m); bad = refuted(pre); pre.pop()
                if (m == mv) == bad: ok = False; break
            if ok: out.append((pre.board_fen(), pre.san(mv), chess.square_name(frm)))
    return out
