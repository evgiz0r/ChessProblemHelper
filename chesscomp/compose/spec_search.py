"""Spec-driven composing search for #2.

A Spec states the composer's idea: core pieces, which piece plays the key, the intended threat,
and how thematic tries are recognised. The search mutates everything else and scores candidates with
the solver + critique rules (taught by E. Bourd). Designed to be driven by an AI in a loop:
propose spec -> search -> inspect report/critique -> adjust spec or position -> repeat.
"""
from __future__ import annotations
import random, time, json, sys
from dataclasses import dataclass, field
from collections import Counter
import chess
from ..core import Problem, Stipulation
from ..analysis import analyse, interference_motive
from ..solver import Engine, Budget


@dataclass
class Spec:
    core: dict                      # {'d5': ('w','R'), 'b6': ('w','S'), 'f4': ('b','K')}
    key_from: str                   # square of the piece that must play the key
    threat_ids: list                # acceptable threat ids, e.g. ['Sb6d5']
    try_theme: str = 'any'          # 'any' | 'interference' (tries must fail by White line closing)
    required: dict = field(default_factory=dict)   # e.g. {('w','Q'): 1}: pieces that must exist (may move)
    max_units: int = 16
    pool_w: str = 'QRRBBSPPPP'
    pool_b: str = 'QRRBBSSPPPP'
    weights: dict = field(default_factory=lambda: dict(
        key=10, threat=6, try_thematic=5, try_other=1.0, distinct_refs=2, variation=3.5, dual=-2,
        king_ref=-4, same_ref=-3, flight=-3, unit=-0.55, extra_material=-6, cook=-5, refs=-3))


def build(pos):
    b = chess.Board(None)
    for sq, (col, pc) in pos.items():
        b.set_piece_at(chess.parse_square(sq), chess.Piece(chess.Piece.from_symbol(pc.replace('S', 'N')).piece_type, col == 'w'))
    b.turn = chess.WHITE
    b.castling_rights = 0
    return b


def legal(pos):
    b = build(pos)
    if len(b.pieces(chess.KING, True)) != 1 or len(b.pieces(chess.KING, False)) != 1:
        return False
    if any(p == 'P' and sq[1] in '18' for sq, (c, p) in pos.items()):
        return False
    return b.is_valid()


