"""Changed-mates search (E. Bourd's task, session 18): the SAME Black unit makes two defences, each answered by a
different mate in two phases (set play vs solution, or try vs solution).

Whole-diagram evaluation (the post-key search is useless for changed mates - see lessons.jsonl): a candidate
diagram passes when
  * set play: >= 2 moves of the thematic unit have exactly one mate each, with distinct mates;
  * a quiet, non-capturing White move with a unique threat exists after which the same defences get one mate each,
    all different (problemist identity: piece + diagram square + destination) from the set mates;
  * the diagram has no White mate in 1.
Holes (Black moves without a mate) are tolerated and counted; `close()` then adds units by beam search until the
post-key play is hole- and dual-free and the key is unique; `full()` runs the real solver.

NEGATIVE RESULT (session 18): four skeleton families (~5M positions) found geometries - bKd5 bSc6 guarding d4+e5
with wRe4 gives every set mate on d4 and every solution mate on e5, and 8/8/2n2B2/1K1k4/1Q2R3/8/8/8 is a reciprocal
Q/R change after 1...Se5/1...Sd4 - but nothing sound. What the search lacked is the composer's first step: a
Black effect that yields SEVERAL mates, then a selector between them (his 8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8:
self-blocks let either knight mate, the flight picks the knight, the bishop's capture picks the square).

    from chesscomp.compose.changed_mates_search import evaluate, enumerate_family, close, full
"""
from __future__ import annotations
import itertools, time
import chess
from .scheme_search import mates_after

W, B = chess.WHITE, chess.BLACK


def set_phase(board, tsq):
    """board: Black to move. -> (thematic {move: mate}, holes, duals) or None"""
    b = board
    them, holes, duals = {}, [], 0
    for d in b.legal_moves:
        b.push(d)
        over = b.is_game_over()
        ms = [] if over else mates_after(b)
        b.pop()
        if over or not ms:
            if not any(h.from_square == d.from_square and h.to_square == d.to_square for h in holes):
                holes.append(d)
            continue
        if len(ms) > 1:
            duals += 1
        if d.from_square == tsq and len(ms) == 1:
            them[d] = ms[0]
    return them, holes, duals


def key_phase(board, w, tsq, set_them):
    """board: White to move; w a White move. Returns dict or None."""
    b = board.copy(stack=False)
    if b.is_capture(w) or b.gives_check(w):
        return None
    b.push(w)
    b0 = b.copy(); b0.push(chess.Move.null())
    threats = mates_after(b0)
    if len(threats) != 1:
        return None
    t = threats[0]
    changed, holes, duals, refuted_by = {}, [], 0, []
    for d in b.legal_moves:
        b.push(d)
        over = b.is_game_over()
        ms = [] if over else mates_after(b)
        b.pop()
        if over or not ms:
            if not any(h.from_square == d.from_square and h.to_square == d.to_square for h in holes):
                holes.append(d)
            continue
        if any(m == t for m in ms):
            continue                       # threat works: not a defence
        if len(ms) > 1:
            duals += 1
        if d.from_square == tsq and d in set_them and len(ms) == 1:
            m = ms[0]; s = set_them[d]
            # problemist identity: piece type + DIAGRAM square + destination (the key piece is mapped back)
            origin = w.from_square if m.from_square == w.to_square else m.from_square
            mid = (b.piece_type_at(m.from_square), origin, m.to_square, m.promotion)
            sid = (board.piece_type_at(s.from_square), s.from_square, s.to_square, s.promotion)
            if mid != sid:
                changed[d] = m
    return {'key': w, 'threat': t, 'changed': changed, 'holes': holes, 'duals': duals}


def evaluate(board, tsq, min_changed=2, max_holes=6, key_from=None):
    """board: White to move (the diagram). Returns best key-phase dict (with set info) or None."""
    sb = board.copy(stack=False); sb.turn = B; sb.ep_square = None
    if not sb.is_valid() or sb.is_check():
        return None
    if mates_after(board):
        return None                      # mate in 1 in the diagram: cooked / no set play worth the name
    # cheap prefilter: the thematic unit alone
    q = {}
    for d in sb.legal_moves:
        if d.from_square != tsq:
            continue
        sb.push(d)
        ms = [] if sb.is_game_over() else mates_after(sb)
        sb.pop()
        if len(ms) == 1:
            q[d] = ms[0]
    if len(q) < min_changed or len(set(m.uci() for m in q.values())) < min_changed:
        return None
    them, sholes, sduals = set_phase(sb, tsq)
    if len(them) < min_changed or len(set(m.uci() for m in them.values())) < min_changed:
        return None
    if len(sholes) > max_holes:
        return None
    best = None
    for w in board.legal_moves:
        if key_from is not None and w.from_square not in key_from:
            continue
        r = key_phase(board, w, tsq, them)
        if not r or len(r['changed']) < min_changed:
            continue
        if len(set(m.uci() for m in r['changed'].values())) < min_changed:
            continue
        if len(r['holes']) > max_holes:
            continue
        r['set'] = them; r['set_holes'] = sholes; r['set_duals'] = sduals
        r['score'] = (len(r['changed']) * 10 - 3 * len(r['holes']) - 2 * len(sholes)
                      - 4 * r['duals'] - 2 * sduals)
        if best is None or r['score'] > best['score']:
            best = r
    return best


