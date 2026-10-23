"""Evolutionary theme search (session 29): grow a #2 toward a theme specification, scoring every candidate
with the solver. Where pattern_search and kernel_search add one or two units around a sound kernel, this
starts from a sketch (a few fixed units: the theme's core) and mutates the rest: add, remove, move or
nudge a unit, keep the better candidates, repeat until the time budget runs out.

    CORE="8/3p4/8/4k3/8/8/8/8" SEED="8/3p4/8/4k3/8/8/8/3Q3K" DEFS=d6,d5 CHANGED=1 BUDGET_S=900 \\
        python -m chesscomp.compose.evolve JOB OUTFILE

CORE: units that never move or disappear (the theme's pieces). SEED: the starting position (must contain
CORE). DEFS: the thematic Black defences (SAN as the solver prints them) that must each get one mate,
all different, after a unique key. CHANGED=1 also rewards set mates for DEFS that the key changes;
a set dual after a DEF costs score and refuses a HIT (the set play is thematic).
Score (higher is better): soundness first (unique key; for unsound positions, fewer refutations of the
best try is better), then the thematic variations, then purity (no duals, quiet key, single threat),
then economy. CORR=d4 (Black correction mode) rewards, for the Black piece on that square, a random move with
one mate and corrections each with their own single mate (the solver's S~ lines); NCORR (default 2) corrections
are needed for a HIT, every move of that piece must defend, and DEFS may be empty. CTHREAT=1 (default) refuses a HIT
that the gate fails as a 'simple block': no threat, and every Black unit but the king answered by one mate on three or more
of its moves, corrections or not (daily No. 17 found 1.Qb5! R~ Sxd2#, Rd5 Qe2#, Rc4 Qxc4# that way); CTHREAT=0 allows them. CTRY=N (CORR mode)
rewards quiet tries refuted only by one move of the CORR piece that the key answers, one per distinct refutation, and
needs N of them for a HIT: without a try or a change the gate fails a single phase. NOFLIGHT=1 (default) penalises
every diagram flight and refuses it in a HIT (the constitution makes it fatal); NOFLIGHT=0 restores the old
score, where only an unprovided flight costs. KEYROLE=1 (default) penalises a key piece out of play (fatal, E. Bourd on
daily No. 2) or idle in the diagram (guards nothing near the king, no set mate, blocks no line) and refuses both in a
HIT; KEYROLE=0 restores the old score. SELFBLOCK=N (self-block mode, daily No. 5) needs no DEFS: it rewards every
variation whose defence is a functional self-block (the motive 'self-block on ..': the defender stands next to its
king and the mate would fail without it), with distinct single mates; a HIT needs N such mates and no dual after a
self-block. PATTERN with no DEFS (e.g. PATTERN=Half-pin NPAT=3, daily No. 7) rewards every key-phase defence the
solver reports with that pattern and a single mate, distinct mates only; a HIT needs NPAT of them (PATTERN=Self-pin
for direct self-pins by the defender, daily No. 8). KEY=e7e8n (fixed-key mode, daily No. 9: underpromotion) needs no DEFS:
it scores only the phase whose first move is KEY (uci), rewards it being the only key, and rewards NVAR (default 3)
distinct single mates after its real defences, any defences; a HIT needs exactly that key, at most one threat, NVAR
such mates and no flight. Put the promoting pawn and the black king in CORE. TRIES=N (with KEY, daily No. 12: corner key) rewards tries by the key piece whose single refutations are distinct and
answered after the key, and needs N of them for a HIT. BRISTOL=1 (with KEY, daily No. 11) also
needs the threat to follow KEY along its line (analysis.bristol) for a HIT, and rewards tries by the key piece whose single
refutation the key answers with a mate (E. Bourd's prototype: 1.Bd8? Bd6!, 1.Bb6? d6!). UNIQUE=1 makes every DEF the only defence of its unit (any other
move of that unit must let the threat mate; E. Bourd: "realistically all knight moves are the same"). A line starting HIT is a position that meets the whole specification; check it with
`tools/blog.py check` before believing it.
Type-1 changed mates (E. Bourd, 14 Oct 2026: one White piece mates in both phases on another line): DEFSQ=f3,a3 names
the thematic Black units by their diagram squares instead of DEFS, and TKEY=g5g6 the intended key (uci); the DEFS are
read off the TKEY phase (each unit's defending move, the one with fewest mates first), so the threat is free.
QMATE=1 wants every thematic mate, set and solution, given by the queen. Use with CHANGED=1 UNIQUE=1.
CANDS=Pd2,Sb2,Bf8,Kd8,pe7,sb3 restricts mutation to those units on those squares (upper case White, lower case Black,
S/s for knights): add one, remove one, or swap a unit for another candidate of the same colour. Use it when the guard
analysis has already named the job of every square; the blind search wastes most solves on units with no role.
WCORR=e7 (white correction mode, daily No. 10) needs no DEFS: it scores the moves of the White unit on that square
(chesscomp.compose.white_correction): a unique quiet key by it, a random refutation shared by at least two of its tries,
NCORR (default 2) distinct correction refutations, no king refutation, every thematic refutation answered in the key;
mates changed from the random stage score extra. Put the key piece and the black king in CORE.
"""
from chesscomp.core import illegal_position as _illegal
import os, sys, random, time, json, chess
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import idle_key_piece, out_of_play_key
from chesscomp.motives import mate_motives
from chesscomp.compose.unique_defence import extra_defences
from chesscomp.compose.white_correction import wcorr_score

