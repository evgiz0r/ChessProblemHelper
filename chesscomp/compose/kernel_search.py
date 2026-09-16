"""Kernel search: add one or two units around a hand-made kernel so that a chosen key stays the only key and
Black gets at least two real defences with different mates (no duals, legal force).

    KERNEL="Q7/KB6/6N1/8/8/8/7k/8" KEY_UCI=b7h1 KEY_SAN=Bh1 BUDGET_S=300 JOBS=4 python -m chesscomp.compose.kernel_search 1 1
    (args: number of Black units, number of White units; sessions 22-23)

The composer's part is the kernel (mechanism, box, reason for the key); this only does the last layer.
A cheap prefilter (legal, no promoted force, no mate in one, the key still forces mate) runs before the full
solve. Slices run in parallel and stop at the time budget; partial results are printed as they come.
Negative results are results: around the three underpromotion miniatures ~150k additions gave nothing."""
import sys, itertools, time, chess
from chesscomp.core import Problem
from chesscomp.analysis import analyse

import os
KERNEL = os.environ.get("KERNEL", "Q7/KB6/6N1/8/8/8/7k/8")
KEY = chess.Move.from_uci(os.environ.get("KEY_UCI", "b7h1"))
KEY_SAN = os.environ.get("KEY_SAN", "Bh1")
WHITE = [chess.ROOK, chess.BISHOP, chess.PAWN]
BLACK = [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN, chess.QUEEN]
base = chess.Board(KERNEL + " w - - 0 1")
empty = [s for s in chess.SQUARES if not base.piece_at(s)]

def mates1(b):
    out = []
    for m in b.legal_moves:
        b.push(m)
        if b.is_checkmate(): out.append(m)
        b.pop()
    return out

def promoted(b):
    """Obtrusive force: more than 2 knights/rooks, 2 bishops of one colour, or 2 queens on a side."""
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and (chess.square_file(bs[0]) + chess.square_rank(bs[0])) % 2 == (chess.square_file(bs[1]) + chess.square_rank(bs[1])) % 2):
            return True
    return False

def prefilter(b):
    if not b.is_valid(): return False
    if promoted(b): return False
    if b.is_check(): return False
    if mates1(b): return False                      # mate in 1 in the diagram
    if KEY not in b.legal_moves: return False
    b.push(KEY)
    ok = True
    if b.is_checkmate() or b.is_stalemate(): ok = False
    else:
        for m in list(b.legal_moves):
            b.push(m)
            ms = mates1(b)
            b.pop()
            if not ms: ok = False; break
    b.pop()
    return ok

def judge(b):
    r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=1, include_tries=False, include_set=False, time_limit=10)
    if r.get('keys') != [KEY_SAN]: return None
    ph = [p for p in r['phases'] if p['type'] == 'key'][0]
    real = [v for v in ph['variations'] if not v['threat_repeat'] and v['continuations']]
    if any(v['dual'] for v in real): return None
    mates = {v['continuations'][0]['san'] for v in real}
    return len(real), len(mates), [(v['defence']['san'], v['continuations'][0]['san']) for v in real]

BUDGET = float(os.environ.get('BUDGET_S', '300'))   # wall-clock cap per run, seconds
JOBS = int(os.environ.get('JOBS', '4'))

def _work(args):
    """One slice: a fixed White combination (or none) against every Black combination."""
    wc, n_black, bslots, deadline = args
    seen = 0; hits = []
    for bc in itertools.combinations(bslots, n_black):
        if time.time() > deadline: break
        sq = {s for _, s in wc} | {s for _, s in bc}
        if len(sq) < len(wc) + n_black: continue
        b = base.copy()
        for p, s in wc: b.set_piece_at(s, chess.Piece(p, chess.WHITE))
        for p, s in bc: b.set_piece_at(s, chess.Piece(p, chess.BLACK))
        seen += 1
        if not prefilter(b): continue
        j = judge(b)
        if j and j[0] >= 2 and j[1] >= 2:
            hits.append((j[1], j[0], b.board_fen(), j[2]))
    return seen, hits

def run(n_black, whites=(1,)):
    """Slices run in parallel (JOBS processes) and stop at BUDGET_S seconds; partial results are reported."""
    from multiprocessing import Pool
    print('kernel', KERNEL, 'black', n_black, 'white', whites, 'jobs', JOBS, 'budget', BUDGET, flush=True)
    t0 = time.time(); deadline = t0 + BUDGET
    wslots = [(p, s) for p in WHITE for s in empty if not (p == chess.PAWN and chess.square_rank(s) in (0, 7))]
    bslots = [(p, s) for p in BLACK for s in empty if not (p == chess.PAWN and chess.square_rank(s) in (0, 7))]
    tasks = []
    for nw in whites:
        for wc in (itertools.combinations(wslots, nw) if nw else [()]):
            if len({s for _, s in wc}) < nw: continue
            tasks.append((wc, n_black, bslots, deadline))
    seen = 0; hits = []
    with Pool(JOBS) as pool:
        for s, h in pool.imap_unordered(_work, tasks, chunksize=8):
            seen += s
            for x in h:
                hits.append(x); print(*x, flush=True)
    note = ' (time budget hit, partial)' if time.time() > deadline else ''
    print(f"done: {seen} positions, {len(hits)} hits, {time.time()-t0:.0f}s{note}", flush=True)
    return hits

if __name__ == '__main__':
    nb = int(sys.argv[1]); nw = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    run(nb, whites=(nw,))
