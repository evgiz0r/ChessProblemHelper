"""Evolutionary theme search (session 29): grow a #2 toward a theme specification, scoring every candidate
with the solver. Where pattern_search and kernel_search add one or two units around a sound kernel, this
starts from a sketch (a few fixed units: the theme's core) and mutates the rest: add, remove, move or
nudge a unit, keep the better candidates, repeat until the time budget runs out.

    CORE="8/3p4/8/4k3/8/8/8/8" SEED="8/3p4/8/4k3/8/8/8/3Q3K" DEFS=d6,d5 CHANGED=1 BUDGET_S=900 \\
        python -m chesscomp.compose.evolve JOB OUTFILE

CORE: units that never move or disappear (the theme's pieces). SEED: the starting position (must contain
CORE). DEFS: the thematic Black defences (SAN as the solver prints them) that must each get one mate,
all different, after a unique key. CHANGED=1 also rewards set mates for DEFS that the key changes.
Score (higher is better): soundness first (unique key; for unsound positions, fewer refutations of the
best try is better), then the thematic variations, then purity (no duals, quiet key, single threat),
then economy. CORR=d4 (Black correction mode) rewards, for the Black piece on that square, a random move with
one mate and corrections each with their own single mate (the solver's S~ lines); NCORR (default 2) corrections
are needed for a HIT, every move of that piece must defend, and DEFS may be empty. NOFLIGHT=1 (default) penalises
every diagram flight and refuses it in a HIT (the constitution makes it fatal); NOFLIGHT=0 restores the old
score, where only an unprovided flight costs. KEYROLE=1 (default) penalises a key piece out of play (fatal, E. Bourd on
daily No. 2) or idle in the diagram (guards nothing near the king, no set mate, blocks no line) and refuses both in a
HIT; KEYROLE=0 restores the old score. SELFBLOCK=N (self-block mode, daily No. 5) needs no DEFS: it rewards every
variation whose defence is a functional self-block (the motive 'self-block on ..': the defender stands next to its
king and the mate would fail without it), with distinct single mates; a HIT needs N such mates and no dual after a
self-block. A line starting HIT is a position that meets the whole specification; check it with
`tools/blog.py check` before believing it.
"""
import os, sys, random, time, json, chess
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import idle_key_piece, out_of_play_key
from chesscomp.motives import mate_motives

JOB = int(sys.argv[1]) if len(sys.argv) > 1 else 0
OUT = sys.argv[2] if len(sys.argv) > 2 else f'evolve_{JOB}.txt'
CORE = os.environ.get('CORE', '8/3p4/8/4k3/8/8/8/8')
SEED = os.environ.get('SEED', CORE)
DEFS = [d for d in os.environ.get('DEFS', 'd6,d5').split(',') if d]
CHANGED = os.environ.get('CHANGED', '0') == '1'
PATTERN = os.environ.get('PATTERN', '')            # e.g. 'Dombrovskis (refutation)': every DEF must carry it
TRYCHANGE = os.environ.get('TRYCHANGE', '0') == '1'  # reward tries whose mates for DEFS differ (or swap: reciprocal)
CORR = os.environ.get('CORR', '')                  # Black correction mode: square of the correcting piece
NCORR = int(os.environ.get('NCORR', '2'))
SELFBLOCK = int(os.environ.get('SELFBLOCK', '0'))      # self-block mode: N distinct self-block mates for a HIT
NOFLIGHT = os.environ.get('NOFLIGHT', '1') == '1'   # constitution: a diagram flight is fatal, so no HIT has one
KEYROLE = os.environ.get('KEYROLE', '1') == '1'     # E. Bourd: no HIT whose key piece is out of play or idle in the diagram
RECIP = os.environ.get('RECIP', '0') == '1'          # set play and key swap the mates of the two DEFS
TARGET = dict(x.split(':') for x in os.environ.get('TARGET', '').split(',') if ':' in x)   # exact mates, e.g. d6:Qe6#,d5:Ba4#
BUDGET = float(os.environ.get('BUDGET_S', '900'))
MAXU = int(os.environ.get('MAX_UNITS', '16'))
random.seed(int(os.environ.get('SEED_RNG', str(JOB * 7919 + int(time.time()) % 1000))))