JOB = int(sys.argv[1]) if len(sys.argv) > 1 else 0
OUT = sys.argv[2] if len(sys.argv) > 2 else f'evolve_{JOB}.txt'
CORE = os.environ.get('CORE', '8/3p4/8/4k3/8/8/8/8')
SEED = os.environ.get('SEED', CORE)
# The modes that need no DEFS start with none when DEFS is unset (daily No. 16: PATTERN=... NPAT=2 without DEFS= silently
# scored the default d6,d5, which the position did not have, for two minutes of four jobs).
_NODEFS = any(os.environ.get(k, '') for k in ('PATTERN', 'CORR', 'WCORR', 'KEY', 'DEFSQ')) or \
    os.environ.get('SELFBLOCK', '0') not in ('', '0')
DEFS = [d for d in os.environ.get('DEFS', '' if _NODEFS else 'd6,d5').split(',') if d]
CHANGED = os.environ.get('CHANGED', '0') == '1'
PATTERN = os.environ.get('PATTERN', '')            # e.g. 'Dombrovskis (refutation)': every DEF must carry it
TRYCHANGE = os.environ.get('TRYCHANGE', '0') == '1'  # reward tries whose mates for DEFS differ (or swap: reciprocal)
CORR = os.environ.get('CORR', '')                  # Black correction mode: square of the correcting piece
NCORR = int(os.environ.get('NCORR', '2'))
CTHREAT = os.environ.get('CTHREAT', '1') == '1'       # CORR mode: no HIT that the gate fails as a simple block
CTRY = int(os.environ.get('CTRY', '0'))              # CORR mode: N quiet tries each refuted only by a correction
NPAT = int(os.environ.get('NPAT', '2'))               # PATTERN with no DEFS: distinct pattern mates for a HIT
SELFBLOCK = int(os.environ.get('SELFBLOCK', '0'))      # self-block mode: N distinct self-block mates for a HIT
NOFLIGHT = os.environ.get('NOFLIGHT', '1') == '1'   # constitution: a diagram flight is fatal, so no HIT has one
KEYROLE = os.environ.get('KEYROLE', '1') == '1'     # E. Bourd: no HIT whose key piece is out of play or idle in the diagram
RECIP = os.environ.get('RECIP', '0') == '1'          # set play and key swap the mates of the two DEFS
UNIQUE = os.environ.get('UNIQUE', '0') == '1'        # each DEF is its unit's only defence (E. Bourd, 14 Oct 2026)
TARGET = dict(x.split(':') for x in os.environ.get('TARGET', '').split(',') if ':' in x)   # exact mates, e.g. d6:Qe6#,d5:Ba4#
WCORR = os.environ.get('WCORR', '')                  # white correction mode: square of the key piece
KEY = os.environ.get('KEY', '')                      # fixed-key mode: the key's uci, e.g. e7e8n
BRISTOL = os.environ.get('BRISTOL', '0') == '1'      # fixed-key mode: the threat must follow KEY on its line (daily No. 11)
NVAR = int(os.environ.get('NVAR', '3'))
TRIES = int(os.environ.get('TRIES', '0'))            # fixed-key mode: N tries by the key piece, refutations answered (daily No. 12)
DEFSQ = [x for x in os.environ.get('DEFSQ', '').split(',') if x]   # type-1: thematic units by square (needs TKEY)
TKEY = os.environ.get('TKEY', '')                    # type-1: the intended key (uci)
QMATE = os.environ.get('QMATE', '0') == '1'          # type-1: every thematic mate by the queen
BUDGET = float(os.environ.get('BUDGET_S', '900'))
CANDS = [(chess.parse_square(t[1:]), chess.Piece.from_symbol(t[0].replace('S', 'N').replace('s', 'n')))
         for t in os.environ.get('CANDS', '').split(',') if t]
