"""Recursive trimming: remove units until nothing more can go, in every order.

E. Bourd (8 Oct 2026): "you could remove the h6 pawn as well, worth searching recursively sometimes as some
pieces are artifacts of others" (bRh5 went, and then bPh6, which only stopped the rook's checks, could go too).
A single pass of removals misses such pairs; this explores removal sets breadth-first and keeps every position
in which the key is still the only key, the play of the key phase is unchanged (every defence keeps exactly
its mates, no new defence without a mate), there is no diagram flight and no unprovided check in the set play.

    python3 -m chesscomp.compose.trim FEN [--keep e5,d7] [--max 4]
"""
from __future__ import annotations
import argparse
import chess
from ..core import Problem
from ..analysis import analyse


def key_play(fen: str):
    """(keys, {defence: frozenset(mates)} of the key phase, unprovided checks in the set) or None."""
    b = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid():
        return None
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid() or any(m.from_square == n.king(chess.BLACK) for m in n.legal_moves):
        return None
    try:
        r = analyse(Problem.from_fen(b.fen(), '#2'), include_tries=False, include_set=True, time_limit=10)
    except Exception:
        return None
    keys = r.get('keys') or []
    kp = next((p for p in r['phases'] if p['type'] == 'key'), None)
    sp = next((p for p in r['phases'] if p['type'] == 'set'), None)
    checks = [u for u in (sp or {}).get('unprovided', []) if u.endswith('+')]
    play = {v['defence']['san']: frozenset(c['san'] for c in v['continuations'])
            for v in (kp or {}).get('variations', []) if not v['threat_repeat']} if kp else {}
    if kp:                                         # the threat is part of the play: a removal that adds a second
        play['(threat)'] = frozenset(t['san'] for t in kp.get('threat') or [])   # threat is no trim (10 Oct 2026)
    return keys, play, checks


def trim(fen: str, keep=(), max_removed=6):
    base = key_play(fen)
    if not base or len(base[0]) != 1:
        raise SystemExit('the diagram is not sound: nothing to trim against')
    keys0, play0, _ = base
    board = chess.Board(fen + ' w - - 0 1')
    removable = [s for s in chess.SquareSet(board.occupied)
                 if board.piece_type_at(s) != chess.KING and chess.square_name(s) not in keep]
    seen, frontier, found = {frozenset()}, [frozenset()], []
    for depth in range(1, max_removed + 1):
        nxt = []
        for gone in frontier:
            for s in removable:
                if s in gone:
                    continue
                g = gone | {s}
                if g in seen:
                    continue
                seen.add(g)
                b = board.copy()
                for x in g:
                    b.remove_piece_at(x)
                kp = key_play(b.board_fen())
                if not kp or kp[0] != keys0 or kp[2]:
                    continue
                if any(kp[1].get(d) != m for d, m in play0.items() if m) or any(not m for m in kp[1].values()):
                    continue
                nxt.append(g); found.append((g, b.board_fen()))
        if not nxt:
            break
        frontier = nxt
    return keys0[0], board, found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('fen'); ap.add_argument('--keep', default=''); ap.add_argument('--max', type=int, default=6)
    a = ap.parse_args(argv)
    key, board, found = trim(a.fen.split()[0], [k for k in a.keep.split(',') if k], a.max)
    if not found:
        print(f'1.{key}: no unit (or set of units) can be removed with the same key and play'); return
    best = max(len(g) for g, _ in found)
    print(f'1.{key}: {len(found)} trimmed versions keep the key and the play; at most {best} units removable')
    for g, fen in sorted(found, key=lambda x: -len(x[0])):
        if len(g) < best and len(found) > 12:
            continue
        print('  -' + ' -'.join(board.piece_at(s).symbol() + chess.square_name(s) for s in sorted(g)) + '   ' + fen)


if __name__ == '__main__':
    main()