core = chess.Board(CORE + ' w - - 0 1')
CORE_SQ = {sq: core.piece_at(sq) for sq in chess.SQUARES if core.piece_at(sq)}
WHITE_TYPES = [chess.QUEEN, chess.ROOK, chess.ROOK, chess.BISHOP, chess.BISHOP, chess.KNIGHT, chess.KNIGHT, chess.PAWN, chess.PAWN]
BLACK_TYPES = [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN, chess.PAWN, chess.QUEEN]

def promoted(b):
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and (chess.square_file(bs[0]) + chess.square_rank(bs[0])) % 2 == (chess.square_file(bs[1]) + chess.square_rank(bs[1])) % 2):
            return True
        if len(b.pieces(chess.PAWN, col)) > 8:
            return True
    return False

def legal(b):
    if len(b.pieces(chess.KING, chess.WHITE)) != 1 or len(b.pieces(chess.KING, chess.BLACK)) != 1:
        return False
    for sq in b.pieces(chess.PAWN, chess.WHITE) | b.pieces(chess.PAWN, chess.BLACK):
        if chess.square_rank(sq) in (0, 7):
            return False
    if not b.is_valid() or b.is_check() or promoted(b):
        return False
    n = b.copy(); n.push(chess.Move.null())
    if n.is_check():                       # Black king in check with White to move
        return False
    for m in b.legal_moves:                # no mate in one
        b.push(m); mate = b.is_checkmate(); b.pop()
        if mate:
            return False
    return True

def units(b):
    return sum(1 for sq in chess.SQUARES if b.piece_at(sq))

def var_map(ph):
    out = {}
    for v in ph['variations']:
        out[v['defence']['san'].rstrip('+#')] = v
    return out

def corr_score(ph):
    """(score, summary, ok) of the correction play of the piece on CORR in phase ph."""
    if not CORR:
        return 0.0, '', True
    mine = [v for v in ph['variations'] if v['defence']['uci'][:2] == CORR]
    t = -4.0 * sum(1 for v in mine if v['threat_repeat'] or not v['continuations'])   # moves that do not defend
    c = next((c for c in ph.get('corrections', []) if c['piece'][1:] == CORR), None)
    if not c:
        return t - 30, 'no S~', False
    r = c['random']
    t += 20 - 8 * len(r['duals'])
    single = [x for x in c['corrections'] if len(x['mates']) == 1]
    mates = [x['mates'][0] for x in single]
    t += 18 * len(set(mates) - {r['mate']}) - 8 * (len(c['corrections']) - len(single))
    distinct = len(set(mates)) == len(mates) and r['mate'] not in mates
    if distinct and len(single) >= NCORR:
        t += 15
    ok = (not r['duals'] and len(single) == len(c['corrections']) >= NCORR and distinct
          and all(v['continuations'] and not v['threat_repeat'] for v in mine))
    return t, f"S~ {r['mate']} | " + ' '.join(f"{x['move']}:{'/'.join(x['mates'])}" for x in c['corrections']), ok


def selfblocks(b, ph):
    """(distinct single mates, dual count) of the functional self-blocks in phase ph of diagram b."""
    bk = b.copy()
    if ph['type'] != 'set':
        bk.push(chess.Move.from_uci(ph['first_move']['uci']))
    else:
        bk.push(chess.Move.null())
    k = bk.king(chess.BLACK)
    mates, duals = set(), 0
    for v in ph['variations']:
        d = chess.Move.from_uci(v['defence']['uci'])
        if (v['threat_repeat'] or not v['continuations'] or v['refutes'] or d.from_square == k
                or not chess.BB_KING_ATTACKS[k] & chess.BB_SQUARES[d.to_square]):
            continue
        sb = [c for c in v['continuations']
              if any(w.startswith('self-block') for w in mate_motives(bk, d, chess.Move.from_uci(c['uci'])))]
        if not sb:
            continue
        if len(v['continuations']) == 1:
            mates.add(sb[0]['san'])
        else:
            duals += 1
    return mates, duals


