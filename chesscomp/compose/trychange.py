"""Fast pre-filter for changed mates between two first moves (try/key) on the same thematic defences.

No full solver: python-chess move generation only (about 100 positions a second), so it finds MECHANISMS, not
sound problems. For every quiet, non-checking move of the key piece that keeps the threat, it lists the mates
after each thematic defence (None when the defence does not stop the threat), then scores pairs of such moves:
single mates, all different between the two moves and between the defences, one threat, no holes.

    CORE=4r1b1/6Q1/8/2k5/8/8/8/8 SEED=... KP=g7 THREAT=Qd6# DEFS=e8e6,g8e6 ONLY=g7g6,g7h6 \\
        FORBID=f7,e7,d5,c4,e5,e4,e3 TARGET='{"Qh6":["Qc1#","Qe3#"]}' BUDGET_S=240 \\
        python -m chesscomp.compose.trychange JOB OUTFILE

KP: square of the key piece, or Q for the White queen wherever she stands. ONLY: restrict its moves (uci).
FORBID: squares that must stay empty (the thematic lines). TARGET: wanted mates per move SAN, in DEFS order.
MODE=posts scores one key (KEYS: the wanted ones) with the other moves as tries, each refuted once and differently.
MODE=set scores set play against the best key instead (setkey_evaluate): set and key mates single and changed,
no mate in one, no White check after which every Black reply is mated (check_cooks).

15 Oct 2026, Grimshaw on e6 (bK c5, bR e8, bB g8, threat Qd6#): it found the queen posts f6/g6/h6 with six
different mates (Qc3/Qf2, Qc2/Qg1, Qc1/Qe3) in four minutes, where chesscomp.compose.evolve found no changed
pair in twenty. It ignores two-move cooks (1.Qc3+ Bc4 2.Qxc4#): solve every hit with chesscomp.report.
"""
from __future__ import annotations
import json, os, random, sys, time
import chess


def _san(b, m):
    return b.san(m).replace('N', 'S')


def mates(b):
    out = []
    for m in b.legal_moves:
        b.push(m); ok = b.is_checkmate(); b.pop()
        if ok:
            out.append(_san(b, m).rstrip('#+') + '#')
    return out


def promoted(b):
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def phase_rows(b, kp, threat, defs, only=()):
    """One row per quiet move of the key piece that keeps `threat`: {move, thr, defs: [tuple of mates | None], p}."""
    rows = []
    if kp is None:
        kp = next(iter(b.pieces(chess.QUEEN, chess.WHITE)), None)
    for m in list(b.legal_moves):
        if m.from_square != kp or b.is_capture(m) or b.gives_check(m) or (only and m.uci() not in only):
            continue
        p = b.copy(); p.push(m)
        n = p.copy(); n.push(chess.Move.null())
        thr = mates(n) if n.is_valid() and not n.is_check() else []
        if threat not in thr:
            continue
        row = {'move': _san(b, m), 'uci': m.uci(), 'thr': len(thr), 'defs': [], 'p': p}
        for d in defs:
            if d not in p.legal_moves:
                row['defs'].append(None); continue
            p.push(d); ms = tuple(sorted(mates(p))); p.pop()
            row['defs'].append(None if threat in ms else ms)        # not a defence in this phase
        rows.append(row)
    return rows


def evaluate(b, kp, threat, defs, only=(), target=None):
    """(score, summary) of the best try/key pair of diagram b (White to move)."""
    target = target or {}
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid():
        return -1e9, ''
    s = -25.0 * sum(1 for m in n.legal_moves if m.from_square == n.king(chess.BLACK))
    if mates(b):
        s -= 60
    rows = phase_rows(b, kp, threat, defs, only)
    if len(rows) < 2:
        return s - 100 + 20 * len(rows), 'fewer than two threat moves'

    def good(r):
        return all(x and len(x) == 1 for x in r['defs']) and len({x[0] for x in r['defs']}) == len(defs)
    best, best_t = None, -1e9
    for i, r1 in enumerate(rows):
        for r2 in rows[i + 1:]:
            t = 0.0
            for a, c in zip(r1['defs'], r2['defs']):
                if not a or not c:
                    t -= 15; continue
                t += 10 if not set(a) & set(c) else -5
                t -= 4 * (len(a) - 1 + len(c) - 1)
                if len(a) == 1 and len(c) == 1 and a != c:
                    t += 12
            t -= 8 * (r1['thr'] - 1 + r2['thr'] - 1)
            for r in (r1, r2):
                sing = [x[0] for x in r['defs'] if x and len(x) == 1]
                if len(sing) != len(set(sing)):
                    t -= 25                                         # the same mate after both defences: no theme
                for x, want in zip(r['defs'], target.get(r['move'], [])):
                    if x and want in x:
                        t += 10 if len(x) == 1 else 4
            if good(r1) and good(r2):
                t += 20
            if t > best_t:
                best_t, best = t, (r1, r2)
    s += best_t
    holes = {}
    for r in best:
        p, h = r['p'], 0
        for d in list(p.legal_moves):
            p.push(d)
            if not p.is_game_over() and not mates(p):
                h += 1
            p.pop()
        holes[r['move']] = h
    s -= 2.5 * min(holes.values()) + 1.0 * max(holes.values())
    s -= max(0, len(b.piece_map()) - 12)
    return s, ' || '.join(f"{r['move']} thr{r['thr']} " + ' '.join('/'.join(x) if x else '-' for x in r['defs'])
                          + f" h{holes[r['move']]}" for r in best)


