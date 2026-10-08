"""Find a key for a finished post-key position, the way E. Bourd works (8 Oct 2026): "threat -> defences ->
arrange mates -> find a key; most of the part is just finding the key. The solution doesn't have to match 100%,
I need to move stuff around and maybe patch and add pieces. I am looking for decent keys."

    python3 -m chesscomp.compose.keyfind POSTKEY [--patch] [--jobs 4] [--top 15]

POSTKEY is the position after the key, Black to move. Its play (the threat and every Black move that stops
it, with its mates) is the specification. Every White unit is taken back one legal move (no captures, no
promotions); each diagram is solved, and the sound ones (that move the only key, no diagram flight, no
unprovided check in the set play) are ranked by the quality of the key: a sacrifice, a flight given, a
change from the set play and a key piece with a role in the diagram rank high; a check, a capture, a flight
taken, an out-of-play or idle key piece rank low or are dropped.

--patch also tries, for every retraction whose key works but is cooked (or refuted), ONE added unit of either
colour on every empty square, and keeps the additions after which the key is unique and the post-key play of
the thematic defences is unchanged. A patch is a proposal: it is the composer who decides whether the unit
earns its place.
"""
from __future__ import annotations
import sys, os, argparse
from concurrent.futures import ProcessPoolExecutor
import chess
from ..core import Problem
from ..analysis import analyse
from ..critique import out_of_play_key, idle_key_piece


def mates_after(board: chess.Board) -> list[str]:
    out = []
    for m in list(board.legal_moves):
        san = board.san(m)
        board.push(m)
        if board.is_checkmate():
            out.append(san)
        board.pop()
    return out


def move_id(board: chess.Board, m: chess.Move) -> str:
    return f"{board.piece_at(m.from_square).symbol().upper()}{chess.square_name(m.from_square)}{chess.square_name(m.to_square)}"


def post_spec(post_fen: str):
    """(threat ids, {defence uci: frozenset of mate ids}) of the post-key position, Black to move."""
    w = chess.Board(post_fen + ' w - - 0 1')
    threat = set()
    for m in list(w.legal_moves):
        w.push(m)
        if w.is_checkmate():
            w.pop(); threat.add(move_id(w, m)); continue
        w.pop()
    b = chess.Board(post_fen + ' b - - 0 1')
    defences = {}
    for d in list(b.legal_moves):
        b.push(d)
        mates = set()
        for m in list(b.legal_moves):
            b.push(m)
            if b.is_checkmate():
                b.pop(); mates.add(move_id(b, m)); continue
            b.pop()
        b.pop()
        if not (mates & threat):                       # it stops the threat: a defence
            defences[d.uci()] = frozenset(mates)
    return threat, defences


def retractions(post: chess.Board):
    """(pre-board, key move) for every legal one-move retraction of a white unit (no capture, no promotion)."""
    for sq, pc in post.piece_map().items():
        if pc.color != chess.WHITE:
            continue
        for frm in chess.SQUARES:
            if post.piece_at(frm) or frm == sq:
                continue
            if pc.piece_type == chess.PAWN and chess.square_rank(frm) in (0, 7):
                continue
            pre = post.copy()
            pre.remove_piece_at(sq); pre.set_piece_at(frm, pc)
            pre.turn = chess.WHITE
            key = chess.Move(frm, sq)
            if not pre.is_valid() or key not in pre.legal_moves:
                continue
            yield pre, key


def diagram_ok(pre: chess.Board) -> bool:
    n = pre.copy(); n.push(chess.Move.null())
    if not n.is_valid():
        return False
    return not any(m.from_square == n.king(chess.BLACK) for m in n.legal_moves)   # no diagram flight


def judge(pre: chess.Board, key: chess.Move, res: dict):
    """(score, notes) of a sound diagram whose only key is `key`."""
    notes, s = [], 0
    if pre.gives_check(key):
        return None
    if pre.is_capture(key):
        s -= 6; notes.append('capture')
    if out_of_play_key(pre, key):
        return None                                    # fatal (E. Bourd, 7 Oct 2026)
    if pre.piece_type_at(key.from_square) != chess.KING and idle_key_piece(pre, key, res['phases']):
        s -= 5; notes.append('idle key piece')
    after = pre.copy(); after.push(key)
    if after.is_attacked_by(chess.BLACK, key.to_square):
        s += 6; notes.append('sacrifice')
    bk = pre.king(chess.BLACK)
    b0 = pre.copy(); b0.turn = chess.BLACK
    fl0 = {m.to_square for m in b0.legal_moves if m.from_square == bk}
    fl1 = {m.to_square for m in after.legal_moves if m.from_square == bk}
    if fl1 - fl0:
        s += 6; notes.append('gives flight ' + ','.join(chess.square_name(x) for x in fl1 - fl0))
    if fl0 - fl1:
        s -= 3; notes.append('takes flight')
    setv = {v['defence']['uci']: {c['uci'] for c in v['continuations']}
            for ph in res['phases'] if ph['type'] == 'set' for v in ph['variations'] if v['continuations']}
    keyph = next(ph for ph in res['phases'] if ph['type'] == 'key')
    changed = [v['defence']['san'] for v in keyph['variations']
               if not v['threat_repeat'] and v['continuations'] and v['defence']['uci'] in setv
               and setv[v['defence']['uci']] != {c['uci'] for c in v['continuations']}]
    added = [v['defence']['san'] for v in keyph['variations']
             if not v['threat_repeat'] and v['continuations'] and v['defence']['uci'] not in setv]
    if changed:
        s += 3 * len(changed); notes.append('changed: ' + ','.join(changed))
    if not changed and not added:
        s -= 2; notes.append('static (all set)')
    dist = chess.square_distance(key.from_square, key.to_square)
    if dist >= 4:
        s += 1; notes.append('long')
    return s, notes