def sb_score(b, ph):
    """(score, summary, ok) of the self-block play in phase ph (SELFBLOCK mode)."""
    if not SELFBLOCK:
        return 0.0, '', True
    mates, duals = selfblocks(b, ph)
    return 22 * len(mates) - 8 * duals, f"SB {'/'.join(sorted(mates))} duals={duals}", len(mates) >= SELFBLOCK and not duals


def score(b):
    """(score, summary, hit)"""
    p = Problem.from_fen(b.fen(), '#2')
    try:
        r = analyse(p, max_refutations=4, include_tries=True, include_set=True, time_limit=8)
    except Exception as e:
        return -1e9, 'error', False
    keys = r.get('keys') or []
    phases = r.get('phases') or []
    s = 0.0
    if not keys:
        tries = [ph for ph in phases if ph['type'] == 'try' and not ph.get('check_key')]
        best = min((len(ph['refutations']) if isinstance(ph['refutations'], list) else ph['refutations'] for ph in tries), default=9)
        s -= 40 + 10 * best
        cands = tries
    else:
        s -= 18 * (len(keys) - 1)
        cands = [ph for ph in phases if ph['type'] == 'key']
    setph = [ph for ph in phases if ph['type'] == 'set']
    setmap = var_map(setph[0]) if setph else {}
    best_theme, best_sum = -1e9, ''
    for ph in cands:
        t, mates = 0.0, []
        vm = var_map(ph)
        for d in DEFS:
            v = vm.get(d)
            if not v or v['threat_repeat'] or not v['continuations'] or v['refutes']:
                t -= 6; mates.append(None); continue
            t += 22
            if len(v['continuations']) == 1:
                t += 10
            else:
                t -= 6 * (len(v['continuations']) - 1)
            mates.append(v['continuations'][0]['san'])
            if d in TARGET:
                t += 20 if TARGET[d] in [c['san'] for c in v['continuations']] else -10
            if CHANGED:
                sv = setmap.get(d)
                if sv and sv['continuations']:
                    sm = {c['san'] for c in sv['continuations']}
                    t += 12 if v['continuations'][0]['san'] not in sm else 3
        real = [m for m in mates if m]
        if len(real) == len(DEFS) and len(set(real)) < len(real):
            t -= 30                                  # the same mate after two thematic defences is no theme
        if len(real) == len(DEFS) and len(set(real)) == len(real):
            t += 15
            if RECIP and len(DEFS) == 2:
                s0, s1 = setmap.get(DEFS[0]), setmap.get(DEFS[1])
                if s0 and s1 and s0['continuations'] and s1['continuations']:
                    m0 = {c['san'] for c in s0['continuations']}; m1 = {c['san'] for c in s1['continuations']}
                    if real[1] in m0 and real[0] in m1:
                        t += 30 - 4 * (len(m0) + len(m1) - 2)
        if ph.get('check_key'):
            t -= 25
        if KEYROLE and not ph.get('check_key'):
            km = chess.Move.from_uci(ph['first_move']['uci'])
            if out_of_play_key(b, km):
                t -= 30
            elif b.piece_type_at(km.from_square) != chess.KING and idle_key_piece(b, km, phases):
                t -= 12
        if 'x' in ph['first_move']['san']:
            t -= 20
        if len(ph.get('threat') or []) > 1:
            t -= 8 * (len(ph['threat']) - 1)
        if len(ph.get('threat') or []) == 1:
            t += 4
        t -= 3 * sum(1 for v in ph['variations'] if v['dual'] and v['defence']['san'].rstrip('+#') not in DEFS)
        ct, csum, _ = corr_score(ph)
        t += ct
        st, ssum, _ = sb_score(b, ph)
        t += st
        csum = (csum + ' ' + ssum).strip()
        if t > best_theme:
            best_theme, best_sum = t, f"{ph['type']} {ph['first_move']['san']} " + ' '.join(f'{d}:{m}' for d, m in zip(DEFS, mates)) + (' ' + csum if csum else '')
    s += best_theme
    s -= 1.5 * max(0, units(b) - 10)
    # flights in the diagram need set mates (E. Bourd: a diagram flight is fatal unless provided)
    n = b.copy(); n.push(chess.Move.null())
    kmoves = [m for m in n.legal_moves if n.piece_type_at(m.from_square) == chess.KING]
    for m in kmoves:
        sv = setmap.get(n.san(m).rstrip('+#'))
        if not (sv and sv['continuations']):
            s -= 10
        if NOFLIGHT:
            s -= 15
    pats = (r.get('relations') or {}).get('patterns', [])
    if PATTERN:
        got = {pt.get('defence') for pt in pats if pt['name'] == PATTERN}
        s += 25 * sum(1 for d in DEFS if d in got)
    keyph = [ph for ph in phases if ph['type'] == 'key']
    if TRYCHANGE and keyph:
        km = var_map(keyph[0])
        kmates = {d: km[d]['continuations'][0]['san'] for d in DEFS if d in km and km[d]['continuations']}
        bonus = 0
        for ph in phases:
            if ph['type'] != 'try' or ph.get('check_key'):
                continue
            nref = len(ph['refutations']) if isinstance(ph['refutations'], list) else ph['refutations']
            if nref > 1:
                continue
            tm = var_map(ph)
            tmates = {d: tm[d]['continuations'][0]['san'] for d in DEFS if d in tm and tm[d]['continuations'] and len(tm[d]['continuations']) == 1}
            if len(tmates) == len(DEFS) == len(kmates):
                b_ = 8 * sum(1 for d in DEFS if tmates[d] != kmates[d])
                if len(DEFS) == 2 and tmates[DEFS[0]] == kmates[DEFS[1]] and tmates[DEFS[1]] == kmates[DEFS[0]]:
                    b_ += 25                                   # reciprocal change
                bonus = max(bonus, b_)
        s += bonus
    hit = False
    if len(keys) == 1:
        ph = cands[0]; vm = var_map(ph)
        ok = all(d in vm and vm[d]['continuations'] and len(vm[d]['continuations']) == 1 and not vm[d]['threat_repeat'] for d in DEFS)
        ok = ok and len({vm[d]['continuations'][0]['san'] for d in DEFS}) == len(DEFS) and not ph.get('check_key')
        # a hit is a publishable shape: one threat (or a block), a quiet non-capturing key (session 29: the
        # search learned to plant a black unit for the key to take, and to accept triple threats)
        ok = ok and len(ph.get('threat') or []) <= 1 and 'x' not in ph['first_move']['san']
        if ok and PATTERN:
            got = {pt.get('defence') for pt in (r.get('relations') or {}).get('patterns', []) if pt['name'] == PATTERN}
            ok = all(d in got for d in DEFS)
        if ok and RECIP and len(DEFS) == 2:
            s0, s1 = setmap.get(DEFS[0]), setmap.get(DEFS[1])
            k0, k1 = vm[DEFS[0]]['continuations'][0]['san'], vm[DEFS[1]]['continuations'][0]['san']
            ok = bool(s0 and s1 and [c['san'] for c in s0['continuations']] == [k1] and [c['san'] for c in s1['continuations']] == [k0])
        if ok and CHANGED:
            ok = all(d in setmap and setmap[d]['continuations'] and vm[d]['continuations'][0]['san'] not in {c['san'] for c in setmap[d]['continuations']} for d in DEFS)
        if ok and TARGET:
            ok = all(vm[d]['continuations'][0]['san'] == TARGET[d] for d in TARGET if d in vm)
        ok = ok and corr_score(ph)[2] and sb_score(b, ph)[2] and not (NOFLIGHT and kmoves)
        if ok and KEYROLE:
            km = chess.Move.from_uci(ph['first_move']['uci'])
            ok = not out_of_play_key(b, km) and (b.piece_type_at(km.from_square) == chess.KING or not idle_key_piece(b, km, phases))
        hit = ok
    return s, f"keys={keys} {best_sum}", hit

