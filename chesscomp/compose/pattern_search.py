"""Pattern search (session 28): add 1-2 White units (+ optionally 1 Black unit) to a hand-made kernel so
that a unique quiet non-capturing key exists and the solver reports PATTERN on defence DEF, with no dual
after DEF in the key phase. Default pattern: 'Dombrovskis (refutation)' (a try threatens A, DEF refutes
it, after the key DEF allows A).
    BASE="6K1/1N6/4p3/1P1k3p/8/8/4Q3/8" DEF=e5 BUDGET_S=1500 python -m chesscomp.compose.pattern_search JOB JOBS MODE
MODE: w1 | w2 | w1b1 | w2b1 (which units to add). Run JOBS copies with JOB=0..JOBS-1 in parallel.
The one-variation Dombrovskis 6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1 came out of this in seven minutes (w2 mode),
after five hand-made kernels had died to mates in one."""
import sys, os, itertools, time, chess
from chesscomp.core import Problem
from chesscomp.analysis import analyse
JOB, JOBS, MODE = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
BASE = os.environ.get('BASE', '6K1/1N6/4p3/1P1k3p/8/8/4Q3/8')
DEF = os.environ.get('DEF', 'e5')
PATTERN = os.environ.get('PATTERN', 'Dombrovskis (refutation)')
PURE = os.environ.get('PURE', '0') == '1'   # DEF must have no mate in the set play (the key creates it)
BUDGET = float(os.environ.get('BUDGET_S', '1500'))
base = chess.Board(BASE + ' w - - 0 1')
empty = [s for s in chess.SQUARES if not base.piece_at(s)]
W = [chess.Piece(t, chess.WHITE) for t in ((chess.QUEEN,) if os.environ.get('QUEEN') == '1' else ()) + (chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN)]
B = [chess.Piece(t, chess.BLACK) for t in (chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN)]
def okp(s, p):
    r = chess.square_rank(s)
    return not (p.piece_type == chess.PAWN and (r == 0 or r == 7))
def mates1(b):
    for m in b.legal_moves:
        b.push(m); mate = b.is_checkmate(); b.pop()
        if mate: return True
    return False
def promoted(b):
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2: return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and (chess.square_file(bs[0]) + chess.square_rank(bs[0])) % 2 == (chess.square_file(bs[1]) + chess.square_rank(bs[1])) % 2): return True
    return False
def pre(b):
    if not b.is_valid() or b.is_check() or promoted(b): return False
    b2 = b.copy(); b2.push(chess.Move.null())
    if b2.is_check(): return False
    if mates1(b): return False
    return True
def judge(b):
    r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=1, time_limit=8)
    keys = r.get('keys') or []
    if len(keys) != 1: return None
    ph = [p for p in r['phases'] if p['type'] == 'key'][0]
    if ph.get('check_key') or 'x' in keys[0]: return None
    pats = [p for p in (r.get('relations') or {}).get('patterns', []) if p['name'] == PATTERN and p.get('defence') == DEF]
    if not pats: return None
    v = [v for v in ph['variations'] if v['defence']['san'] == DEF]
    if not v or v[0]['dual'] or v[0].get('threat_repeat'): return None
    if PURE:
        for sp in r['phases']:
            if sp['type'] == 'set':
                for sv in sp['variations']:
                    if sv['defence']['san'] == DEF and sv['continuations']: return None
    return keys[0], [(p['defence'], p['phases']) for p in pats], v[0]['continuations'][0]['san']
def cands():
    wa = [(s, p) for s in empty for p in W if okp(s, p)]
    ba = [(s, p) for s in empty for p in B if okp(s, p)]
    if MODE == 'w1':
        for s, p in wa: yield [(s, p)]
    elif MODE == 'w2':
        for (s1, p1), (s2, p2) in itertools.combinations(wa, 2):
            if s1 != s2: yield [(s1, p1), (s2, p2)]
    elif MODE == 'w1b1':
        for (s1, p1) in wa:
            for (s2, p2) in ba:
                if s1 != s2: yield [(s1, p1), (s2, p2)]
    elif MODE == 'w2b1':
        for (s1, p1), (s2, p2) in itertools.combinations(wa, 2):
            if s1 == s2: continue
            for (s3, p3) in ba:
                if s3 not in (s1, s2): yield [(s1, p1), (s2, p2), (s3, p3)]
t0 = time.time(); n = 0; hits = 0
for i, adds in enumerate(cands()):
    if i % JOBS != JOB: continue
    if time.time() - t0 > BUDGET: print('budget'); break
    b = base.copy()
    for s, p in adds: b.set_piece_at(s, p)
    if not pre(b): continue
    n += 1
    res = judge(b)
    if res:
        hits += 1
        print(' '.join(p.symbol() + chess.square_name(s) for s, p in adds), '|', b.fen().split(' ')[0], '|', res, flush=True)
print('done', n, 'judged', hits, 'hits', round(time.time() - t0), 's')