MAXU = int(os.environ.get('MAX_UNITS', '16'))
random.seed(int(os.environ.get('SEED_RNG', str(JOB * 7919 + int(time.time()) % 1000))))

core = chess.Board(CORE + ' w - - 0 1')
CORE_SQ = {sq: core.piece_at(sq) for sq in chess.SQUARES if core.piece_at(sq)}
WHITE_TYPES = [chess.QUEEN, chess.ROOK, chess.ROOK, chess.BISHOP, chess.BISHOP, chess.KNIGHT, chess.KNIGHT, chess.PAWN, chess.PAWN]
BLACK_TYPES = [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN, chess.PAWN, chess.QUEEN]

def promoted(b):
    if _illegal(b):                                   # retro: pawn captures, promotions (17 Oct 2026)
        return True
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

def set_duals(setmap, defs):
    """The thematic defences whose set variation has more than one mate. In changed mates the set phase is thematic,
    so a set dual blurs the change (daily No. 18: CHANGED hits were accepted with 1...exd4 2.Qf4#/Qe2#/Qe1# in the set)."""
    return [d for d in defs if d in setmap and len(setmap[d]['continuations']) > 1]

def simple_block(ph):
    """The gate's 'simple block' (critique): a phase with no threat in which every Black unit but the king has one mate
    answering three or more of its moves. A correction alone does not save it."""
    if ph.get('threat'):
        return False
    groups = {}
    for v in ph['variations']:
        if v['defence']['san'][0] != 'K':
            groups.setdefault(v['defence']['uci'][:2], []).append(frozenset(c['id'] for c in v['continuations']))
    return bool(groups) and all(max(ms.count(m) for m in ms) >= 3 for ms in groups.values())


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
    if CTHREAT and ph['type'] == 'key' and simple_block(ph):
        t -= 15                    # the gate fails it ('simple block', daily No. 17)
        ok = False
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


