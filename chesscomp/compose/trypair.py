"""Try-pair completion: enumerate one or two added units around a kernel so that the key is the only key, every
named try has exactly its named refutation, and the post-key play is the wanted one (E. Bourd, 12 Oct 2026: "without
a pure pair, its almost not worth having 1 pair").

    SPEC='{"kernel": "<board FEN, diagram>", "key": "e4d2", "tries": {"e4f2": "c1c5", "e4f6": "a7c5"},
           "want": {"Bc5": "Nd8c6", "Rc5": "Bg1d4"}, "threat": "Rh4e4", "add": 2, "jobs": 4, "budget": 280}' \
        python3 -m chesscomp.compose.trypair

Cheap filters run first (legal, no promoted force, no diagram flight, no White mate in one, the key's post-key play
via keyfind.post_spec: the one threat, the wanted mates, no holes, no duals, no by-play repeating a wanted mate); only
survivors get the full solve (key uniqueness, try refutations). Prints every full hit, and the best near misses
(post-key exact, key or tries not yet) so a kernel can be repaired by hand.
SPEC "loose": true keeps only the wanted play (threat, wanted mates, key, tries): random-move duals, by-play repeating a
thematic mate and black checks are allowed (E. Bourd's bench schemes have them while still soft, 22 Oct 2026); holes are
never allowed (a hole refutes the key).
"""
from chesscomp.core import illegal_position as _illegal
import itertools, json, os, sys, time
from multiprocessing import Pool
import chess
from chesscomp.compose.keyfind import post_spec
from chesscomp.core import Problem
from chesscomp.analysis import analyse

SPEC = json.loads(os.environ.get('SPEC', '{}'))
UNITS = SPEC.get('units', 'NBRPnbrp')


def promoted(b):
    if _illegal(b):                                   # retro: pawn captures, promotions (17 Oct 2026)
        return True
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def cheap(fen):
    """None when a cheap filter fails, else (post-key board fen, info)."""
    w = chess.Board(fen + ' w - - 0 1')
    if not w.is_valid() or promoted(w):
        return None
    bl = chess.Board(fen + ' b - - 0 1')
    if not bl.is_valid() or any(m.from_square == bl.king(chess.BLACK) for m in bl.legal_moves):
        return None                                           # a diagram flight is fatal
    for m in list(w.legal_moves):
        w.push(m)
        mate = w.is_checkmate()
        w.pop()
        if mate:
            return None
    key = chess.Move.from_uci(SPEC['key'])
    if key not in w.legal_moves or w.gives_check(key) or w.is_capture(key):
        return None                                           # a checking or capturing key is fatal
    w.push(key)
    post = w.board_fen()
    t, d = post_spec(post)
    if t != {SPEC['threat']}:
        return None
    b = chess.Board(post + ' b - - 0 1')
    names = {b.san(chess.Move.from_uci(u)): m for u, m in d.items()}
    want = SPEC['want']
    if any(names.get(k) != {v} for k, v in want.items()):
        return None
    if any(not m for m in names.values()):
        return None                                           # holes
    if SPEC.get('loose'):
        return post, len(names)
    if any(not m or len(m) > 1 for m in names.values()):
        return None                                           # holes and duals
    if any(k not in want and m & set(want.values()) for k, m in names.items()):
        return None                                           # by-play repeating a thematic mate
    if any(b.gives_check(m) for m in b.legal_moves):
        return None                                           # a black check after the key
    return post, len(names)


def full(fen):
    w = chess.Board(fen + ' w - - 0 1')
    key = chess.Move.from_uci(SPEC['key'])
    key_san = w.san(key).replace('N', 'S').rstrip('+#')
    try:
        r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_set=False, max_refutations=3, time_limit=10)
    except Exception:
        return False, 'error'
    keys = r.get('keys') or []
    got = {p['first_move']['uci']: [x['uci'] for x in p['refutations']] for p in r['phases'] if p['type'] == 'try'}
    ok = keys == [key_san] and all(got.get(t) == [ref] for t, ref in SPEC['tries'].items())
    return ok, f"keys={keys} tries={ {t: got.get(t) for t in SPEC['tries']} }"


def additions(base):
    empty = [s for s in chess.SQUARES if not base.piece_at(s)]
    singles = []
    for s in empty:
        for u in UNITS:
            if u in 'Pp' and chess.square_rank(s) in (0, 7):
                continue
            singles.append((s, u))
    return singles


def place(base_fen, items):
    b = chess.BaseBoard(base_fen)
    for s, u in items:
        if b.piece_at(s):
            return None
        b.set_piece_at(s, chess.Piece.from_symbol(u))
    return b.board_fen()


def work(items):
    fen = place(SPEC['kernel'], items)
    if fen is None:
        return None
    c = cheap(fen)
    if c is None:
        return None
    ok, info = full(fen)
    return fen, ok, info, items


def main():
    t0 = time.time()
    base = chess.BaseBoard(SPEC['kernel'])
    singles = additions(base)
    jobs = [(x,) for x in singles]
    if SPEC.get('add', 1) >= 2:
        jobs += [(a, b) for a, b in itertools.combinations(singles, 2) if a[0] != b[0]]
    budget = SPEC.get('budget', 280)
    print(f"{len(jobs)} placements", flush=True)
    hits = near = 0
    with Pool(SPEC.get('jobs', 4)) as pool:
        for r in pool.imap_unordered(work, jobs, chunksize=64):
            if time.time() - t0 > budget:
                pool.terminate()
                print('budget reached', flush=True)
                break
            if r is None:
                continue
            fen, ok, info, items = r
            add = ' '.join(u + chess.square_name(s) for s, u in items)
            if ok:
                hits += 1
                print(f"HIT {fen} +{add} {info}", flush=True)
            elif near < 40:
                near += 1
                print(f"near {fen} +{add} {info}", flush=True)
    print(f"done hits={hits} near={near} {time.time() - t0:.0f}s", flush=True)


if __name__ == '__main__':
    main()
