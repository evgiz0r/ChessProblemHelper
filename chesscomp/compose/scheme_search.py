"""Scheme-first search (technique from E. Bourd, session 4): get the POST-KEY play clean before
thinking about a key at all.

Why this is fast: a sound post-key position of a #2 is simply a position where White mates in 1 after
EVERY Black reply. No refutation search over all White first moves is needed, so each candidate costs
milliseconds instead of ~0.3 s. Only when a scheme is clean do we call compose.key_candidates to look
for keys (and then for thematic tries).

Scored for a half-pin scheme:
  * every Black reply must be answerable (else the position cannot be a post-key position)
  * a unique threat (the mate that works against non-defences)
  * defences by BOTH half-pinned units, each with exactly ONE mate  -> dual avoidance
  * the pin must be used: removing the half-pinning White unit must break the mate
"""
from __future__ import annotations
import random, time
import chess
from ..core import Problem, Stipulation, san

PIECE_OF = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'S': chess.KNIGHT, 'P': chess.PAWN}


def mates_after(board: chess.Board) -> list[chess.Move]:
    out = []
    for m in board.legal_moves:
        board.push(m)
        if board.is_checkmate():
            out.append(m)
        board.pop()
    return out


def analyse_core(board: chess.Board, pin_sq: int, halfpin: tuple[int, int]):
    """Like analyse_postkey but TOLERANT: Black replies with no mate are counted as 'holes' instead of
    rejecting the position. This is the composer's prototype stage: get the thematic core, then close holes."""
    b0 = board.copy(); b0.push(chess.Move.null())
    threats = mates_after(b0)
    if not threats:
        return None
    tset = {m.uci() for m in threats}
    defs, duals, holes = [], 0, []
    for d in board.legal_moves:
        board.push(d)
        over = board.is_game_over() and not board.is_checkmate()
        ms = [] if over else mates_after(board)
        board.pop()
        if over or not ms:
            holes.append(d); continue
        if any(m.uci() in tset for m in ms):
            continue
        defs.append((d, ms))
        if len(ms) > 1:
            duals += 1
    hp = {}
    for d, ms in defs:
        if d.from_square in halfpin:
            hp.setdefault(d.from_square, []).append((d, ms))
    return {'threats': threats, 'threat_dual': len(threats) > 1, 'defences': defs, 'duals': duals,
            'halfpin': hp, 'holes': holes}


def score_core(board, pin_sq, halfpin, hole_penalty=0.6, want_each=2):
    """Score a thematic CORE: reward clean dual-free half-pin play with distinct mates, tolerate holes."""
    a = analyse_core(board, pin_sq, halfpin)
    if a is None:
        return -1e6, None
    s = -material_penalty(board) - hole_penalty * len(a['holes'])
    s -= 8 * a['duals']
    if a['threat_dual']:
        s -= 20
    s += 6 * len(a['halfpin'])
    # content is measured per PIECE, not per move: many moves of one piece giving the same mate is not content
    per_piece, clean = {}, 0
    for sq, lst in a['halfpin'].items():
        mates, used = set(), set()
        for d, ms in lst:
            if len(ms) == 1:
                mates.add(ms[0].uci())
                if pin_exploited(board, pin_sq, halfpin, d, ms[0]):
                    used.add(ms[0].uci())
            else:
                s -= 6
        per_piece[sq] = (mates, used)
        clean += len(used)
        s += 5 * len(used) + 1.5 * len(mates - used)      # pin-exploiting mates are the thematic ones
        if len(used) >= 2:
            s += 6                                        # two different pin-mates from one piece
    if len(per_piece) == 2:
        (sq1, (m1, u1)), (sq2, (m2, u2)) = list(per_piece.items())
        if u1 and u2 and not (u1 & u2):
            s += 20                                       # both units give their OWN pin-exploiting mate
            # the 'additional effect' (E. Bourd s5): why does each mate fail after the other defence?
            reasons, kinds = [], set()
            for (sqa, ua), (sqb, ub) in (((sq1, u1), (sq2, u2)), ((sq2, u2), (sq1, u1))):
                da = next(d for d, ms in a['halfpin'][sqb] if len(ms) == 1 and ms[0].uci() in ub)
                for mu in ua:
                    r = avoidance_reason(board, da, chess.Move.from_uci(mu))
                    reasons.append(r)
                    kinds.add('flight' if 'king escapes' in r else
                              'none' if 'no avoidance' in r else
                              'capture' if 'captures the mating unit' in r else 'other')
                    if 'king escapes' in r:
                        s -= 4
                    elif 'no avoidance' in r:
                        s -= 12
                    else:
                        s += 7
            # E. Bourd s6: the KIND of avoidance should be the same in both variations (second-layer unity)
            if len(kinds - {'none'}) == 1:
                s += 12
            a['avoidance'] = reasons; a['avoidance_kinds'] = sorted(kinds)
        else:
            s -= 4
        s += 3 * len((u1 | u2))
    hp_mates = sorted(set().union(*[m for m, u in per_piece.values()])) if per_piece else []
    s -= 0.8 * bin(board.occupied).count('1')
    a['clean_pin'] = clean; a['hp_mates'] = hp_mates
    return s, a