def key_mode(r):
    """(score, summary, hit-ok) of the phase whose first move is KEY (fixed-key mode)."""
    phases = r.get('phases') or []
    ph = next((p for p in phases if p['type'] in ('key', 'try') and p['first_move']['uci'] == KEY), None)
    if not ph:
        return -60.0, f'{KEY} not a try', False
    keys = r.get('keys') or []
    t = 0.0
    if ph['type'] == 'key':
        t += 60 - 25 * (len(keys) - 1)
    else:
        refs = ph['refutations']
        t -= 10 * max(1, len(refs) if isinstance(refs, list) else refs) + 18 * len(keys)
    mates, duals = set(), 0
    for v in ph['variations']:
        if v['threat_repeat'] or not v['continuations'] or v.get('refutes'):
            continue
        if len(v['continuations']) == 1:
            mates.add(v['continuations'][0]['san'])
        else:
            duals += 1
    thr = {c['san'] for c in (ph.get('threat') or [])}
    mates -= thr
    t += 18 * min(len(mates), NVAR + 1) - 4 * duals
    nthr = len(ph.get('threat') or [])
    t += 4 if nthr == 1 else -8 * max(0, nthr - 1)
    ok = ph['type'] == 'key' and len(keys) == 1 and nthr <= 1 and len(mates) >= NVAR
    summ = f"{ph['type']} {ph['first_move']['san']} thr={'/'.join(sorted(thr))} mates={'/'.join(sorted(mates))} duals={duals}"
    if BRISTOL:
        bt, btxt, bok = bristol_terms(ph, phases)
        t += bt; ok = ok and bok; summ += ' ' + btxt
    if TRIES:
        refs = thematic_tries(ph, phases)
        t += 12 * min(len(refs), TRIES + 1)
        ok = ok and len(refs) >= TRIES
        summ += f" tries={'/'.join(sorted(refs)) or '-'}"
    return t, summ, ok


def thematic_tries(ph, phases):
    """The distinct single refutations of tries by the key piece that the key answers with a mate (corner key,
    daily No. 12: the key square is chosen because every other square of the piece falls to its own defence)."""
    fm = ph['first_move']['uci']
    answered = {v['defence']['san'].rstrip('+#') for v in ph['variations'] if v['continuations'] and not v['threat_repeat']}
    refs = set()
    for q in phases:
        if q['type'] != 'try' or q.get('check_key'):
            continue
        u = q['first_move']['uci']
        if u[:2] != fm[:2] or u == fm:
            continue
        rr = q['refutations'] if isinstance(q['refutations'], list) else []
        if len(rr) == 1:
            san = (rr[0]['san'] if isinstance(rr[0], dict) else str(rr[0])).rstrip('+#!')
            if san in answered:
                refs.add(san)
    return refs


def bristol_terms(ph, phases):
    """BRISTOL=1 (daily No. 11): (score, summary, ok). The threat must follow the key along its line (analysis.bristol);
    the key piece's other moves are tries whose single refutation the key answers with a mate (E. Bourd's
    prototype: 1.Bd8? Bd6!, 1.Bb6? d6!, 1.Bh2! Bd6 2.Qg8#, d6 2.Qxb4#)."""
    from chesscomp.analysis import bristol
    fm = ph['first_move']['uci']
    thr = ph.get('threat') or []
    follow = bool(thr) and all(bristol(fm, c['uci']) for c in thr)
    refs = thematic_tries(ph, phases)
    t = (25 if follow else -30) + 12 * min(len(refs), 3)
    return t, f"bristol={'yes' if follow else 'no'} thematic-tries={'/'.join(sorted(refs)) or '-'}", follow


def dyn_defs(ph, setmap=None):
    """Type-1 mode: each DEFSQ unit's defending move in phase ph: one whose set mate exists and changes first (not
    a by-play like 1...Rd5 2.Qxd5#), then fewest mates; '-sq' when the unit has no defending move."""
    setmap = setmap or {}
    def changed(v):
        sv = setmap.get(v['defence']['san'].rstrip('+#'))
        return bool(sv and sv['continuations'] and v['continuations'][0]['san'] not in {c['san'] for c in sv['continuations']})
    out = []
    for sq in DEFSQ:
        mine = [v for v in ph['variations'] if v['defence']['uci'][:2] == sq and not v['threat_repeat']
                and v['continuations'] and not v.get('refutes')]
        mine.sort(key=lambda v: (not changed(v), len(v['continuations'])))
        out.append(mine[0]['defence']['san'].rstrip('+#') if mine else f'-{sq}')
    return out