def fmt(board, r):
    b = board.copy(stack=False)
    sb = b.copy(); sb.turn = B
    from chesscomp.core import san
    out = [f"FEN {b.fen().split()[0]}"]
    out.append('  set: ' + '  '.join(f"1...{san(sb, d)} 2.{_san_after(sb, d, m)}" for d, m in r['set'].items())
               + f"   holes={len(r['set_holes'])} duals={r['set_duals']}")
    kb = b.copy(); kb.push(r['key'])
    out.append(f"  key: 1.{san(b, r['key'])} (2.{_san_after(kb, chess.Move.null(), r['threat'])})  "
               + '  '.join(f"1...{san(kb, d)} 2.{_san_after(kb, d, m)}" for d, m in r['changed'].items())
               + f"   holes={len(r['holes'])} duals={r['duals']}  score={r['score']}")
    if r['holes']:
        out.append('  key holes: ' + ' '.join(san(kb, h) for h in r['holes'][:8]))
    if r['set_holes']:
        out.append('  set holes: ' + ' '.join(san(sb, h) for h in r['set_holes'][:8]))
    return '\n'.join(out)


def _san_after(b, d, m):
    from chesscomp.core import san
    bb = b.copy(); bb.push(d)
    return san(bb, m)


def place(pieces: dict[int, chess.Piece]):
    b = chess.Board(None)
    for sq, p in pieces.items():
        b.set_piece_at(sq, p)
    b.turn = W
    return b


def enumerate_family(fixed, slots, tsq, min_changed=2, max_holes=6, key_from=None, limit=None, verbose=True):
    """fixed: {sq: Piece}; slots: list of (piece, [candidate squares]). Yields (board, result)."""
    t0, n, hits = time.time(), 0, []
    for combo in itertools.product(*[s[1] for s in slots]):
        if len(set(combo)) != len(combo) or any(c in fixed for c in combo):
            continue
        pieces = dict(fixed)
        for (p, _), sq in zip(slots, combo):
            pieces[sq] = p
        b = place(pieces)
        if not b.is_valid():
            continue
        n += 1
        r = evaluate(b, tsq, min_changed, max_holes, key_from)
        if r:
            hits.append((b, r))
            if verbose:
                print(fmt(b, r)); print()
        if limit and len(hits) >= limit:
            break
    if verbose:
        print(f'{n} positions, {len(hits)} hits, {time.time()-t0:.0f}s')
    return hits


# ---------------------------------------------------------------- stage 2/3: hole closing, full analysis
from ..core import Problem, Stipulation
from ..analysis import analyse
from ..report import format_report

ADD = [chess.Piece(chess.PAWN, B), chess.Piece(chess.PAWN, W), chess.Piece(chess.KNIGHT, B), chess.Piece(chess.BISHOP, B),
       chess.Piece(chess.ROOK, B), chess.Piece(chess.KNIGHT, W), chess.Piece(chess.BISHOP, W), chess.Piece(chess.ROOK, W)]


def n_keys(board, time_limit=20):
    """Fast cook check: number of White first moves with no refutation (checks and captures included)."""
    from chesscomp.solver import Engine
    eng = Engine(time_limit)
    b = board.copy(stack=False)
    n = 0
    for w in b.legal_moves:
        b.push(w)
        try:
            refs = eng.refutations(b, 2, 'direct', limit=0)
        finally:
            b.pop()
        if refs is not None and not refs:
            n += 1
            if n > 1:
                break
    return n


def cost(r, tsq):
    them_holes = sum(1 for h in r['set_holes'] if h.from_square == tsq)
    c = 10 * len(r['holes']) + 6 * r['duals'] + 3 * r['set_duals'] + 4 * them_holes + 1 * len(r['set_holes'])
    if 'cooks' in r:
        c += 8 * r['cooks']
    return c


def close(board, tsq, key_from, beam=8, depth=4, adds=ADD, min_changed=2, verbose=True):
    """board: diagram, White to move. key_from: from-square of the intended key (int)."""
    r0 = evaluate(board, tsq, min_changed, 99, {key_from})
    if not r0:
        return []
    frontier = [(board, r0)]
    done = []
    for d in range(depth):
        cand, seen = [], set()
        for b, r in frontier:
            for sq in chess.SQUARES:
                if b.piece_at(sq):
                    continue
                for p in adds:
                    if p.piece_type == chess.PAWN and chess.square_rank(sq) in (0, 7):
                        continue
                    nb = b.copy(stack=False); nb.set_piece_at(sq, p)
                    if not nb.is_valid():
                        continue
                    f = nb.fen().split()[0]
                    if f in seen:
                        continue
                    seen.add(f)
                    nr = evaluate(nb, tsq, min_changed, 99, {key_from})
                    if not nr:
                        continue
                    if not nr['holes'] and not nr['duals']:
                        nr['cooks'] = n_keys(nb) - 1
                    if cost(nr, tsq) >= cost(r, tsq):
                        continue
                    cand.append((nb, nr))
        cand.sort(key=lambda x: (cost(x[1], tsq), -x[1]['score']))
        frontier = cand[:beam]
        if verbose:
            print(f'depth {d+1}: {len(cand)} improvements, best (cost, keyholes, keyduals, setduals, setholes, cooks):',
                  [(cost(r, tsq), len(r['holes']), r['duals'], r['set_duals'], len(r['set_holes']), r.get('cooks')) for _, r in frontier])
        for b, r in frontier:
            if not r['holes'] and not r['duals'] and r.get('cooks') == 0 and (b.fen(), ) not in {(x.fen(),) for x, _ in done}:
                done.append((b, r))
        if not frontier:
            break
    close.frontier = frontier
    done.sort(key=lambda x: (cost(x[1], tsq), -x[1]['score']))
    return done


def full(board, verbose=True):
    p = Problem(board.copy(stack=False), Stipulation.parse('#2'))
    res = analyse(p, time_limit=60)
    if verbose:
        print(format_report(res))
    return p, res


def critique_it(p, res):
    from chesscomp.critique import critique, format_critique
    print('Critique:'); print(format_critique(critique(p, res)))
