"""Which error of a Black defence enables each White mate: its departure, its arrival, either, or both together.

E. Bourd (14 Oct 2026), on type-1 changed mates: "instead of one piece defending 2 squares, another error happens:
unguard + line close for example"; "unguard/line-close + line-opening; there are many combinations of creating two
errors at once". A defence makes two errors when the set mate comes from one part of the move and the solution mate
from the other (or from a different error of the same part). This splits a Black move a->b into:

  departure only: the unit is removed from a (guards given up, lines through a opened, a vacated)
  arrival only:   the unit stays on a and a copy stands on b (lines through b closed, b self-blocked, new guards)

and asks, for each mate, whether it still mates on each partial board. 'departure' = only the departure board mates,
'arrival' = only the arrival board, 'either' = both (the mate has two causes), 'both' = neither alone (the two
errors work together). `effects` names the errors themselves.

    python -m chesscomp.compose.errors FEN DEFENCE [DEFENCE ...] [--key UCI]     # FEN: the diagram, White to move
"""
from __future__ import annotations
import argparse
import chess
from .effects import effects


def _mates(board: chess.Board) -> set[str]:
    out = set()
    for m in board.legal_moves:
        b = board.copy()
        b.push(m)
        if b.is_checkmate():
            out.add(board.san(m).rstrip('#+').replace('N', 'S'))
    return out


def split(board: chess.Board, move: chess.Move) -> dict[str, chess.Board]:
    """board: Black to move. Returns the full, departure-only and arrival-only boards, White to move."""
    full = board.copy()
    full.push(move)
    unit = board.piece_at(move.from_square)
    dep = board.copy()
    dep.remove_piece_at(move.from_square)
    dep.turn = chess.WHITE
    arr = board.copy()
    arr.remove_piece_at(move.to_square)
    arr.set_piece_at(move.to_square, chess.Piece(move.promotion or unit.piece_type, unit.color))
    arr.turn = chess.WHITE
    for b in (dep, arr):
        b.ep_square = None
        b.clear_stack()
    return {'full': full, 'departure': dep, 'arrival': arr}


def classify(board: chess.Board, move: chess.Move) -> dict[str, str]:
    """mate SAN (as played after the full defence) -> 'departure' | 'arrival' | 'either' | 'both'"""
    bs = split(board, move)
    full = _mates(bs['full'])
    dep, arr = _mates(bs['departure']), _mates(bs['arrival'])
    out = {}
    for m in sorted(full):
        d, a = m.replace('x', '') in {x.replace('x', '') for x in dep}, m.replace('x', '') in {x.replace('x', '') for x in arr}
        out[m] = 'either' if d and a else 'departure' if d else 'arrival' if a else 'both'
    return out


def report(fen: str, defences: list[str], key: str | None = None) -> str:
    diagram = chess.Board(fen if len(fen.split()) > 1 else fen + ' w - - 0 1')
    phases = [('set', diagram)]
    if key:
        post = diagram.copy()
        post.push_uci(key)
        phases.append(('after ' + diagram.san(chess.Move.from_uci(key)), post))
    lines = []
    for name, ph in phases:
        b = ph.copy()
        b.turn = chess.BLACK
        lines.append(f'{name}:')
        for d in defences:
            try:
                m = b.parse_san(d.replace('S', 'N'))
            except ValueError:
                lines.append(f'  {d}: not legal here')
                continue
            cls = classify(b, m)
            txt = ', '.join(f'{k}# ({v})' for k, v in cls.items()) or 'no mate'
            lines.append(f'  1...{d}: {txt}')
    lines.append('errors (effects, on the last phase):')
    last = phases[-1][1]
    for d in defences:
        for e in effects(last.board_fen(), d.replace('S', 'N')):
            lines.append(f'  {d}: {e}')
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('fen')
    ap.add_argument('defences', nargs='+')
    ap.add_argument('--key')
    a = ap.parse_args(argv)
    print(report(a.fen, a.defences, a.key))


if __name__ == '__main__':
    main()