def score(b):
    """(score, summary, hit)"""
    global DEFS
    p = Problem.from_fen(b.fen(), '#2')
    try:
        r = analyse(p, max_refutations=4, include_tries=True, include_set=True, time_limit=8)
    except Exception as e:
        return -1e9, 'error', False
    keys = r.get('keys') or []
    phases = r.get('phases') or []
    s = 0.0
    if WCORR:
        t, summ, ok = wcorr_score(b, r, WCORR, NCORR)
        n = b.copy(); n.push(chess.Move.null())
        nfl = sum(1 for m in n.legal_moves if n.piece_type_at(m.from_square) == chess.KING)
        t -= 15 * nfl + 1.5 * max(0, units(b) - 10)
        if KEYROLE and keys:
            km = next((chess.Move.from_uci(ph['first_move']['uci']) for ph in phases if ph['type'] == 'key'), None)
            if km and (out_of_play_key(b, km) or idle_key_piece(b, km, phases)):
                t -= 25; ok = False
        return t, f'keys={keys} {summ}', ok and not (NOFLIGHT and nfl)
    if KEY:
        t, summ, ok = key_mode(r)
        n = b.copy(); n.push(chess.Move.null())
        nfl = sum(1 for m in n.legal_moves if n.piece_type_at(m.from_square) == chess.KING)
        t -= 15 * nfl + 1.5 * max(0, units(b) - 10)
        return t, f'keys={keys} {summ}', ok and not (NOFLIGHT and nfl)
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
    if DEFSQ:
        tk = [ph for ph in phases if ph['type'] in ('key', 'try') and ph['first_move']['uci'] == TKEY]
        DEFS = dyn_defs(tk[0], setmap) if tk else [f'-{sq}' for sq in DEFSQ]
        if tk:
            cands = tk
            if tk[0]['type'] == 'try':
                refs = tk[0]['refutations']
                s -= 30 + 10 * (len(refs) if isinstance(refs, list) else refs)
        else:
            s -= 60
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
                    t -= 5 * (len(sm) - 1)                # a dual in the thematic set play
                    if QMATE:
                        t += 6 * (v['continuations'][0]['san'][0] == 'Q') + 6 * all(m[0] == 'Q' for m in sm) - 4 * (len(sm) - 1)
        if UNIQUE:                                   # other moves of a DEF's unit must let the threat mate
            t -= 12 * sum(len(x) for x in extra_defences(ph, DEFS).values())
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
        if not DEFS:
            s += 25 * min(NPAT + 1, len(pattern_mates(r, got)))
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
            ok = all(d in got for d in DEFS) and (bool(DEFS) or len(pattern_mates(r, got)) >= NPAT)
        if ok and RECIP and len(DEFS) == 2:
            s0, s1 = setmap.get(DEFS[0]), setmap.get(DEFS[1])
            k0, k1 = vm[DEFS[0]]['continuations'][0]['san'], vm[DEFS[1]]['continuations'][0]['san']
            ok = bool(s0 and s1 and [c['san'] for c in s0['continuations']] == [k1] and [c['san'] for c in s1['continuations']] == [k0])
        if ok and CHANGED:
            ok = all(d in setmap and setmap[d]['continuations'] and vm[d]['continuations'][0]['san'] not in {c['san'] for c in setmap[d]['continuations']} for d in DEFS)
            ok = ok and not set_duals(setmap, DEFS)
        if ok and DEFSQ:
            ok = ph['type'] == 'key' and ph['first_move']['uci'] == TKEY
        if ok and QMATE:
            ok = all(vm[d]['continuations'][0]['san'][0] == 'Q' and len(setmap[d]['continuations']) == 1
                     and setmap[d]['continuations'][0]['san'][0] == 'Q' for d in DEFS)
        if ok and TARGET:
            ok = all(vm[d]['continuations'][0]['san'] == TARGET[d] for d in TARGET if d in vm)
        ok = ok and corr_score(ph)[2] and sb_score(b, ph)[2] and not (NOFLIGHT and kmoves)
        ok = ok and not (UNIQUE and any(extra_defences(ph, DEFS).values()))
        if ok and KEYROLE:
            km = chess.Move.from_uci(ph['first_move']['uci'])
            ok = not out_of_play_key(b, km) and (b.piece_type_at(km.from_square) == chess.KING or not idle_key_piece(b, km, phases))
        hit = ok
    if CORR and CTRY:
        ct, csum = corr_tries(phases)
        s += 12 * min(ct, CTRY + 1)
        best_sum += csum
        hit = hit and ct >= CTRY
    return s, f"keys={keys} {best_sum}", hit


