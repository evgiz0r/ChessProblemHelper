"""Text views of a chess position, for a language model to read.

Ported from the board-views experiment of 9 Oct 2026 (evgiz0r/Personaldashboard, branch
ccr-859f3d72-q4pgb7, chesslab/lab/views.py; rebuilt from that session's transcript, code unchanged).
What was measured with them: knowledge/experiments/board_views_2026-10-09.md.

    python tools/board_views.py "<FEN>"                 # every view
    python tools/board_views.py "<FEN>" annotated tree1 # some views

Every view is a function Board -> str registered in VIEWS. Views must never contain answers to bench
probes beyond what their description promises (e.g. `relations` lists attacks, but never says "pinned"
or "hanging"); LEAKS says which probes each view gives away.
"""
import chess

DIRS = {'↑': (0, 1), '↓': (0, -1), '→': (1, 0), '←': (-1, 0),
        '↗': (1, 1), '↖': (-1, 1), '↘': (1, -1), '↙': (-1, -1)}
ROOK_DIRS = ['↑', '↓', '→', '←']
BISHOP_DIRS = ['↗', '↖', '↘', '↙']


def sq(s):
    return chess.square_name(s)


def piece_str(b, s):
    p = b.piece_at(s)
    return ('w' if p.color else 'b') + p.symbol().upper() + sq(s)


def side_to_move(b):
    return "Side to move: " + ("White" if b.turn else "Black") + " (uppercase=White, lowercase=Black)"


def grid_lines(b):
    rows = []
    for r in range(7, -1, -1):
        cells = [(b.piece_at(chess.square(f, r)).symbol() if b.piece_at(chess.square(f, r)) else '.') for f in range(8)]
        rows.append(f"{r + 1} | " + ' '.join(cells))
    rows += ["    " + '-' * 15, "    a b c d e f g h"]
    return rows


def piece_list(b):
    out = []
    order = 'KQRBNP'
    for color, name in ((chess.WHITE, 'White'), (chess.BLACK, 'Black')):
        items = sorted(((s, p) for s, p in b.piece_map().items() if p.color == color),
                       key=lambda x: (order.index(x[1].symbol().upper()), x[0]))
        out.append(f"{name}: " + ' '.join(p.symbol().upper() + sq(s) for s, p in items))
    return out


def ray(s, d):
    df, dr = DIRS[d]
    f, r = chess.square_file(s), chess.square_rank(s)
    while True:
        f += df
        r += dr
        if not (0 <= f < 8 and 0 <= r < 8):
            return
        yield chess.square(f, r)


def slider_dirs(p):
    return (ROOK_DIRS if p.piece_type in (chess.ROOK, chess.QUEEN) else []) + \
           (BISHOP_DIRS if p.piece_type in (chess.BISHOP, chess.QUEEN) else [])


def mark(b, s, owner_color):
    p = b.piece_at(s)
    if not p:
        return sq(s)
    return f"{sq(s)}[{p.symbol()} {'own' if p.color == owner_color else 'ENEMY'}]"


# ---------------------------------------------------------------- views

def v_fen(b):
    return f"FEN: {b.fen()}"


def v_grid(b):
    return '\n'.join(grid_lines(b) + [side_to_move(b)])


def v_grid_list(b):
    return '\n'.join(grid_lines(b) + piece_list(b) + [side_to_move(b)])


def all_lines():
    lines = [(f"file {'abcdefgh'[f]}", [chess.square(f, r) for r in range(8)]) for f in range(8)]
    lines += [(f"rank {r + 1}", [chess.square(f, r) for f in range(8)]) for r in range(8)]
    for d in range(-6, 7):
        s = [chess.square(f, f - d) for f in range(8) if 0 <= f - d < 8]
        lines.append((f"diag↗ {sq(s[0])}-{sq(s[-1])}", s))
    for d in range(1, 14):
        s = sorted((chess.square(f, d - f) for f in range(8) if 0 <= d - f < 8), key=chess.square_file)
        lines.append((f"diag↘ {sq(s[0])}-{sq(s[-1])}", s))
    return lines


def v_lines(b):
    """Every file/rank/diagonal with 2+ pieces written out contiguously."""
    out = grid_lines(b) + piece_list(b) + ["", "LINES (only lines holding 2+ pieces):"]
    for name, sqs in all_lines():
        if sum(1 for s in sqs if b.piece_at(s)) >= 2:
            out.append(f"{name}: " + ' '.join(f"{sq(s)}={b.piece_at(s).symbol() if b.piece_at(s) else '.'}" for s in sqs))
    return '\n'.join(out + [side_to_move(b)])


