"""Diagram search scored by the solver and the critique (11 Oct 2026): the thematic core never moves; every other unit
(either colour, kings too) is added, removed or moved. Score: one key; the named defences (solver SAN, S for knights)
each answered by one mate, all different; extra defences cost a little (E. Bourd: "not clean"); then the critique on
sound candidates, each major (fatal) finding costing heavily. Diagrams with White in check are rejected.
    python3 -m chesscomp.compose.diagsearch CORE SEED DEFS BUDGET_S RNG      e.g. DEFS=S3c5,S7c5
Lesson of its first runs: without the pinner in CORE it drops the theme; it finds unique keys mostly where the diagram
has a flight (fatal), so read the major list, not the score.
"""
from chesscomp.core import illegal_position as _illegal
import sys, random, time, chess

from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique

CORE, SEED, DEFS = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
BUDGET = float(sys.argv[4]); random.seed(int(sys.argv[5]))
core = chess.Board(CORE + ' w - - 0 1'); CSQ = {s: core.piece_at(s) for s in chess.SQUARES if core.piece_at(s)}


def promoted(b):
    if _illegal(b):                                   # retro: pawn captures, promotions (17 Oct 2026)
        return True
    for col in (chess.WHITE, chess.BLACK):
        w = lambda t: len(b.pieces(t, col))
        if w(chess.QUEEN) > 1 or w(chess.ROOK) > 2 or w(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def play_score(ph):
    s = 15 if ph.get('threat') else 0
    v = {x['defence']['san']: [c['san'] for c in x['continuations']] for x in ph['variations'] if not x.get('threat_repeat')}
    mates = []
    for d in DEFS:
        m = v.get(d)
        if m is None:
            s -= 15
        elif len(m) == 1:
            s += 15; mates.append(m[0])
        else:
            s -= 8
    if len(mates) == len(DEFS) and len(set(mates)) == len(mates):
        s += 15
    s -= 4 * len([k for k in v if k not in DEFS])
    return s, v


def score(fen):
    b = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid() or promoted(b) or b.is_check():
        return -1e9, ''
    s = -0.7 * len(b.piece_map())
    try:
        r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), max_refutations=1, time_limit=6)
    except Exception:
        return -1e9, ''
    keys = r.get('keys') or []
    if not keys:
        return s - 60, 'no key'
    kph = [p for p in r['phases'] if p['type'] == 'key']
    best = max((play_score(p)[0] for p in kph), default=-30)
    s += best - 10 * (len(keys) - 1)
    info = f"keys={keys}"
    if len(keys) == 1 and best >= 60:
        try:
            F = critique(Problem.from_fen(fen + ' w - - 0 1', '#2'), r, necessity=False)['findings']
        except Exception:
            return s, info + ' critique-error'
        majors = [f['rule'] for f in F if f['severity'] == 'major']
        minors = [f['rule'] for f in F if f['severity'] == 'minor']
        pluses = [f['rule'] for f in F if f['severity'] == 'plus']
        s += 40 - 40 * len(majors) - 3 * len(minors) + 4 * len(pluses)
        if not majors:
            s += 60
        info += f" major={majors} minor={minors} plus={pluses} play={play_score(kph[0])[1]}"
    return s, info


def mutate(fen):
    b = chess.Board(fen + ' w - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in CSQ and b.piece_type_at(s) != chess.KING]
    kings = [s for s in chess.SquareSet(b.occupied) if s not in CSQ and b.piece_type_at(s) == chess.KING]
    empty = [s for s in chess.SQUARES if not b.piece_at(s)]
    op = random.random()
    if op < .35:
        sym = random.choice('NBRPPPpppnbrQq'); sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
            return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .5 and free:
        b.remove_piece_at(random.choice(free))
    elif op < .9 and free:
        s = random.choice(free); p = b.piece_at(s); b.remove_piece_at(s); b.set_piece_at(random.choice(empty), p)
    elif kings:
        s = random.choice(kings); p = b.piece_at(s); b.remove_piece_at(s); b.set_piece_at(random.choice(empty), p)
    return b.board_fen()


t0 = time.time(); pop = [(score(SEED)[0], SEED)]; seen = {SEED}; best = pop[0]
while time.time() - t0 < BUDGET:
    pop.sort(key=lambda x: -x[0]); pop = pop[:14]
    ch = random.choice(pop[:6])[1]
    for _ in range(random.choice((1, 1, 2, 3))):
        ch = mutate(ch)
    if ch in seen:
        continue
    seen.add(ch); sc, info = score(ch); pop.append((sc, ch))
    if sc > best[0]:
        best = (sc, ch); print('BEST', round(sc, 1), ch, info, flush=True)
pop.sort(key=lambda x: -x[0])
for sc, f in pop[:3]:
    print('TOP', round(sc, 1), f, score(f)[1])
print('evaluated', len(seen))