def analyse_postkey(board: chess.Board, pin_sq: int, halfpin: tuple[int, int]):
    """board: Black to move. Returns dict or None if not a valid post-key position."""
    b0 = board.copy(); b0.push(chess.Move.null())
    threats = mates_after(b0)
    if not threats:
        return None
    tset = {m.uci() for m in threats}
    defs, duals = [], 0
    for d in board.legal_moves:
        board.push(d)
        if board.is_game_over():
            board.pop(); return None                   # Black escapes (stalemate etc.)
        ms = mates_after(board)
        board.pop()
        if not ms:
            return None                                # a refutation: not a post-key position
        if any(m.uci() in tset for m in ms):
            continue                                   # threat still works: not a defence
        defs.append((d, ms))
        if len(ms) > 1:
            duals += 1
    hp = {}
    for d, ms in defs:
        if d.from_square in halfpin:
            hp.setdefault(d.from_square, []).append((d, ms))
    return {'threats': threats, 'threat_dual': len(threats) > 1, 'defences': defs, 'duals': duals, 'halfpin': hp}


def pin_exploited(board: chess.Board, pin_sq: int, halfpin, d: chess.Move, mate: chess.Move):
    """Is the SELF-PIN genuinely exploited by the mate? (E. Bourd, session 5)

    Not enough that the mate collapses when the half-pinner is removed - the half-pinner may merely be
    guarding the mating piece (e.g. 2.Qxe5# protected by Bh8), or the mate may capture the pinned unit.
    The pin is exploited only if the pinned Black unit is still on the board and, WERE IT NOT PINNED,
    it could parry the mate: capture the mating unit, or interpose on the checking line.
    Returns None or a short reason string.
    """
    b = board.copy(); b.push(d)
    other = [x for x in halfpin if x != d.from_square]
    if not other:
        return None
    P = other[0]
    if not b.piece_at(P) or b.color_at(P) != chess.BLACK:
        return None
    if not b.is_pinned(chess.BLACK, P):
        return None
    after = b.copy(); after.push(mate)
    if mate.to_square == P:
        return None                                  # the mate simply captures the pinned unit
    if not after.is_checkmate():
        return None
    checker = mate.to_square
    k = after.king(chess.BLACK)
    line = chess.SquareSet(chess.between(checker, k))
    att = after.attacks(P)
    # a pinned PAWN also cannot PUSH to interpose - add its forward squares to the parry set
    push_sqs = set()
    if after.piece_type_at(P) == chess.PAWN:
        step = -8 if after.color_at(P) == chess.BLACK else 8
        one = P + step
        if 0 <= one < 64 and not after.piece_at(one):
            push_sqs.add(one)
            start = 6 if after.color_at(P) == chess.BLACK else 1
            two = one + step
            if chess.square_rank(P) == start and 0 <= two < 64 and not after.piece_at(two):
                push_sqs.add(two)
    if checker in att:
        return f'pinned {chess.piece_symbol(after.piece_type_at(P)).upper()}{chess.square_name(P)} cannot capture on {chess.square_name(checker)}'
    inter = [x for x in line if (x in att or x in push_sqs) and not after.piece_at(x)]
    if inter:
        nmp = chess.piece_symbol(after.piece_type_at(P)).upper().replace('P', '')
        return f'pinned {nmp}{chess.square_name(P)} cannot interpose on {chess.square_name(inter[0])}'
    return None


def pin_used(board, pin_sq, d, mate):          # kept for older callers
    b = board.copy(); b.push(d); b.push(mate)
    t = b.copy(); t.remove_piece_at(pin_sq)
    return not t.is_checkmate()