def v_relations(b):
    """Attack sets per piece + attackers/defenders per piece (separate tables)."""
    out = grid_lines(b) + piece_list(b) + ["", "ATTACKS (squares each piece attacks; occupied ones marked):"]
    pieces = sorted(b.piece_map().items(), key=lambda x: (not x[1].color, x[0]))
    for s, p in pieces:
        tg = [sq(t) + (f"({b.piece_at(t).symbol()})" if b.piece_at(t) else '') for t in sorted(b.attacks(s))]
        out.append(f"{piece_str(b, s)} -> {' '.join(tg) or '(none)'}")
    out += ["", "PIECE STATUS (attacked by enemy / defended by own):"]
    for s, p in pieces:
        att = [piece_str(b, a) for a in b.attackers(not p.color, s)]
        dfn = [piece_str(b, a) for a in b.attackers(p.color, s)]
        out.append(f"{piece_str(b, s)}: attacked by [{', '.join(att)}] defended by [{', '.join(dfn)}]")
    return '\n'.join(out + [side_to_move(b)])


def annotate_piece(b, s):
    """One line: the piece with its lines of sight, blockers and x-ray beyond."""
    p = b.piece_at(s)
    parts = []
    if p.piece_type in (chess.BISHOP, chess.ROOK, chess.QUEEN):
        for d in slider_dirs(p):
            seen, xray = [], None
            it = ray(s, d)
            for t in it:
                if b.piece_at(t):
                    seen.append(mark(b, t, p.color))
                    for u in it:  # look through the first blocker
                        if b.piece_at(u):
                            xray = mark(b, u, p.color)
                            break
                    break
                seen.append(sq(t))
            if seen:
                parts.append(f"{d} {' '.join(seen)}" + (f" (x-ray→ {xray})" if xray else ''))
    else:
        tg = [mark(b, t, p.color) for t in sorted(b.attacks(s))]
        parts.append(('attacks ' if p.piece_type == chess.PAWN else '→ ') + (' '.join(tg) or '(none)'))
    att = [piece_str(b, a)[1:] for a in b.attackers(not p.color, s)]
    dfn = [piece_str(b, a)[1:] for a in b.attackers(p.color, s)]
    status = f"  {{attacked by {','.join(att) or '-'}; defended by {','.join(dfn) or '-'}}}"
    return f"{p.symbol().upper()}{sq(s)}: " + '   '.join(parts) + status


def v_annotated(b):
    """Each piece carries its own lines of sight inline (best composing method so far)."""
    out = grid_lines(b) + ["", "PIECES (lines of sight per direction; first blocker marked; x-ray = next piece behind it):"]
    for color, name in ((chess.WHITE, 'White'), (chess.BLACK, 'Black')):
        out.append(f"{name}:")
        for s, p in sorted(b.piece_map().items(), key=lambda x: ('KQRBNP'.index(x[1].symbol().upper()), x[0])):
            if p.color == color:
                out.append("  " + annotate_piece(b, s))
    return '\n'.join(out + [side_to_move(b)])


