"""Re-place a cook-stopper: remove units that only keep a sound position sound, and try every single unit (either
colour, every empty square) in their place. Kept: the key is still the only one, the named defences keep their
mates, no diagram flight, no unprovided check in the set play. Printed with the variations the new unit adds.

    python3 -m chesscomp.compose.restop FEN KEY "Bf6=Sb4#,Bg6=Qb3#" a8[,g5] [--jobs 4]
    python3 -m chesscomp.compose.restop FEN KEY "Bf6=Sb4#,Bg6=Qb3#" -        # add one unit, remove nothing

E. Bourd's 1.Qb5! (11 Oct 2026, nK6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8): the black knight a8 only stopped the second
threat Sc7#. Of 470 single replacements the only one that works besides it is the knight on e8: it still guards c7,
and 1...Sf6 cuts the same line as the bishops, 2.Sc7#. A corner unit with one job became a third thematic defence.
"""
from __future__ import annotations
import sys, argparse, time
from concurrent.futures import ProcessPoolExecutor
import chess

from ..core import Problem
from ..analysis import analyse
from .keyfind import diagram_ok

PIECES = (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)


def promoted(b: chess.Board) -> bool:
    for col in (chess.WHITE, chess.BLACK):
        n = lambda t: len(b.pieces(t, col))
        if n(chess.QUEEN) > 1 or n(chess.ROOK) > 2 or n(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def check(args):
    """(fen, {defence: set mate or '-'}, {other defence: mates}) if the diagram keeps the key and the wanted play."""
    fen, key, want = args
    b = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid() or promoted(b) or not diagram_ok(b):
        return None
    try:
        r = analyse(Problem.from_fen(b.fen(), '#2'), include_set=True, include_tries=False, time_limit=10)
    except Exception:
        return None
    if r.get('keys') != [key]:
        return None
    sp = next((ph for ph in r['phases'] if ph['type'] == 'set'), None)
    if sp and any(u.endswith('+') for u in sp.get('unprovided', [])):
        return None
    kp = next(ph for ph in r['phases'] if ph['type'] == 'key')
    got = {v['defence']['san']: '/'.join(c['san'] for c in v['continuations'])
           for v in kp['variations'] if not v.get('threat_repeat')}
    if any(got.get(d) != m for d, m in want.items()):
        return None
    setm = {v['defence']['san']: '/'.join(c['san'] for c in v['continuations'])
            for v in (sp['variations'] if sp else []) if v['continuations']}
    return fen, {d: setm.get(d, '-') for d in want}, {d: m for d, m in got.items() if d not in want}


def candidates(fen: str, remove: list[int]):
    base = chess.Board(fen + ' w - - 0 1')
    for s in remove:
        base.remove_piece_at(s)
    for sq in chess.SQUARES:
        if base.piece_at(sq):
            continue
        for col in (chess.WHITE, chess.BLACK):
            for pt in PIECES:
                if pt == chess.PAWN and chess.square_rank(sq) in (0, 7):
                    continue
                b = base.copy(); b.set_piece_at(sq, chess.Piece(pt, col))
                yield b.board_fen()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('fen'); ap.add_argument('key'); ap.add_argument('want'); ap.add_argument('remove')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args(argv)
    want = dict(x.split('=') for x in a.want.split(','))
    remove = [] if a.remove == '-' else [chess.parse_square(s) for s in a.remove.split(',')]
    cands = list(candidates(a.fen.split()[0], remove))
    t0, hits = time.time(), []
    with ProcessPoolExecutor(a.jobs) as ex:
        for res in ex.map(check, [(c, a.key, want) for c in cands], chunksize=8):
            if res:
                hits.append(res)
    hits.sort(key=lambda h: -len(h[2]))                  # units that add play first
    for fen, setm, extra in hits:
        print(fen, '| set:', ', '.join(f'{d} {m}' for d, m in setm.items()),
              '| adds:', ', '.join(f'{d} {m}' for d, m in extra.items()) or '-')
    print(f'{len(cands)} candidates, {len(hits)} kept, {time.time() - t0:.0f}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