def avoidance_reason(board: chess.Board, d_other: chess.Move, mate: chess.Move):
    """Why does `mate` fail after the OTHER thematic defence? (the 'additional effect')"""
    b = board.copy(); b.push(d_other)
    if mate not in b.legal_moves:
        if b.piece_at(mate.to_square) and b.color_at(mate.to_square) == chess.WHITE:
            return 'mating square occupied by the defender-freed White unit'
        blockers = [x for x in chess.SquareSet(chess.between(mate.from_square, mate.to_square)) if b.piece_at(x)]
        if blockers:
            return f'line to {chess.square_name(mate.to_square)} blocked on {chess.square_name(blockers[0])}'
        return 'mating move no longer legal'
    a = b.copy(); a.push(mate)
    if not a.is_check():
        return 'no longer gives check'
    esc = []
    for m in a.legal_moves:
        if m.to_square == mate.to_square:
            esc.append(f'{chess.square_name(m.from_square)} captures the mating unit')
        elif m.from_square == a.king(chess.BLACK):
            esc.append(f'king escapes to {chess.square_name(m.to_square)}')
        else:
            esc.append(f'interposition {chess.square_name(m.from_square)}-{chess.square_name(m.to_square)}')
    return '; '.join(esc[:2]) if esc else 'still mate (no avoidance!)' 


def material_penalty(board):
    """Realistic material: at most 1 Q, 2 R, 2 B (opposite colours), 2 S, 8 P per side."""
    pen = 0.0
    for col in (chess.WHITE, chess.BLACK):
        for pt, lim in ((chess.QUEEN, 1), (chess.ROOK, 2), (chess.BISHOP, 2), (chess.KNIGHT, 2), (chess.PAWN, 8)):
            pen += 12 * max(0, len(board.pieces(pt, col)) - lim)
        bs = list(board.pieces(chess.BISHOP, col))
        if len(bs) == 2 and (chess.square_file(bs[0]) + chess.square_rank(bs[0])) % 2 == \
                            (chess.square_file(bs[1]) + chess.square_rank(bs[1])) % 2:
            pen += 8
    return pen


def score_scheme(board, pin_sq, halfpin, want_each=2):
    a = analyse_postkey(board, pin_sq, halfpin)
    if a is None:
        return -1e6, None
    s = -material_penalty(board)
    s -= 8 * a['duals']
    if a['threat_dual']:
        s -= 20                                          # a dual threat wrecks the scheme
    s += 8 * len(a['halfpin'])                           # defences from both half-pinned units
    clean, hp_mates = 0, []
    for sq, lst in a['halfpin'].items():
        n = 0
        for d, ms in lst:
            if len(ms) == 1:
                if pin_used(board, pin_sq, d, ms[0]):
                    s += 8; clean += 1; hp_mates.append(ms[0].uci()); n += 1
                else:
                    s += 1                               # self-pin not exploited: weak
            else:
                s -= 6
        s += 4 if n >= want_each else 0                   # ~2 thematic defences per unit
    # dual avoidance is only meaningful if the mates DIFFER
    if hp_mates:
        s += 7 * len(set(hp_mates)) - 3 * (len(hp_mates) - len(set(hp_mates)))
    s -= 0.8 * bin(board.occupied).count('1')
    a['clean_pin'] = clean
    a['hp_mates'] = hp_mates
    return s, a


def report(board, a, pin_sq):
    """Album-ish listing of a scheme/core."""
    out = [f"threat: {'/'.join(san(board.copy().mirror() and board, t) for t in [])}"]
    b0 = board.copy(); b0.push(chess.Move.null())
    out = ['threat: ' + '/'.join(san(b0, t) for t in a['threats'])]
    if a.get('holes'):
        bb = board.copy()
        out.append(f"   holes ({len(a['holes'])}): " + ', '.join(san(bb, h) for h in a['holes'][:12]))
    for d, ms in a['defences']:
        tag = ''
        if d.from_square in a['halfpin'] and len(ms) == 1:
            tag = '  [half-pin' + (', pin used' if pin_used(board, pin_sq, d, ms[0]) else '') + ']'
        bb = board.copy(); dn = san(bb, d); bb.push(d)
        out.append(f"   1...{dn} 2.{'/'.join(san(bb, m) for m in ms)}{'  [DUAL]' if len(ms) > 1 else ''}{tag}")
    return '\n'.join(out)