def solve_one(args):
    fen, key_uci, spec = args
    pre = chess.Board(fen)
    key = chess.Move.from_uci(key_uci)
    if not diagram_ok(pre):
        return None
    if spec is not None:                               # patched: the thematic play must be unchanged
        after = pre.copy(); after.push(key)
        threat, defs = post_spec(after.board_fen())
        t0, d0 = spec
        if threat != t0 or any(defs.get(d) != m for d, m in d0.items()):
            return None
    try:
        res = analyse(Problem.from_fen(pre.fen(), '#2'), include_tries=False, include_set=True, time_limit=10)
    except Exception:
        return None
    keys = res.get('keys') or []
    san = pre.san(key)
    sp = next((ph for ph in res['phases'] if ph['type'] == 'set'), None)
    if sp and any(u.endswith('+') for u in sp.get('unprovided', [])):
        return ('bad', fen, san, keys)
    if keys != [san]:
        return ('cooked' if san in keys else 'fails', fen, san, keys)
    j = judge(pre, key, res)
    return ('ok', fen, san, j) if j else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('post'); ap.add_argument('--patch', action='store_true')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2); ap.add_argument('--top', type=int, default=15)
    a = ap.parse_args(argv)
    post = chess.Board(a.post.split()[0] + ' b - - 0 1')
    spec = post_spec(post.board_fen())
    print(f"post-key: threat {sorted(spec[0])}, {len(spec[1])} defences")
    # mates in two that the post-key position already has with White to move: any key that leaves them alone
    # is cooked by them, so they say which white force is too strong before a single retraction is tried
    try:
        own = analyse(Problem.from_fen(post.board_fen() + ' w - - 0 1', '#2'), include_tries=False, include_set=False,
                      time_limit=15).get('keys') or []
    except Exception:
        own = []
    if own:
        print(f"White to move in the post-key position also solves by: {', '.join(own)} (each cooks keys that leave it)")
        # a key piece must be needed by every one of them: without it (taken back) none may still solve
        print('white units the other solutions depend on (none left without it = a key-piece candidate):')
        for sq, pc in sorted(post.piece_map().items()):
            if pc.color != chess.WHITE or pc.piece_type == chess.KING:
                continue
            b = post.copy(); b.remove_piece_at(sq)
            try:
                left = analyse(Problem.from_fen(b.board_fen() + ' w - - 0 1', '#2'), include_tries=False,
                               include_set=False, time_limit=15).get('keys') or []
            except Exception:
                continue
            print(f"   without {pc.symbol()}{chess.square_name(sq)}: {len(left)} left" + (f" ({', '.join(left[:6])})" if left else '  <- candidate'))
    tasks = [(pre.fen(), key.uci(), None) for pre, key in retractions(post)]
    print(f"{len(tasks)} retractions")
    with ProcessPoolExecutor(a.jobs) as ex:
        results = [r for r in ex.map(solve_one, tasks, chunksize=4) if r]
    good = sorted([r for r in results if r[0] == 'ok'], key=lambda r: -r[3][0])
    print(f"\nSOUND ({len(good)}):")
    for _, fen, san, (s, notes) in good[:a.top]:
        print(f"  {s:+3d}  1.{san}!  {fen.split()[0]}  {'; '.join(notes)}")
    if not a.patch:
        near = [r for r in results if r[0] == 'cooked']
        print(f"\ncooked ({len(near)}), fewest extra keys first:")
        for _, fen, san, keys in sorted(near, key=lambda r: len(r[3]))[:a.top]:
            print(f"  1.{san}  {fen.split()[0]}  also {', '.join(k for k in keys if k != san)}")
        return
    near = [r for r in results if r[0] in ('cooked', 'fails')]
    ptasks = []
    for _, fen, san, keys in near:
        pre = chess.Board(fen); key = pre.parse_san(san)
        if len(keys) > 4:
            continue
        for sq in chess.SQUARES:
            if pre.piece_at(sq) or sq in (key.to_square,):
                continue
            for sym in 'pnbrqPNBR':
                if sym in 'pP' and chess.square_rank(sq) in (0, 7):
                    continue
                b = pre.copy(); b.set_piece_at(sq, chess.Piece.from_symbol(sym))
                if b.is_valid() and key in b.legal_moves:
                    ptasks.append((b.fen(), key.uci(), spec))
    print(f"\npatching {len(near)} near-misses: {len(ptasks)} one-unit additions")
    with ProcessPoolExecutor(a.jobs) as ex:
        pres = [r for r in ex.map(solve_one, ptasks, chunksize=8) if r and r[0] == 'ok']
    pres.sort(key=lambda r: -r[3][0])
    print(f"PATCHED SOUND ({len(pres)}):")
    for _, fen, san, (s, notes) in pres[:a.top * 2]:
        print(f"  {s:+3d}  1.{san}!  {fen.split()[0]}  {'; '.join(notes)}")


if __name__ == '__main__':
    main()