def evaluate(spec: Spec, pos: dict, full=True):
    W = spec.weights
    if not legal(pos):
        return -1e9, None
    b = build(pos)
    eng = Engine(time_limit=5)
    refs = {}
    try:
        for w in list(b.legal_moves):
            b.push(w)
            try:
                r = eng.refutations(b, 2, 'direct', limit=3)
            finally:
                b.pop()
            if r is not None:
                refs[w] = len(r)
    except Budget:
        return -1e9, None
    keys = [m for m, r in refs.items() if r == 0]
    s = W['unit'] * len(pos)
    cnt = Counter(pos.values())
    for col in 'wb':
        extra = max(0, cnt[(col, 'Q')] - 1) + max(0, cnt[(col, 'R')] - 2) + max(0, cnt[(col, 'S')] - 2) + max(0, cnt[(col, 'B')] - 2)
        bs = [(ord(q[0]) + int(q[1])) % 2 for q, v in pos.items() if v == (col, 'B')]
        extra += len(bs) - len(set(bs))
        extra += max(0, cnt[(col, 'P')] - 8)
        s += W['extra_material'] * extra
    for pc, n in spec.required.items():
        if cnt[pc] != n:
            s -= 25
    kf = chess.parse_square(spec.key_from)
    good_keys = [k for k in keys if k.from_square == kf]
    s += W['cook'] * len([k for k in keys if k.from_square != kf]) + W['cook'] * max(0, len(good_keys) - 1)
    if len(keys) != 1 or not good_keys:
        best = min([r for m, r in refs.items() if m.from_square == kf] or [5])
        return s + W['refs'] * best, None
    if not full:
        return s + W['key'], None
    p = Problem(b, Stipulation.parse('#2'))
    r = analyse(p, max_refutations=1, time_limit=20)
    if r.get('timeout'):
        return s, None
    s += W['key']
    key = [ph for ph in r['phases'] if ph['type'] == 'key'][0]
    th = {t['id'] for t in key['threat']}
    s += W['threat'] if th and th <= set(spec.threat_ids) else (-4 if not th & set(spec.threat_ids) else 0)
    ksq = next(sq for sq, v in pos.items() if v == ('b', 'K'))
    # diagram flights (taught: king escape makes it easy)
    bb = b.copy(); bb.turn = chess.BLACK
    if bb.is_valid():
        s += W['flight'] * len([m for m in bb.legal_moves if m.from_square == bb.king(chess.BLACK)])
    # tries by the key piece
    tries = [ph for ph in r['phases'] if ph['type'] == 'try' and ph['first_move']['uci'][:2] == spec.key_from and ph['threat']]
    refl = []
    for t in tries:
        rf = t['refutations'][0]['uci']
        refl.append(rf)
        if rf[:2] == ksq:
            s += W['king_ref']
        thematic = True
        if spec.try_theme == 'interference':
            thematic = bool(interference_motive(b, t, key))
        s += W['try_thematic'] if thematic else W['try_other']
    c = Counter(refl)
    s += W['same_ref'] * sum(n - 1 for n in c.values())
    if len(c) >= 2:
        s += W['distinct_refs'] * (len(c) - 1)
    # variations
    mates = set()
    for v in key['variations']:
        if v['threat_repeat'] or not v['continuations']:
            continue
        if len(v['continuations']) > 1:
            s += W['dual']
        elif v['continuations'][0]['id'] not in mates:
            mates.add(v['continuations'][0]['id']); s += W['variation']
    # content (E. Bourd s2): reward mates exploiting Black errors, penalise pure guard/unguard
    try:
        from ..motives import explain_key_phase
        for e in explain_key_phase(Problem(b, Stipulation.parse('#2')), r):
            w = ' '.join(x for m in e['mates'] for x in m['why_works'])
            if any(k in w for k in ('self-block', 'interference', 'line opening', 'self-pin')):
                s += W.get('motive', 2.0)
            elif 'unguard' in w:
                s += W.get('unguard', -0.5)
    except Exception:
        pass
    return s, r


def mutate(spec, pos, rng):
    pos = dict(pos)
    free = [chess.square_name(i) for i in range(64) if chess.square_name(i) not in pos]
    movable = [sq for sq in pos if sq not in spec.core and pos[sq] != ('w', 'K')]
    op = rng.random()
    if len(pos) < spec.max_units and (op < 0.3 or not movable):
        col = 'w' if rng.random() < 0.4 else 'b'
        pos[rng.choice(free)] = (col, rng.choice(spec.pool_w if col == 'w' else spec.pool_b))
    elif len(pos) < spec.max_units - 1 and op < 0.45:          # paired: a defender + a White answer
        a, c = rng.sample(free, 2)
        pos[a] = ('b', rng.choice(spec.pool_b)); pos[c] = ('w', rng.choice(spec.pool_w))
    elif op < 0.65 and movable:
        del pos[rng.choice(movable)]
    elif op < 0.72:
        wk = next(sq for sq, v in pos.items() if v == ('w', 'K'))
        pos[rng.choice(free)] = pos.pop(wk)
    elif movable:
        sq = rng.choice(movable)
        pos[rng.choice(free)] = pos.pop(sq)
    return pos


def search(spec: Spec, start: dict, seconds=240, seed=1, log=None):
    rng = random.Random(seed)
    cur = dict(start); cs, cr = evaluate(spec, cur)
    best = (cs, cur, cr)
    t0 = time.time(); it = 0
    while time.time() - t0 < seconds:
        it += 1
        cand = mutate(spec, cur, rng)
        sc, r = evaluate(spec, cand)
        if sc >= cs or rng.random() < 0.02:
            cur, cs, cr = cand, sc, r
            if sc > best[0]:
                best = (sc, cand, r)
                if log:
                    log(f'{time.time()-t0:6.0f}s score {sc:.1f} ' + ' '.join(f"{v[0]}{v[1]}{k}" for k, v in sorted(cand.items())))
    return best, it


def pos_to_lists(pos):
    w = [f"{v[1]}{k}" for k, v in pos.items() if v[0] == 'w']
    b = [f"{v[1]}{k}" for k, v in pos.items() if v[0] == 'b']
    return w, b
