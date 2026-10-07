"""Retract the key: from a finished post-key position, find the diagrams one white move earlier.

E. Bourd's way of working (session 29): build the position after the key first, then take the key back.
Give the post-key position (Black to move); every white non-capturing, non-promoting move is undone in
every legal way and each resulting diagram is solved as #2. Sound diagrams with that move as the only key
are listed with their tries and set play, so you can judge which key the position wants.

    python3 -m chesscomp.compose.retract "8/2N1R3/8/8/3k1n2/8/7B/1RQ1N2K"
"""
from __future__ import annotations
import sys
import chess
from ..core import Problem
from ..analysis import analyse
from ..report import format_compact


def retractions(post: chess.Board):
    for sq, piece in post.piece_map().items():
        if piece.color != chess.WHITE:
            continue
        for frm in chess.SQUARES:
            if post.piece_at(frm):
                continue
            pre = post.copy()
            pre.remove_piece_at(sq)
            pre.set_piece_at(frm, piece)
            pre.turn = chess.WHITE
            if piece.piece_type == chess.PAWN and chess.square_rank(frm) in (0, 7):
                continue
            mv = chess.Move(frm, sq)
            if not pre.is_valid() or pre.is_check() or mv not in pre.legal_moves:
                continue
            pre.push(mv)
            if pre.board_fen() == post.board_fen():
                pre.pop()
                yield pre, mv


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    post = chess.Board(argv[0].split()[0] + ' b - - 0 1')
    for pre, mv in retractions(post):
        san = pre.san(mv)
        p = Problem.from_fen(pre.fen(), '#2')
        res = analyse(p, max_refutations=1, include_tries=True, include_set=True, time_limit=20)
        keys = [ph for ph in res['phases'] if ph['type'] == 'key']
        if len(keys) == 1 and keys[0]['first_move']['uci'] == mv.uci():
            print('=' * 60, '\n', san.replace('N', 'S'), pre.board_fen())
            print(format_compact(res))


if __name__ == '__main__':
    main()
