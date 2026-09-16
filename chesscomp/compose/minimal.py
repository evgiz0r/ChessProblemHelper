"""Minimal-form search: every placement of a tiny set of units, keeping the positions whose only key is the
move asked for (E. Bourd s24: 7K/3P1k2/3Q4/8/8/8/8/8, four units, 1.d8=B!). The composer shrinks a mechanism to
its essence by hand in a few solves; this checks whether anything smaller or different exists.

    python -m chesscomp.compose.minimal --key-promo b --extra Q,R,B,N --jobs 4
"""
import argparse, itertools, sys, time, chess
from multiprocessing import Pool
from .kernel_search import mates1
from ..core import Problem
from ..analysis import analyse

PROMO = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}

def forces_mate(b):
    """Black to move: every reply mated at once (a #2 second move)."""
    if b.is_checkmate(): return True
    if b.is_stalemate(): return False
    for r in list(b.legal_moves):
        b.push(r); ms = mates1(b); b.pop()
        if not ms: return False
    return True

def check_one(args):
    """One pawn square + extra unit type: enumerate the extra unit's square and both kings."""
    pawn_sq, extra_type, promo = args
    out = []; seen = 0
    for xs in chess.SQUARES:
        if xs == pawn_sq: continue
        for wk in chess.SQUARES:
            if wk in (pawn_sq, xs): continue
            for bk in chess.SQUARES:
                if bk in (pawn_sq, xs, wk) or chess.square_distance(wk, bk) < 2: continue
                b = chess.Board(None)
                b.set_piece_at(pawn_sq, chess.Piece(chess.PAWN, chess.WHITE))
                b.set_piece_at(xs, chess.Piece(extra_type, chess.WHITE))
                b.set_piece_at(wk, chess.Piece(chess.KING, chess.WHITE))
                b.set_piece_at(bk, chess.Piece(chess.KING, chess.BLACK))
                b.turn = chess.WHITE
                if not b.is_valid() or b.is_check(): continue
                seen += 1
                if mates1(b): continue
                key = chess.Move(pawn_sq, pawn_sq + 8, promotion=promo)
                if key not in b.legal_moves: continue
                b.push(key); ok = not b.is_check() and forces_mate(b); b.pop()
                if not ok: continue
                r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=1, include_tries=False, include_set=False, time_limit=5)
                if len(r.get('keys', [])) != 1: continue
                ph = [p for p in r['phases'] if p['type'] == 'key'][0]
                real = [v for v in ph['variations'] if not v['threat_repeat'] and v['continuations']]
                out.append((b.board_fen(), r['keys'][0], [(v['defence']['san'], '/'.join(c['san'] for c in v['continuations'])) for v in real]))
    return seen, out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--key-promo', default='b', choices='qrbn')
    ap.add_argument('--extra', default='Q,R,B,N', help='types of the one extra White unit')
    ap.add_argument('--files', default='abcd', help='pawn files (mirror symmetry: a-d covers all)')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    types = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'N': chess.KNIGHT}
    tasks = [(chess.square(ord(f) - 97, 6), types[t], PROMO[a.key_promo]) for f in a.files for t in a.extra.split(',')]
    t0 = time.time(); seen = 0; hits = []
    with Pool(a.jobs) as pool:
        for s, h in pool.imap_unordered(check_one, tasks):
            seen += s; hits += h
            for x in h: print(*x, flush=True)
    print(f'done: {seen} legal positions, {len(hits)} with a unique {a.key_promo.upper()}-promotion key, {time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