# Black half-batteries made of two PAWNS (E. Bourd's task, session 8). Pawns leave a rank or a diagonal
# simply by advancing, so these are the natural geometries; on a file they could only leave by capturing.
PAWN_SKELETONS = {
    'rank5-a5':  ('e5', ('R', 'a5'), ('c5', 'd5')),
    'rank4-b4':  ('e4', ('R', 'b4'), ('c4', 'd4')),
    'rank4-a4':  ('e4', ('Q', 'a4'), ('c4', 'd4')),
    'rank5-h5':  ('d5', ('R', 'h5'), ('f5', 'e5')),
    'diagA1':    ('e5', ('B', 'a1'), ('c3', 'd4')),
    'diagH8':    ('d4', ('B', 'h8'), ('f6', 'e5')),
    'diagH1':    ('d4', ('B', 'h1'), ('f3', 'e3')),
    'diagA8':    ('e4', ('B', 'a8'), ('c6', 'd5')),
}

SKELETONS = {
    # name: (black king, half-pinning White piece+square, the two half-pinned Black squares)
    'diag-h8': ('d4', ('B', 'h8'), ('f6', 'e5')),
    'diag-a1': ('d4', ('B', 'a1'), ('b2', 'c3')),
    'file-e1': ('e4', ('R', 'e1'), ('e2', 'e3')),
    'rank-h4': ('d4', ('R', 'h4'), ('g4', 'f4')),
    'diag-a8': ('e4', ('B', 'a8'), ('c6', 'd5')),
}


def search(skeleton='diag-h8', seconds=120, seed=0, wk='b5', black_pair=('Q', 'S'),
           pool_w='QRBSSPP', pool_b='RBSPP', max_units=14, log=None):
    rng = random.Random(seed)
    bk, (hp_pc, hp_sq), (s1, s2) = SKELETONS[skeleton]
    fixed = {bk: ('b', 'K'), wk: ('w', 'K'), hp_sq: ('w', hp_pc), s1: ('b', black_pair[0]), s2: ('b', black_pair[1])}

    def build(pos):
        b = chess.Board(None)
        for sq, (c, p) in pos.items():
            b.set_piece_at(chess.parse_square(sq), chess.Piece(PIECE_OF.get(p, chess.KING) if p != 'K' else chess.KING,
                                                               c == 'w'))
        b.turn = chess.BLACK
        b.castling_rights = 0
        return b

    def ok(pos):
        for sq, (c, p) in pos.items():
            if p == 'P' and sq[1] in '18':
                return False
        b = build(pos)
        return b.is_valid() and not b.is_check()

    def mutate(pos):
        pos = dict(pos)
        movable = [q for q in pos if q not in fixed]
        free = [chess.square_name(i) for i in range(64) if chess.square_name(i) not in pos]
        r = rng.random()
        if (r < 0.45 or not movable) and free and len(pos) < max_units:
            col = 'w' if rng.random() < 0.6 else 'b'
            pos[rng.choice(free)] = (col, rng.choice(pool_w if col == 'w' else pool_b))
        elif r < 0.7 and movable:
            del pos[rng.choice(movable)]
        elif movable:
            sq = rng.choice(movable)
            v = pos.pop(sq)
            free = [chess.square_name(i) for i in range(64) if chess.square_name(i) not in pos]
            pos[rng.choice(free)] = v
        return pos

    pin_sq = chess.parse_square(hp_sq)
    halfpin = (chess.parse_square(s1), chess.parse_square(s2))
    cur = dict(fixed)
    cs, ca = score_scheme(build(cur), pin_sq, halfpin) if ok(cur) else (-1e6, None)
    best = (cs, cur, ca)
    t0 = time.time(); it = 0; last = 0
    while time.time() - t0 < seconds:
        it += 1
        cand = mutate(cur)
        if not ok(cand):
            continue
        sc, a = score_scheme(build(cand), pin_sq, halfpin)
        if sc >= cs or rng.random() < 0.04:
            cur, cs, ca = cand, sc, a
            if sc > best[0]:
                best = (sc, dict(cand), a)
                if log and time.time() - last > 20:
                    last = time.time()
                    log(f'   {int(time.time()-t0)}s it{it} score {sc:.1f}')
    return best, it


def to_fen(pos, turn='b'):
    b = chess.Board(None)
    for sq, (c, p) in pos.items():
        b.set_piece_at(chess.parse_square(sq), chess.Piece(PIECE_OF.get(p, chess.KING) if p != 'K' else chess.KING, c == 'w'))
    b.turn = chess.BLACK if turn == 'b' else chess.WHITE
    return b
