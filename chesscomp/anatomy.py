"""Anatomy of a #2: how it works on the board, not only what the solution is.

For every phase (set play, tries, key) and every variation it prints the king's field after the mate
(who covers each square, which squares Black blocked itself), what the first move changed in the field,
why each try fails (the field after the refutation, with the square or guard White lacks), and a role
table: which White unit works in which mate, and which unit never works (an idle unit is a fatal flaw).

    python -m chesscomp.anatomy --fen "<FEN>" [--tries 3] [--all]

Units are named by their diagram square (Qh3, Ba6, ph5 for a black pawn) so a piece keeps its name
after it moves.
"""
from __future__ import annotations
import argparse
import chess
from .core import Problem, san
from .analysis import analyse

LET = {chess.PAWN: 'P', chess.KNIGHT: 'S', chess.BISHOP: 'B', chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'}


class Names:
    """Diagram name of every unit, carried along as moves are made."""

    def __init__(self, board: chess.Board):
        self.at = {}
        for sq, p in board.piece_map().items():
            n = LET[p.piece_type] + chess.square_name(sq)
            self.at[sq] = n if p.color == chess.WHITE else n.lower()

    def copy(self):
        c = Names.__new__(Names); c.at = dict(self.at); return c

    def push(self, board: chess.Board, m: chess.Move):
        if board.is_en_passant(m):
            self.at.pop(m.to_square + (-8 if board.turn == chess.WHITE else 8), None)
        if board.is_castling(m):
            rf, rt = (chess.H1, chess.F1) if m.to_square > m.from_square else (chess.A1, chess.D1)
            if board.turn == chess.BLACK:
                rf, rt = rf + 56, rt + 56
            self.at[rt] = self.at.pop(rf, '?')
        self.at[m.to_square] = self.at.pop(m.from_square, '?')
        board.push(m)


def guards(board: chess.Board, names: Names, sq: int, color=chess.WHITE) -> list[str]:
    """Units of `color` covering sq, seen through the black king (a line through the king still guards)."""
    b = board.copy(stack=False)
    k = b.king(chess.BLACK)
    if k is not None and k != sq:
        b.remove_piece_at(k)
    return sorted(names.at.get(s, '?') for s in b.attackers(color, sq))


def field(board: chess.Board, names: Names, king_color=chess.BLACK) -> dict[int, str]:
    """sq -> short description of the black king's 3x3 field."""
    k = board.king(king_color)
    out = {}
    for sq in [k] + list(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        g = guards(board, names, sq)
        p = board.piece_at(sq)
        if sq == k:
            out[sq] = '@' + ('+' + ','.join(g) if g else '')     # the king's own square
        elif p and p.color == chess.BLACK:
            out[sq] = '[' + names.at.get(sq, '?') + ']'          # Black unit on its own king's field
        elif g:
            out[sq] = ','.join(g)
        else:
            out[sq] = '--FREE--'
    return out


def essential_pins(board: chess.Board, names: Names) -> list[tuple[str, str, str]]:
    """In a mate: Black units held by a pin that would otherwise capture the checker or interpose.
    Returns (pinner, pinned unit, square it is pinned on)."""
    k = board.king(chess.BLACK)
    checkers = list(board.checkers())
    out = []
    for sq in chess.SquareSet(board.occupied_co[chess.BLACK]):
        if sq == k or not board.is_pinned(chess.BLACK, sq):
            continue
        line = board.pin(chess.BLACK, sq)
        pinner = next((s for s in line if board.color_at(s) == chess.WHITE), None)
        parry = False
        for m in board.generate_pseudo_legal_moves(from_mask=chess.BB_SQUARES[sq]):
            if any(m.to_square == c or m.to_square in chess.SquareSet(chess.between(c, k)) for c in checkers):
                parry = True
        if parry and pinner is not None:
            out.append((names.at.get(pinner, '?'), names.at.get(sq, '?'), chess.square_name(sq)))
    return out


def needed_units(board: chess.Board, names: Names) -> list[str]:
    """In a mate: White units without which it is no longer mate (a guard, a pin, a plug on a Black line,
    a protector, the checker). The test is removal, so it sees jobs a guard map cannot."""
    out = []
    for sq in chess.SquareSet(board.occupied_co[chess.WHITE]):
        if board.piece_type_at(sq) == chess.KING:
            continue
        b = board.copy(stack=False)
        b.remove_piece_at(sq)
        if not b.is_checkmate():
            out.append(names.at.get(sq, '?'))
    return sorted(out)


def _mark_needed(board, names, f, lines, indent='      '):
    need = needed_units(board, names)
    for u in need:
        f[('needed', u)] = u
    seen = {v for k, v in f.items() if isinstance(k, tuple) and k[0] in ('pin', 'occupies')}
    sole = set()
    for sq, v in f.items():
        if isinstance(sq, int) and v[0] not in '@[' and ',' not in v and v != '--FREE--':
            sole.add(v)
    checker = names.at.get(board.peek().to_square) if board.move_stack else None
    other = [u for u in need if u not in sole and u not in seen and u != checker]
    if other:
        lines.append(f"{indent}needed beyond its guards (a plug, a protector, a line): {', '.join(other)}")


def draw_field(board, names, indent='      '):
    f = field(board, names)
    k = board.king(chess.BLACK)
    kf, kr = chess.square_file(k), chess.square_rank(k)
    w = max(len(v) for v in f.values()) + 1
    lines = []
    for r in (kr + 1, kr, kr - 1):
        cells = []
        for fl in (kf - 1, kf, kf + 1):
            if 0 <= fl < 8 and 0 <= r < 8:
                sq = chess.square(fl, r)
                cells.append(f"{chess.square_name(sq)} {f[sq].replace('@', 'K'):<{w}}")
            else:
                cells.append(' ' * (w + 3))
        lines.append(indent + ' '.join(cells))
    k = board.king(chess.BLACK)
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[k]):
        q = board.piece_at(sq)
        if q and q.color == chess.WHITE:                     # a White unit standing on a flight blocks it
            f[('occupies', chess.square_name(sq))] = names.at.get(sq, '?')
    for pinner, pinned, sq in essential_pins(board, names):
        lines.append(f"{indent}pin: {pinner} holds {pinned} on {sq} (it could parry the check)")
        f[('pin', sq)] = pinner
    return lines, f


def _double(f):
    """Squares covered twice in a mate: a sign of a unit that could be spared, or of a duty shared."""
    return [chess.square_name(s) for s, v in f.items() if isinstance(s, int) and ',' in v and v[0] not in '@[']


def field_change(before: chess.Board, after: chess.Board, nb: Names, na: Names) -> list[str]:
    """What a White first move changed in the black king's field (and the king's own square)."""
    k = before.king(chess.BLACK)
    out = []
    for sq in [k] + list(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        g0, g1 = set(guards(before, nb, sq)), set(guards(after, na, sq))
        if before.piece_at(sq) and before.color_at(sq) == chess.BLACK:
            continue
        lost, won = g0 - g1, g1 - g0
        s = chess.square_name(sq)
        if lost and not g1:
            out.append(f"{s}: unguarded ({','.join(sorted(lost))} gone) -> flight given")
        elif won and not g0:
            out.append(f"{s}: now guarded by {','.join(sorted(won))} (flight taken)")
        elif lost or won:
            out.append(f"{s}: {','.join(sorted(g0)) or '-'} -> {','.join(sorted(g1)) or '-'}")
    return out


def why_fails(board: chess.Board, names: Names, m: chess.Move) -> str:
    """board: White to move after a refutation. Why the move m (a threat) no longer mates."""
    if m not in board.legal_moves:
        if board.is_check():
            return f'{chess.square_name(m.from_square)}-{chess.square_name(m.to_square)}: impossible, White is in check'
        p = board.piece_at(m.from_square)
        if not p or p.color != chess.WHITE:
            return f'{chess.square_name(m.to_square)}: the threat piece was captured'
        return f'{names.at.get(m.from_square)}-{chess.square_name(m.to_square)}: illegal now (line blocked or pinned)'
    b, n = board.copy(), names.copy()
    mv = san(b, m)
    n.push(b, m)
    if not b.is_check():
        return f'{mv}: no longer check'
    out = []
    for e in b.legal_moves:
        p = b.piece_at(e.from_square)
        if p.piece_type == chess.KING:
            out.append(('Kx' if b.piece_at(e.to_square) else 'flight ') + chess.square_name(e.to_square))
        elif e.to_square in [s for s in b.checkers()]:
            out.append(f'{n.at.get(e.from_square)} takes the checker')
        else:
            out.append(f'{n.at.get(e.from_square)} interposes on {chess.square_name(e.to_square)}')
    return f'{mv}: ' + ', '.join(dict.fromkeys(out))


def _uci(board, u):
    return chess.Move.from_uci(u)


def phase_anatomy(problem: Problem, ph: dict, roles: dict | None, show_all: bool,
                  collect: list | None = None) -> list[str]:
    b0 = problem.board.copy()
    n0 = Names(b0)
    L = []
    if ph['type'] == 'set':
        L.append('SET PLAY')
        b1, n1 = b0.copy(), n0.copy()
        b1.turn = chess.BLACK
    else:
        fm = _uci(b0, ph['first_move']['uci'])
        tag = 'KEY' if ph['type'] == 'key' else 'TRY'
        b1, n1 = b0.copy(), n0.copy()
        n1.push(b1, fm)
        thr = ', '.join(t['san'] for t in ph.get('threat', [])) or ('zugzwang' if ph.get('zugzwang') else 'check')
        if ph.get('stalemate'):
            L.append(f"{tag} 1.{ph['first_move']['san']}?   stalemate: Black has no move")
            return L
        L.append(f"{tag} 1.{ph['first_move']['san']}{'!' if tag == 'KEY' else '?'}   threat: {thr}")
        ch = field_change(b0, b1, n0, n1)
        if ch:
            L.append('   field change: ' + '; '.join(ch))
    # group variations by mate set
    seen_mates = {}
    threat_ids = {t['id'] for t in ph.get('threat', [])}
    for v in ph.get('variations', []):
        conts = v['continuations']
        if not conts:
            continue
        ids = tuple(sorted(c['id'] for c in conts))
        unit = v['defence']['uci'][:2]          # one drawing per Black unit and mate set
        seen_mates.setdefault((ids, unit), []).append(v)
    if ph.get('threat'):
        bt, nt = b1.copy(), n1.copy()
        bt.push(chess.Move.null())
        t = ph['threat'][0]
        nt.push(bt, _uci(bt, t['uci']))
        L.append(f"   threat 2.{t['san']}")
        lines, f = draw_field(bt, nt)
        _mark_needed(bt, nt, f, lines)
        L += lines
        if roles is not None:
            _note_roles(roles, f, 'threat')
    for (ids, _), vs in seen_mates.items():
        if set(ids) <= threat_ids and not show_all and not any(v['defence']['san'].startswith('K') for v in vs):
            continue
        v = vs[0]
        bd, nd = b1.copy(), n1.copy()
        d = _uci(bd, v['defence']['uci'])
        nd.push(bd, d)
        c = v['continuations'][0]
        nd.push(bd, _uci(bd, c['uci']))
        defs = ','.join(x['defence']['san'] for x in vs)
        mates = '/'.join(x['san'] for x in v['continuations'])
        L.append(f"   1...{defs} 2.{mates}" + ('   DUAL' if len(v['continuations']) > 1 else ''))
        lines, f = draw_field(bd, nd)
        _mark_needed(bd, nd, f, lines)
        L += lines
        dbl = _double(f)
        if dbl:
            L.append(f"      covered twice: {', '.join(dbl)}")
        if roles is not None:
            _note_roles(roles, f, defs)
        if collect is not None and len(v['continuations']) == 1 and not set(ids) <= threat_ids:
            collect.append((defs, nd.at.get(bd.peek().to_square, '?'), f))
    for r in ph.get('refutations', []):
        br, nr = b1.copy(), n1.copy()
        nr.push(br, _uci(br, r['uci']))
        L.append(f"   refuted by 1...{r['san']}!")
        thr = ph.get('threat') or []
        if not thr:
            L.append('      (zugzwang try) Black\'s field after it, White to move:')
            L += draw_field(br, nr)[0]
        for t in thr:
            L.append('      ' + why_fails(br, nr, chess.Move.from_uci(t['uci'])))
    return L


def _cover(f, sq):
    v = f.get(sq, '')
    if not isinstance(sq, int) or v.startswith('@') or v.startswith('[') or v == '--FREE--':
        return set()
    return set(v.split(','))


def links(mates: list) -> list[str]:
    """How the variations of a phase hang together (E. Bourd, 11 Oct 2026: "both mating pieces guard the same c5 ...
    each of the other variations they have a job ... the play seems connected, and not like 2 distant variations").
    mates: (defences, mating unit, field) per single-mate variation. Reports squares two mating units hold for each
    other (each the only guard in the other's mate), then mating units that work in another unit's mate."""
    out = []
    for i, (d1, m1, f1) in enumerate(mates):
        for d2, m2, f2 in mates[i + 1:]:
            if m1 == m2:
                continue
            for sq in sorted(s for s in f1 if isinstance(s, int)):
                if _cover(f1, sq) == {m2} and _cover(f2, sq) == {m1}:
                    out.append(f"   {m1} and {m2} hold {chess.square_name(sq)} for each other: "
                               f"{m2} alone after {d1}, {m1} alone after {d2}")
    mating = {m for _, m, _ in mates}
    for d, m, f in mates:
        helpers = {}
        for sq in (s for s in f if isinstance(s, int)):
            for u in _cover(f, sq) & (mating - {m}):
                helpers.setdefault(u, []).append(chess.square_name(sq) + ('' if _cover(f, sq) == {u} else '='))
        for u, sqs in sorted(helpers.items()):
            out.append(f"   {u} works in the mate after {d} (by {m}): {' '.join(sorted(sqs))}")
    return out


def _note_roles(roles, f, label):
    for sq, v in f.items():
        if not isinstance(sq, int):
            if sq[0] == 'needed':
                roles.setdefault(v, []).append((label, 'needed', '!'))
                continue
            tag = 'pin@' if sq[0] == 'pin' else 'on '
            roles.setdefault(v, []).append((label, tag + sq[1], ''))
            continue
        if v.startswith('['):
            continue
        body = v[2:] if v.startswith('@+') else ('' if v.startswith('@') else v)
        us = [u for u in body.split(',') if u and u != '--FREE--']
        for u in us:
            mark = ('*' if v.startswith('@+') else '') + ('=' if len(us) > 1 else '')
            roles.setdefault(u, []).append((label, chess.square_name(sq), mark))


def anatomy(fen: str, tries: int = 2, show_all: bool = False) -> str:
    p = Problem.from_fen(fen if ' ' in fen else fen + ' w - - 0 1', '#2')
    res = analyse(p, max_refutations=tries)
    out = [p.diagram(), '']
    roles = {}
    phases = res.get('phases', [])
    order = [x for x in phases if x['type'] == 'set'] + [x for x in phases if x['type'] == 'try'] + \
            [x for x in phases if x['type'] == 'key']
    key_mates = []
    for ph in order:
        out += phase_anatomy(p, ph, roles if ph['type'] == 'key' else None, show_all,
                             key_mates if ph['type'] == 'key' else None)
        out.append('')
    if key_mates:
        lk = links(key_mates)
        out.append('LINKS between the variations of the solution (mating units reused; = shared with another unit)')
        out += lk or ['   none: each mate is made by its own units']
        out.append('')
    # role table for the solution
    out.append('ROLES in the solution (unit: variation/square it covers; * = gives check, = = square also covered by another unit)')
    names = Names(p.board)
    for sq, n in sorted(names.at.items(), key=lambda kv: (kv[1][0].islower(), kv[1])):
        if n[0].islower():
            continue
        r = roles.get(n, [])
        if not r:
            out.append(f"   {n:5} -- takes no part in any mate of the solution --")
            continue
        need = sorted({lab for lab, _, mark in r if mark == '!'})
        r = [x for x in r if x[2] != '!']
        by = {}
        for lab, s, mark in r:
            by.setdefault(lab, []).append(s + mark)
        sole = any(not mark.endswith('=') for _, _, mark in r)
        text = '; '.join(f"{lab}: {' '.join(v)}" for lab, v in by.items()) or '(no guard)'
        if not need:
            text += '   <- needed in no mate (removing it keeps every mate): only for tries or soundness?'
        elif not sole:
            text += f"   <- needed only as plug/protector/line, in: {'; '.join(need)}"
        out.append(f"   {n:5} {text}")
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--fen', required=True)
    ap.add_argument('--tries', type=int, default=2, help='show tries with up to N refutations')
    ap.add_argument('--all', action='store_true', help='also show variations that repeat the threat')
    a = ap.parse_args(argv)
    print(anatomy(a.fen, a.tries, a.all))


if __name__ == '__main__':
    main()