def set_mates(b, defs):
    """Mates after each defence played in the diagram (set play); None when the move is illegal there."""
    out = []
    for d in defs:
        n = b.copy(); n.push(chess.Move.null())
        if not n.is_valid() or d not in n.legal_moves:
            out.append(None); continue
        n.push(d); out.append(tuple(sorted(mates(n))))
    return out


def check_cooks(b):
    """White checks in the diagram after which every Black reply allows a mate (1.Qc3+ Bc4 2.Qxc4#)."""
    out = []
    for m in list(b.legal_moves):
        if not b.gives_check(m):
            continue
        b.push(m)
        replies = list(b.legal_moves)
        ok = bool(replies)
        for r in replies:
            b.push(r); mated = bool(mates(b)); b.pop()
            if not mated:
                ok = False; break
        b.pop()
        if ok:
            out.append(_san(b, m))
    return out


def setkey_evaluate(b, kp, threat, defs, only=()):
    """(score, summary): set play against the solution (E. Bourd, 15 Oct 2026: changes between the diagram and the
    key, the mates arriving on the two lines the Grimshaw opens). The best key among the key piece's moves."""
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid():
        return -1e9, ''
    s = -25.0 * sum(1 for m in n.legal_moves if m.from_square == n.king(chess.BLACK))
    if mates(b):
        s -= 80
    cooks = check_cooks(b)
    s -= 30 * len(cooks)
    sm = set_mates(b, defs)
    for x in sm:
        s += 10 if x and len(x) == 1 else (-4 * (len(x) - 1) if x else -10)
    rows = phase_rows(b, kp, threat, defs, only)
    if not rows:
        return s - 100, f'no key; set {sm}'
    best, bt = None, -1e9
    for r in rows:
        t = -8.0 * (r['thr'] - 1)
        for x, y in zip(sm, r['defs']):
            if not y:
                t -= 15; continue
            t += 10 if len(y) == 1 else -4 * (len(y) - 1)
            if x and not set(x) & set(y):
                t += 12
        sing = [y[0] for y in r['defs'] if y and len(y) == 1]
        if len(sing) != len(set(sing)):
            t -= 25
        if t > bt:
            bt, best = t, r
    p, h = best['p'], 0
    for d in list(p.legal_moves):
        p.push(d)
        if not p.is_game_over() and not mates(p):
            h += 1
        p.pop()
    s += bt - 2.5 * h - max(0, len(b.piece_map()) - 12)
    fmt = lambda v: ' '.join('/'.join(x) if x else '-' for x in v)
    return s, f"set {fmt(sm)} || {best['move']} thr{best['thr']} {fmt(best['defs'])} h{h}" + (f" cooks {cooks}" if cooks else '')


def refutations(p, threat_ok=True):
    """Black moves in post-key position p (Black to move) after which White has no mate."""
    out = []
    for d in list(p.legal_moves):
        p.push(d)
        if not p.is_checkmate() and not mates(p):
            out.append(p.peek())
        p.pop()
    return out


def posts_evaluate(b, kp, threat, defs, only=(), want_keys=()):
    """(score, summary): one key and the other moves of the key piece as tries, each refuted once and differently,
    the thematic defences answered by different mates in every phase and in the set (E. Bourd, 15 Oct 2026: the
    queen's posts g6/h6, maybe f6, with changes against the diagram)."""
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid():
        return -1e9, ''
    s = -25.0 * sum(1 for m in n.legal_moves if m.from_square == n.king(chess.BLACK))
    if mates(b):
        s -= 80
    cooks = check_cooks(b)
    s -= 30 * len(cooks)
    sm = set_mates(b, defs)
    s += sum(6 if x and len(x) == 1 else -4 for x in sm)
    rows = phase_rows(b, kp, threat, defs, only)
    if not rows:
        return s - 100, 'no threat move'
    phases = []
    for r in rows:
        refs = refutations(r['p'])
        r['refs'] = [r['p'].san(m) for m in refs]
        phases.append(r)
    s -= 12 * sum(1 for r in phases for y in r['defs'] if not y)   # every post keeps its thematic mates (tries too)
    keys = [r for r in phases if not r['refs']]
    s += 40 if len(keys) == 1 else (-30 * (len(keys) - 1) if keys else -20)
    tries = [r for r in phases if len(r['refs']) == 1]
    s += 12 * len(tries) - 3 * sum(max(0, len(r['refs']) - 1) for r in phases)
    if len({r['refs'][0] for r in tries}) == len(tries):
        s += 6 * len(tries)
    s -= 6 * sum(r['thr'] - 1 for r in phases)
    seen = [set(x) for x in sm if x]
    for r in phases:
        for y in r['defs']:
            if y and len(y) == 1:
                s += 4 + (6 if not any(set(y) <= z for z in seen) else 0)
                seen.append(set(y))
            elif y:
                s -= 3 * (len(y) - 1)
    if len(keys) == 1:
        k = keys[0]
        if want_keys and k['uci'] in want_keys:
            s += 25
        if all(y and len(y) == 1 for y in k['defs']) and all(not x or not set(x) & set(y) for x, y in zip(sm, k['defs'])):
            s += 20                                         # every thematic mate changed against the set
        s += 5 * sum(1 for r in tries if all(y and len(y) == 1 for y in r['defs']))
    s -= max(0, len(b.piece_map()) - 13)
    fmt = lambda v: ' '.join('/'.join(x) if x else '-' for x in v)
    return s, f"set {fmt(sm)} || " + ' | '.join(f"{r['move']} {fmt(r['defs'])} t{r['thr']} ref {','.join(r['refs'][:3]) or 'KEY'}"
                                                for r in phases) + (f" cooks {cooks}" if cooks else '')


