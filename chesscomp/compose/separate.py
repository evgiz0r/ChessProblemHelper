"""Dual separator: which single white moves split a dual, and which pairs of moves give changed mates.

You have a scheme where a black defence (or two) is answered by two mates at once. This lists, for every
white first move, the mates left after each of the defences you name, and then the pairs of white moves that
each leave exactly one mate per defence with all mates different between the two moves: a try/key pair
with changed mates.

    python3 -m chesscomp.compose.separate FEN DEF [DEF ...]      e.g.  ... 2B5/2p1N3/3k4/3N4/4K3/4Q3/8/8 c6 c5

Only the named defences are checked; holes after other black moves and refutations are left to the solver.
E. Bourd, session 29: "at first I just had two mates, then I somehow had to separate, that's the hard part."
"""
from __future__ import annotations
import sys
from itertools import combinations
import chess


def _s(san: str) -> str:
    return san.replace('N', 'S')


def mates_after(board: chess.Board) -> list[str]:
    out = []
    for m in board.legal_moves:
        san = board.san(m)
        board.push(m)
        if board.is_checkmate():
            out.append(_s(san).rstrip('#+') + '#')
        board.pop()
    return sorted(out)


def defence_move(board: chess.Board, d: str):
    try:
        return board.parse_san(d)
    except ValueError:
        return None


def table(fen: str, defs: list[str]):
    b = chess.Board(fen if ' ' in fen else fen + ' w - - 0 1')
    rows = []
    for m in b.legal_moves:
        san = b.san(m)
        b.push(m)
        if b.is_check():
            b.pop(); continue
        cell = {}
        for d in defs:
            dm = defence_move(b, d)
            if dm is None:
                cell[d] = None
                continue
            b.push(dm); cell[d] = mates_after(b); b.pop()
        b.pop()
        rows.append((_s(san), cell))
    return rows


def pairs(rows, defs):
    single = [(san, {d: c[d][0] for d in defs}) for san, c in rows
              if all(c.get(d) and len(c[d]) == 1 for d in defs)]
    out = []
    for (a, ma), (b, mb) in combinations(single, 2):
        if all(ma[d] != mb[d] for d in defs) and len(set(ma.values())) == len(defs) == len(set(mb.values())):
            out.append((a, b, ma, mb))
    return single, out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    fen, defs = argv[0], argv[1:]
    rows = table(fen, defs)
    print('white move'.ljust(10), '  '.join(d.ljust(22) for d in defs))
    for san, c in rows:
        if any(c.get(d) for d in defs):
            print(san.ljust(10), '  '.join(('/'.join(c[d]) if c[d] else ('-' if c[d] is not None else 'n/a')).ljust(22) for d in defs))
    single, prs = pairs(rows, defs)
    print(f'\n{len(single)} moves leave exactly one mate after every named defence.')
    print('Changed-mate pairs (each move one distinct mate per defence, all changed):')
    for a, b, ma, mb in prs:
        print(f'   1.{a} / 1.{b}:  ' + ',  '.join(f'{d} {ma[d]} -> {mb[d]}' for d in defs))
    if not prs:
        print('   none')


if __name__ == '__main__':
    main()