def king_zone(b, defender):
    """Flight squares of `defender`'s king and who covers them."""
    k = b.king(defender)
    out = [f"{'White' if defender else 'Black'} king {sq(k)} zone:"]
    for t in sorted(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        p = b.piece_at(t)
        occ = f"own {p.symbol()}" if p and p.color == defender else (f"enemy {p.symbol()}" if p else "empty")
        cov = [piece_str(b, a)[1:] for a in b.attackers(not defender, t)]
        out.append(f"  {sq(t)}: {occ}; covered by [{', '.join(cov)}]")
    return out


def v_kingzone(b):
    chk = sorted(b.san(m) for m in b.legal_moves if b.gives_check(m))
    return '\n'.join([v_relations(b), ""] + king_zone(b, not b.turn)
                     + [f"ALL CHECKS for side to move: {', '.join(chk) or '(none)'}"])


def v_tree1(b):
    """kingzone + the opponent's legal replies after every check/capture (one ply of search)."""
    out = [v_kingzone(b), "", "1-PLY TREE (each checking or capturing move: opponent's legal replies):"]
    for m in sorted(b.legal_moves, key=b.san):
        if b.gives_check(m) or b.is_capture(m):
            san = b.san(m)
            b.push(m)
            reps = sorted(b.san(r) for r in b.legal_moves)
            b.pop()
            out.append(f"  {san}: {len(reps)} replies: {' '.join(reps)}")
    return '\n'.join(out)


def v_salient(b):
    """Only the relations that usually matter, named: loose pieces, lines to K/Q, king zones, checks."""
    out = grid_lines(b) + piece_list(b) + ["", "SALIENT RELATIONS:"]
    for s, p in b.piece_map().items():
        if p.piece_type == chess.KING:
            continue
        att = b.attackers(not p.color, s)
        if not att:
            continue
        dfn = b.attackers(p.color, s)
        cheaper = [a for a in att if VAL[b.piece_at(a).piece_type] < VAL[p.piece_type]]
        if not dfn:
            out.append(f"  LOOSE: {piece_str(b, s)} attacked by {', '.join(piece_str(b, a) for a in att)}, undefended")
        elif cheaper:
            out.append(f"  ATTACKED BY CHEAPER: {piece_str(b, s)} by {', '.join(piece_str(b, a) for a in cheaper)}")
    for s, p in b.piece_map().items():
        if p.piece_type not in (chess.BISHOP, chess.ROOK, chess.QUEEN):
            continue
        for d in slider_dirs(p):
            hits = [t for t in ray(s, d) if b.piece_at(t)][:2]
            if not hits:
                continue
            first = b.piece_at(hits[0])
            if first.color != p.color and first.piece_type in (chess.KING, chess.QUEEN):
                kind = 'CHECK-LINE' if first.piece_type == chess.KING else 'ATTACKS QUEEN'
                out.append(f"  {kind}: {piece_str(b, s)} {d} {piece_str(b, hits[0])}")
            elif len(hits) == 2:
                tgt = b.piece_at(hits[1])
                if tgt.color != p.color and tgt.piece_type in (chess.KING, chess.QUEEN):
                    if first.color != p.color:
                        kind = 'PIN' if tgt.piece_type == chess.KING else 'PIN(to Q)'
                    else:
                        kind = 'BATTERY (discovery possible)'
                    out.append(f"  {kind}: {piece_str(b, s)} {d} through {piece_str(b, hits[0])} to {piece_str(b, hits[1])}")
    open_files = []
    for f in range(8):
        pawns = [b.piece_at(chess.square(f, r)) for r in range(8)]
        if not any(x and x.piece_type == chess.PAWN for x in pawns):
            open_files.append('abcdefgh'[f])
    if open_files and len(open_files) < 8:
        out.append(f"  OPEN FILES (no pawns): {' '.join(open_files)}")
    out += [""] + king_zone(b, chess.WHITE) + king_zone(b, chess.BLACK)
    chk = sorted(b.san(m) for m in b.legal_moves if b.gives_check(m))
    out.append(f"CHECKS for side to move: {', '.join(chk) or '(none)'}")
    return '\n'.join(out + [side_to_move(b)])


VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}

VIEWS = {
    'fen': v_fen, 'grid': v_grid, 'grid_list': v_grid_list, 'lines': v_lines,
    'relations': v_relations, 'annotated': v_annotated, 'salient': v_salient,
    'kingzone': v_kingzone, 'tree1': v_tree1,
}

# Which bench probes each view gives away directly (so scores on those probes are not
# evidence of perception). Keep this honest when adding views.
LEAKS = {
    'relations': {'hanging', 'profitable_captures'},
    'annotated': {'hanging', 'slider_rays', 'xray_lines', 'profitable_captures', 'pins'},  # x-ray through ENEMY piece to king = pin
    'salient': {'hanging', 'pins', 'xray_lines', 'checks'},
    'kingzone': {'hanging', 'checks', 'profitable_captures'},
    'tree1': {'hanging', 'checks', 'profitable_captures'},
}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('fen', help='FEN; side to move defaults to White')
    ap.add_argument('views', nargs='*', help='view names (default: all): ' + ' '.join(VIEWS))
    a = ap.parse_args(argv)
    fen = a.fen if len(a.fen.split()) > 1 else a.fen + ' w - - 0 1'
    b = chess.Board(fen)
    for name in a.views or VIEWS:
        print(f"===== {name} =====")
        print(VIEWS[name](b))
        print()


if __name__ == '__main__':
    main()