def corr_tries(phases):
    """(count, summary) of quiet tries refuted only by a move of the CORR piece that the key answers with a mate, one per
    distinct refutation: the gate's second phase for a correction (daily No. 17: a single phase fails the gate)."""
    key = next((ph for ph in phases if ph['type'] == 'key'), None)
    if not key:
        return 0, ''
    answered = {v['defence']['uci'] for v in key['variations'] if v['continuations'] and not v['threat_repeat']}
    got = {}
    for ph in phases:
        refs = ph.get('refutations')
        if (ph['type'] != 'try' or ph.get('check_key') or ph['first_move']['san'].endswith('+')
                or not isinstance(refs, list) or len(refs) != 1):
            continue
        u = refs[0]['uci']
        if u[:2] == CORR and u in answered:
            got.setdefault(u, f" try {ph['first_move']['san']}? {refs[0]['san']}!")
    return len(got), ''.join(got.values())

def pattern_mates(r, got):
    """Distinct single mates of the key-phase defences that carry PATTERN (PATTERN with no DEFS)."""
    ph = [p for p in r.get('phases', []) if p['type'] == 'key']
    if not ph:
        return set()
    return {v['continuations'][0]['san'] for v in ph[0]['variations']
            if v['defence']['san'] in got and len(v['continuations']) == 1 and not v['threat_repeat']}

def mutate_cands(b):
    """CANDS mode: add, remove or swap units from the candidate list only."""
    b = b.copy()
    placed = [(sq, pc) for sq, pc in CANDS if b.piece_at(sq) == pc]
    free = [(sq, pc) for sq, pc in CANDS if not b.piece_at(sq)]
    op = random.random()
    if (op < 0.4 or not placed) and free:
        sq, pc = random.choice(free); b.set_piece_at(sq, pc)
    elif op < 0.7 and placed:
        sq, pc = random.choice(placed); b.remove_piece_at(sq)
    elif placed and free:
        sq, pc = random.choice(placed)
        same = [(s2, p2) for s2, p2 in free if p2.color == pc.color]
        if same:
            b.remove_piece_at(sq); s2, p2 = random.choice(same); b.set_piece_at(s2, p2)
    for sq, pc in CORE_SQ.items():
        b.set_piece_at(sq, pc)
    return b


def mutate(b):
    if CANDS:
        return mutate_cands(b)
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
    if not legal(seed):                    # daily logs 11-14 Oct: seeds with a checking unit died in 0 s, silently
        why = 'black king in check' if (lambda n: (n.push(chess.Move.null()), n.is_check())[1])(seed.copy()) else \
              'white in check' if seed.is_check() else 'mate in one, promoted force or invalid position'
        with open(OUT, 'a') as f:
            f.write(f'SEED illegal ({why}): {SEED}\n')
        print(f'SEED illegal ({why}): {SEED}', file=sys.stderr)
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