def mutate(b):
    b = b.copy()
    free = [sq for sq in chess.SQUARES if b.piece_at(sq) and sq not in CORE_SQ]
    empty = [sq for sq in chess.SQUARES if not b.piece_at(sq)]
    op = random.random()
    if op < 0.30 and units(b) < MAXU:                       # add
        col = chess.WHITE if random.random() < 0.6 else chess.BLACK
        t = random.choice(WHITE_TYPES if col else BLACK_TYPES)
        b.set_piece_at(random.choice(empty), chess.Piece(t, col))
    elif op < 0.50 and free:                                # remove (never a king)
        sq = random.choice([s for s in free if b.piece_at(s).piece_type != chess.KING] or free)
        if b.piece_at(sq).piece_type != chess.KING:
            b.remove_piece_at(sq)
    elif op < 0.75 and free:                                # move anywhere
        sq = random.choice(free); pc = b.piece_at(sq)
        b.remove_piece_at(sq); b.set_piece_at(random.choice(empty), pc)
    elif free:                                              # nudge one step
        sq = random.choice(free); pc = b.piece_at(sq)
        f, r = chess.square_file(sq), chess.square_rank(sq)
        nb = [chess.square(f + df, r + dr) for df in (-1, 0, 1) for dr in (-1, 0, 1)
              if (df or dr) and 0 <= f + df < 8 and 0 <= r + dr < 8 and not b.piece_at(chess.square(f + df, r + dr))]
        if nb:
            b.remove_piece_at(sq); b.set_piece_at(random.choice(nb), pc)
    else:
        return mutate(b)
    for sq, pc in CORE_SQ.items():                          # the core never changes
        b.set_piece_at(sq, pc)
    return b

