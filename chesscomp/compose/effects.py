"""The errors of a Black move, listed mechanically, so a mate is chosen for a named error before any search.

E. Bourd (8 Oct 2026), on a hole that a one-unit search could not fill: "you have to find an error for the Se4
move ... this small thing cannot be just search, it has to be a more structured approach." This lists, for a
Black move in a post-key position, what its departure and its arrival change: squares of the king's field
self-blocked or vacated, White lines it opens or closes (with the squares each line gains or loses), Black
guards it gives up or adds, pins it makes or breaks. Each line is a possible error; the composer picks one, names
the mate that would exploit it, and checks that no other defence commits the same error (or the mate becomes a
dual for it too).

    python3 -m chesscomp.compose.effects POSTKEY [MOVE ...]     # no MOVE: every Black move that stops the threat
"""
from __future__ import annotations
import sys
import chess
from .keyfind import post_spec

NAMES = {chess.PAWN: 'P', chess.KNIGHT: 'S', chess.BISHOP: 'B', chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'}


def _pn(board, sq):
    p = board.piece_at(sq)
    return ('w' if p.color else 'b') + NAMES[p.piece_type] + chess.square_name(sq)


def _sqs(bb):
    return ','.join(chess.square_name(s) for s in chess.SquareSet(bb)) or '-'


def effects(fen: str, san: str) -> list[str]:
    before = chess.Board(fen + ' b - - 0 1')
    m = before.parse_san(san)
    after = before.copy(); after.push(m)
    bk = before.king(chess.BLACK)
    field = chess.BB_KING_ATTACKS[bk]
    out = []
    mover = before.piece_at(m.from_square)
    if m.to_square != bk and chess.BB_SQUARES[m.to_square] & field:
        out.append(f"self-block {chess.square_name(m.to_square)} (a square of the king's field is now occupied)")
    if chess.BB_SQUARES[m.from_square] & field and mover.piece_type != chess.KING:
        out.append(f"vacates {chess.square_name(m.from_square)} next to the king (a new flight unless White guards it)")
    if before.piece_at(m.to_square):
        out.append(f"captures {_pn(before, m.to_square)} (its guards are gone: {_sqs(int(before.attacks(m.to_square)) & field)} near the king)")
    # white lines opened / closed: compare each white piece's attacks
    for sq in chess.SquareSet(before.occupied_co[chess.WHITE]):
        if after.piece_at(sq) is None or after.piece_at(sq).color != chess.WHITE:
            continue
        a0, a1 = int(before.attacks(sq)), int(after.attacks(sq))
        gained, lost = a1 & ~a0, a0 & ~a1
        if gained:
            out.append(f"opens a line of {_pn(before, sq)}: now reaches {_sqs(gained)}" + (f" (king's field: {_sqs(gained & field)})" if gained & field else ''))
        if lost:
            out.append(f"closes a line of {_pn(before, sq)}: no longer reaches {_sqs(lost)}" + (f" (king's field: {_sqs(lost & field)})" if lost & field else ''))
    # black guards given up / added (by the mover and by black line pieces it unblocks or blocks)
    for sq in chess.SquareSet(before.occupied_co[chess.BLACK]):
        if sq == bk:
            continue
        a0 = int(before.attacks(sq))
        sq1 = m.to_square if sq == m.from_square else sq
        if after.piece_at(sq1) is None or after.piece_at(sq1).color != chess.BLACK:
            continue
        a1 = int(after.attacks(sq1))
        lost, gained = a0 & ~a1, a1 & ~a0
        who = _pn(before, sq) + ('->' + chess.square_name(sq1) if sq1 != sq else '')
        if lost:
            out.append(f"black {who} stops guarding {_sqs(lost)}")
        if gained:
            out.append(f"black {who} now guards {_sqs(gained)}")
    # pins
    for col, word in ((chess.BLACK, 'black'), (chess.WHITE, 'white')):
        p0 = {s for s in chess.SquareSet(before.occupied_co[col]) if before.is_pinned(col, s)}
        p1 = {s for s in chess.SquareSet(after.occupied_co[col]) if after.is_pinned(col, s)}
        for s in p1 - p0 - {m.to_square}:
            out.append(f"pins its own unit? {word} {_pn(after, s)} is now pinned")
        if col == chess.BLACK and m.to_square in p1:
            out.append(f"self-pin: the moved unit is pinned on {chess.square_name(m.to_square)}")
        for s in p0 - p1 - {m.from_square}:
            out.append(f"unpins {word} {_pn(before, s)}")
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    fen = argv[0].split()[0]
    moves = argv[1:]
    b = chess.Board(fen + ' b - - 0 1')
    if not moves:
        _, defs = post_spec(fen)
        moves = [b.san(chess.Move.from_uci(u)) for u in defs]
    # an error that another defence commits too cannot select a mate for this one alone (E. Bourd, 8 Oct 2026:
    # "unguard has the same error as the other knight defence"): mark what is shared
    _, defs = post_spec(fen)
    all_moves = list(dict.fromkeys(moves + [b.san(chess.Move.from_uci(u)) for u in defs]))
    table = {mv: effects(fen, mv) for mv in all_moves}
    def key(e):                                   # the error itself, not the unit that commits it
        return e.split(' (')[0] if e.startswith(('opens', 'closes', 'self-block', 'vacates', 'unpins')) else None
    for san in moves:
        mv = b.parse_san(san)
        b2 = b.copy(); b2.push(mv)
        mates = []
        for x in list(b2.legal_moves):
            s = b2.san(x); b2.push(x)
            if b2.is_checkmate(): mates.append(s)
            b2.pop()
        print(f"1...{san}   mates now: {', '.join(mates) or 'NONE (hole)'}")
        for e in table[san]:
            k = key(e)
            shared = [o for o in all_moves if o != san and k and any(key(x) == k for x in table[o])]
            print('   ' + e + (f"   [also {', '.join(shared)}]" if shared else ('   <- only this move' if k else '')))


if __name__ == '__main__':
    main()
