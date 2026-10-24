"""Recursive trimming: remove units until nothing more can go, in every order.

E. Bourd (8 Oct 2026): "you could remove the h6 pawn as well, worth searching recursively sometimes as some
pieces are artifacts of others" (bRh5 went, and then bPh6, which only stopped the rook's checks, could go too).
A single pass of removals misses such pairs; this explores removal sets breadth-first and keeps every position
in which the key is still the only key, the play of the key phase is unchanged (every defence keeps exactly
its mates, no new defence at all), there is no diagram flight and no unprovided check in the set play.

    python3 -m chesscomp.compose.trim FEN [--keep e5,d7] [--max 4] [--tries]
--tries also keeps every try with its refutations: without it trim removed his wPh2, the unit that gave the random
bishop move its one refutation in a white correction (E. Bourd, 18 Oct 2026). Use it whenever the tries are content.
--allow-flight keeps the diagram's own flights (no new one): for a scheme that pays a flight for its content, like
his masked pin 1.Bf2! where e4 is the only answer to the free knight's checks (E. Bourd, 24 Oct 2026).
"""
from __future__ import annotations
import argparse
import chess
from ..core import Problem
from ..analysis import analyse


def diagram_flights(fen: str) -> set:
    """Squares the Black king can move to in the diagram (Black to move)."""
    n = chess.Board(fen + ' w - - 0 1'); n.push(chess.Move.null())
    return {m.to_square for m in n.legal_moves if m.from_square == n.king(chess.BLACK)}


def key_play(fen: str, flights: set | None = None):
    """(keys, {defence: frozenset(mates)} of the key phase, unprovided checks in the set) or None.
    flights: the diagram flights allowed to stay (None: no flight at all)."""
    b = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid():
        return None
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid() or not diagram_flights(fen) <= (flights or set()):
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


def try_map(fen: str):
    """{try san: frozenset of refutation san} of the diagram."""
    try:
        r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_tries=True, include_set=False, time_limit=20)
    except Exception:
        return None
    return {p['first_move']['san']: frozenset(x['san'] for x in p.get('refutations', []))
            for p in r['phases'] if p['type'] == 'try'}


def trim(fen: str, keep=(), max_removed=6, keep_tries=False, allow_flight=False):
    tries0 = try_map(fen) if keep_tries else None
    flights = diagram_flights(fen) if allow_flight else None
    base = key_play(fen, flights)
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
                kp = key_play(b.board_fen(), flights)
                if not kp or kp[0] != keys0 or kp[2]:
                    continue
                if any(kp[1].get(d) != m for d, m in play0.items() if m) or \
                        any(not m for d, m in kp[1].items() if d != '(threat)'):   # a zugzwang key has no threat
                    continue
                if set(kp[1]) - set(play0):   # a new defence changes the play: -bPc2 let 1...Sc2 join 1...Sc6
                    continue                  # (bourd-type3-c5-threat, 16 Oct 2026)
                if tries0 is not None:        # --tries: every try keeps its refutations (E. Bourd, 18 Oct 2026: wPh2
                    tm = try_map(b.board_fen())   # gave B~ its one refutation Qg2+, and trim removed it)
                    if tm is None or any(tm.get(t) != r for t, r in tries0.items()):
                        continue
                nxt.append(g); found.append((g, b.board_fen()))
        if not nxt:
            break
        frontier = nxt
    return keys0[0], board, found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('fen'); ap.add_argument('--keep', default=''); ap.add_argument('--max', type=int, default=6)
    ap.add_argument('--tries', action='store_true', help='also keep every try with its refutations')
    ap.add_argument('--allow-flight', action='store_true', help="keep the diagram's own flights (no new one)")
    a = ap.parse_args(argv)
    key, board, found = trim(a.fen.split()[0], [k for k in a.keep.split(',') if k], a.max, a.tries, a.allow_flight)
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