def main():
    t0 = time.time()
    seen = {}
    pop = []
    def consider(b):
        key = b.board_fen()
        if key in seen or not legal(b):
            return
        sc, summ, hit = score(b)
        seen[key] = sc
        pop.append((sc, key, summ))
        if hit:
            with open(OUT, 'a') as f:
                f.write(f'HIT {sc:.1f} | {key} | {summ}\n')
    seed = chess.Board(SEED + ' w - - 0 1')
    consider(seed)
    tries = 0
    while len(pop) < 6 and tries < 400 and time.time() - t0 < BUDGET:
        consider(mutate(seed)); tries += 1
    last_log = 0
    while time.time() - t0 < BUDGET and pop:
        pop.sort(key=lambda x: -x[0]); del pop[14:]
        parent = chess.Board(random.choice(pop[:6])[1] + ' w - - 0 1')
        child = parent
        for _ in range(random.choice((1, 1, 2, 3))):
            child = mutate(child)
        consider(child)
        if time.time() - last_log > 60:
            last_log = time.time()
            pop.sort(key=lambda x: -x[0])
            with open(OUT, 'a') as f:
                f.write(f'-- {int(time.time() - t0)}s evaluated {len(seen)} best {pop[0][0]:.1f} | {pop[0][1]} | {pop[0][2]}\n')
    pop.sort(key=lambda x: -x[0])
    with open(OUT, 'a') as f:
        for sc, key, summ in pop[:5]:
            f.write(f'TOP {sc:.1f} | {key} | {summ}\n')
        f.write(f'done {len(seen)} evaluated in {int(time.time() - t0)}s\n')

if __name__ == '__main__':
    main()
