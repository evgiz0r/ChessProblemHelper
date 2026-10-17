"""Try table: every White move (or those of the units on the named squares) with its threats, refutations and
the mates after each defence, in python-chess alone, in about a second. The hand tool for one change per solve.

    python -m chesscomp.compose.trytable FEN [SQUARE ...]

Daily No. 10 and No. 12 (16-17 Oct 2026) built their positions with a scratch version of this table: one line per
White move, KEY when no Black move refutes it. Its threat is a mate in one after a Black null move, so a check
or a stalemate shows as 'no threat'. It does not replace the solver: run chesscomp.report on what it finds.

    SET: Bg3:Rd2# Bd2:Rxd2# d5:-
    KEY Bh1     thr=Rd3# refs=-  Bg3:Rd2# Bf2:Rd3#/c3#
        Bg2     thr=Rd3# refs=Bg3
"""
from __future__ import annotations
import sys
import chess


def mates_in_one(b: chess.Board) -> list[chess.Move]:
    out = []
    for m in list(b.legal_moves):
        b.push(m)
        if b.is_checkmate():
            out.append(m)
        b.pop()
    return out


def set_play(b: chess.Board) -> dict[str, list[str]]:
    """Black to move in the diagram (a null move for White): each Black move -> White's mates in one."""
    out = {}
    if b.is_check():
        return out
    b.push(chess.Move.null())
    for d in list(b.legal_moves):
        san = b.san(d)
        b.push(d)
        out[san] = [b.san(x) for x in mates_in_one(b)]
        b.pop()
    b.pop()
    return out


def row(b: chess.Board, m: chess.Move) -> dict:
    """One White move: san, mate1 (it mates at once), check, threats, refutations, and the defences whose mates
    differ from the threats (defence san -> mates)."""
    san = b.san(m)
    b.push(m)
    if b.is_checkmate():
        b.pop()
        return {'san': san, 'mate1': True, 'check': True, 'threats': [], 'refutations': [], 'variations': {}}
    check = b.is_check()
    threats = []
    if not check:
        b.push(chess.Move.null())
        threats = [b.san(x) for x in mates_in_one(b)]
        b.pop()
    refs, var = [], {}
    for d in list(b.legal_moves):
        ds = b.san(d)
        b.push(d)
        ms = [b.san(x) for x in mates_in_one(b)]
        b.pop()
        if not ms:
            refs.append(ds)
        elif set(ms) != set(threats):
            var[ds] = ms
    stalemate = not any(True for _ in b.legal_moves) and not check
    b.pop()
    return {'san': san, 'mate1': False, 'check': check, 'threats': threats,
            'refutations': ['stalemate'] if stalemate else refs, 'variations': var}


def table(fen: str, squares: list[str] | None = None) -> tuple[dict, list[dict]]:
    b = chess.Board(fen if ' ' in fen else fen + ' w - - 0 1')
    sqs = {chess.parse_square(s) for s in squares or []}
    rows = [row(b, m) for m in list(b.legal_moves) if not sqs or m.from_square in sqs]
    return set_play(b), rows


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    sp, rows = table(argv[0], argv[1:])
    print('SET:', ' '.join(f"{k}:{'/'.join(v) or '-'}" for k, v in sp.items()) or '-')
    for r in rows:
        tag = 'KEY' if not r['mate1'] and not r['refutations'] else '   '
        if r['mate1']:
            tag = 'M1 '
        thr = '/'.join(r['threats']) or ('check' if r['check'] else '-')
        refs = ','.join(r['refutations'][:6]) + ('...' if len(r['refutations']) > 6 else '') or '-'
        var = ' '.join(f"{k}:{'/'.join(v)}" for k, v in r['variations'].items())
        print(f"{tag} {r['san']:7} thr={thr} refs={refs}  {var}".rstrip())


if __name__ == '__main__':
    main(sys.argv[1:])