WT = [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.KNIGHT, chess.PAWN, chess.PAWN, chess.ROOK, chess.BISHOP]
BT = [chess.BISHOP, chess.KNIGHT, chess.PAWN, chess.PAWN, chess.PAWN, chess.ROOK]


def legal(b, forbid=()):
    if len(b.pieces(chess.KING, chess.WHITE)) != 1 or len(b.pieces(chess.KING, chess.BLACK)) != 1:
        return False
    if any(chess.square_rank(sq) in (0, 7) for sq in b.pieces(chess.PAWN, chess.WHITE) | b.pieces(chess.PAWN, chess.BLACK)):
        return False
    return b.is_valid() and not b.is_check() and not promoted(b) and not any(b.piece_at(sq) for sq in forbid)


def mutate(b, core_sq, maxu=16):
    b = b.copy()
    free = [sq for sq in chess.SQUARES if not b.piece_at(sq)]
    mov = [sq for sq in chess.SQUARES if b.piece_at(sq) and sq not in core_sq]
    op = random.random()
    if (op < 0.35 and 64 - len(free) < maxu) or not mov:
        col = random.random() < 0.55
        b.set_piece_at(random.choice(free), chess.Piece(random.choice(WT if col else BT), col))
    elif op < 0.55:
        sq = random.choice(mov)
        if b.piece_type_at(sq) != chess.KING:
            b.remove_piece_at(sq)
    elif op < 0.85:
        sq = random.choice(mov); pc = b.piece_at(sq); b.remove_piece_at(sq)
        b.set_piece_at(random.choice([s for s in free if chess.square_distance(s, sq) <= 2] or free), pc)
    else:
        sq = random.choice(mov); pc = b.piece_at(sq)
        if pc.piece_type != chess.KING:
            b.set_piece_at(sq, chess.Piece(random.choice(WT if pc.color else BT), pc.color))
    return b


def main(argv=None):
    argv = argv or sys.argv[1:]
    job, out = int(argv[0]), argv[1]
    e = os.environ
    core = chess.Board(e['CORE'] + ' w - - 0 1')
    core_sq = {sq for sq in chess.SQUARES if core.piece_at(sq)}
    kp = None if e['KP'] == 'Q' else chess.parse_square(e['KP'])
    defs = [chess.Move.from_uci(u) for u in e['DEFS'].split(',')]
    only = {x for x in e.get('ONLY', '').split(',') if x}
    forbid = {chess.parse_square(x) for x in e.get('FORBID', '').split(',') if x}
    target = json.loads(e.get('TARGET', '{}'))
    random.seed(job * 7919 + int(time.time()))
    seed = chess.Board(e.get('SEED', e['CORE']) + ' w - - 0 1')
    if e.get('MODE') == 'set':
        ev = lambda b: setkey_evaluate(b, kp, e['THREAT'], defs, only)
    elif e.get('MODE') == 'posts':
        wk = {x for x in e.get('KEYS', '').split(',') if x}
        ev = lambda b: posts_evaluate(b, kp, e['THREAT'], defs, only, wk)
    else:
        ev = lambda b: evaluate(b, kp, e['THREAT'], defs, only, target)
    pop, seen, t0 = [(ev(seed), seed)], {}, time.time()
    while time.time() - t0 < float(e.get('BUDGET_S', '240')):
        _, par = random.choice(pop[:6]) if random.random() < 0.8 else random.choice(pop)
        ch = mutate(par, core_sq, int(e.get('MAX_UNITS', '16')))
        if random.random() < 0.3:
            ch = mutate(ch, core_sq)
        if not legal(ch, forbid) or ch.board_fen() in seen:
            continue
        r = ev(ch); seen[ch.board_fen()] = r
        pop.append((r, ch)); pop.sort(key=lambda x: -x[0][0]); pop = pop[:40]
    with open(out, 'w') as f:
        for fen, (sc, summ) in sorted(seen.items(), key=lambda x: -x[1][0])[:25]:
            f.write(f'{sc:.1f} | {fen} | {summ}\n')


if __name__ == '__main__':
    main()
