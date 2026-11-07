"""What a move changes, as text and as a picture: the view the 9 Oct and 6 Nov experiments asked for
(knowledge/experiments/board_pictures_2026-11-06.md: every false mate in analysis was a departure effect - a line
opened behind the moving piece, a guard the moving piece dropped, a slider that kept its guard, an unpinning).

    python tools/move_delta.py "<FEN with side to move>" "Rxc4 Qe5"            # text, one block per move
    python tools/move_delta.py "<FEN ...>" "Rxc4 Qe5" out.png                  # picture, one panel per move

Per move:
- opens:  squares other units newly see (the mover vacated its square, or a captured unit no longer blocks)
- closes: squares other units no longer see (the mover now stands in the way, or a captured unit's own lines vanish)
- drops / gains: what the mover attacked from its old square and not from the new one, and the reverse; the drops
          no unit of its side covers any more are named again (and crossed in the picture)
- keeps:  squares next to the black king the mover attacked before and still attacks (the slider moving along its line)
- pins / unpins, and the black king's flights gained or lost.
It says nothing about whether the move checks or mates: it shows the facts a reader overlooks, not the verdict.
"""
import os, sys
import chess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_pictures as bp


def _name(b, s):
    p = b.piece_at(s)
    return (('w' if p.color else 'b') + p.symbol().upper() + chess.square_name(s)) if p else chess.square_name(s)


def _attacks(b):
    return {s: set(b.attacks(s)) for s in b.piece_map()}


def _pinned(b):
    return {s for s, p in b.piece_map().items() if p.piece_type != chess.KING and b.is_pinned(p.color, s)}


def _flights(b):
    k = b.king(chess.BLACK)
    return {t for t in chess.SquareSet(chess.BB_KING_ATTACKS[k])
            if not b.attackers(chess.WHITE, t) and not (b.piece_at(t) and b.piece_at(t).color == chess.BLACK)}


def delta(b, move):
    """Facts that change when `move` is played on board b (b is not modified)."""
    a = b.copy(stack=False)
    a.push(move)
    before, after = _attacks(b), _attacks(a)
    fr, to = move.from_square, move.to_square
    k = a.king(chess.BLACK)
    near = set(chess.SquareSet(chess.BB_KING_ATTACKS[k])) | {k}
    opens, closes = {}, {}
    for s in set(before) | set(after):
        if s in (fr, to):
            continue
        new, old = after.get(s, set()), before.get(s, set())
        if new - old:
            opens[s] = new - old
        if old - new:
            closes[s] = old - new
    captured = to if b.piece_at(to) else (chess.square(chess.square_file(to), chess.square_rank(fr))
                                          if b.is_en_passant(move) else None)
    lost = before.get(captured, set()) if captured is not None else set()
    pin_b, pin_a = _pinned(b), _pinned(a)
    return {
        'board': b.copy(stack=False), 'after': a, 'move': move, 'san': b.san(move),
        'opens': opens, 'closes': closes,
        'drops': before[fr] - after[to] - {to}, 'gains': after[to] - before[fr],
        'keeps': (before[fr] & after[to]) & near,
        # squares the mover's side no longer covers with any unit (the drops that really cost something)
        'side_loses': {t for t in before[fr] - after[to] - {to}
                       if not a.attackers(b.piece_at(fr).color, t)},
        'captured': captured, 'captured_guards': lost,
        'pins': pin_a - pin_b, 'unpins': pin_b - pin_a,
        'flights_gained': _flights(a) - _flights(b), 'flights_lost': _flights(b) - _flights(a),
    }


def text(d):
    b, a = d['board'], d['after']
    sq = lambda ss: ' '.join(sorted(chess.square_name(t) + (f"({a.piece_at(t).symbol()})" if a.piece_at(t) else '')
                                    for t in ss))
    mover = _name(a, d['move'].to_square)
    out = [f"{d['san']}: {mover[:2]} {chess.square_name(d['move'].from_square)}->{chess.square_name(d['move'].to_square)}"]
    for s, ts in sorted(d['opens'].items()):
        out.append(f"  opens: {_name(a, s)} now sees {sq(ts)}")
    for s, ts in sorted(d['closes'].items()):
        out.append(f"  closes: {_name(a, s)} no longer sees {sq(ts)}")
    if d['captured'] is not None:
        out.append(f"  captured: {_name(b, d['captured'])}, which saw {sq(d['captured_guards']) or '-'}")
    out.append(f"  mover drops: {sq(d['drops']) or '-'}")
    if d['side_loses']:
        out.append(f"  of those, no {'White' if d['board'].turn else 'Black'} unit covers any more: {sq(d['side_loses'])}")
    out.append(f"  mover gains: {sq(d['gains']) or '-'}")
    if d['keeps']:
        out.append(f"  mover still guards next to the black king: {sq(d['keeps'])}")
    if d['pins']:
        out.append(f"  now pinned: {' '.join(_name(a, s) for s in sorted(d['pins']))}")
    if d['unpins']:
        out.append('  no longer pinned: ' + ' '.join(_name(b, s) + (' (captured)' if s == d['captured'] else '')
                                                    for s in sorted(d['unpins'])))
    for key, word in (('flights_gained', 'black king gains flight'), ('flights_lost', 'black king loses flight')):
        if d[key]:
            out.append(f"  {word}: {sq(d[key])}")
    return '\n'.join(out)


def _farthest(s, ts):
    """Group squares by direction from s and keep the farthest per direction (to draw one line per direction)."""
    best = {}
    for t in ts:
        df, dr = chess.square_file(t) - chess.square_file(s), chess.square_rank(t) - chess.square_rank(s)
        g = max(abs(df), abs(dr))
        key = (df // g, dr // g) if (df == 0 or dr == 0 or abs(df) == abs(dr)) else (df, dr)
        if key not in best or chess.square_distance(s, t) > chess.square_distance(s, best[key]):
            best[key] = t
    return best.values()


def _ring(t, col, w=3.0):
    x, y = bp._xy(t)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="none" stroke="{col}" stroke-width="{w}" opacity="0.9"/>'


def _cross(t, col):
    x, y = bp._xy(t)
    return (f'<path d="M{x - 8:.1f},{y - 8:.1f} L{x + 8:.1f},{y + 8:.1f} M{x + 8:.1f},{y - 8:.1f} L{x - 8:.1f},{y + 8:.1f}" '
            f'stroke="{col}" stroke-width="3.5" opacity="0.9"/>')


def svg(d, size=400):
    """The position after the move with: the move (grey), lines it opens (thick, side colour) and closes (dashed grey),
    guards the mover's side loses altogether (orange crosses) and keeps next to the king (green rings), pins (purple ring), unpins (purple
    dashed ring), flights gained (yellow) and lost (blue) under the pieces."""
    a = d['after']
    s = bp.re.sub(r'<desc>.*?</desc>', '', bp.chess.svg.board(a, size=size, coordinates=True), flags=bp.re.S)
    under = []
    for t, col in [(t, '#ffd400') for t in d['flights_gained']] + [(t, '#5a9bf0') for t in d['flights_lost']]:
        x, y = 15 + chess.square_file(t) * 45, 15 + (7 - chess.square_rank(t)) * 45
        under.append(f'<rect x="{x}" y="{y}" width="45" height="45" fill="{col}" opacity="0.6"/>')
    i = s.index('<use ')
    s = s[:i] + ''.join(under) + s[i:]
    fx, fy = bp._xy(d['move'].from_square)
    tx, ty = bp._xy(d['move'].to_square)
    over = ['<defs><marker id="hg" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" '
            'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#666666"/></marker></defs>',
            f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#666666" stroke-width="5" '
            f'opacity="0.75" marker-end="url(#hg)"/>']
    for u, ts in d['opens'].items():
        p = a.piece_at(u)
        for t in _farthest(u, ts):
            over.append(bp._line(u, t, bp.WHITE if p.color else bp.BLACK, p.color, width=5))
    for u, ts in d['closes'].items():
        p = a.piece_at(u)
        for t in _farthest(u, ts):
            over.append(bp._line(u, t, '#777777', p.color, dash=True, head=False, width=3))
    k = a.king(chess.BLACK)
    near = set(chess.SquareSet(chess.BB_KING_ATTACKS[k])) | {k}
    for t in d['side_loses']:
        if a.piece_at(t) or t in near:                       # guards really lost, on units and the king's field
            over.append(_cross(t, '#f08c00'))
    for t in d['keeps']:
        over.append(_ring(t, '#2b9a3e'))
    for t in d['pins']:
        over.append(_ring(t, '#8e44ad', 4))
    for t in d['unpins'] - {d['captured']}:
        x, y = bp._xy(t)
        over.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="none" stroke="#8e44ad" stroke-width="4" '
                    f'stroke-dasharray="4,3" opacity="0.9"/>')
    return s.replace('</svg>', bp.DEFS + ''.join(over) + '</svg>')


def deltas(fen, moves):
    b = chess.Board(fen)
    out = []
    for san in moves:
        m = b.parse_san(san)
        out.append(delta(b, m))
        b.push(m)
    return out


def png(ds, out, size=400):
    cells = ''.join(f'<div style="text-align:center;font:600 18px sans-serif">{d["board"].fullmove_number if not d["board"].turn else ""}'
                    f'{"..." if not d["board"].turn else ""}{d["san"]}<br>{svg(d, size)}</div>' for d in ds)
    html = (f'<html><body style="margin:0;background:#fff"><div style="display:grid;grid-template-columns:'
            f'repeat({len(ds)},{size}px);gap:16px;padding:12px">{cells}</div></body></html>')
    bp.render(html, out, len(ds) * (size + 16) + 24, size + 60, scale=2)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        sys.exit(__doc__)
    fen = argv[0] if len(argv[0].split()) > 1 else argv[0] + ' w - - 0 1'
    ds = deltas(fen, argv[1].split())
    if len(argv) > 2:
        png(ds, argv[2])
        print(argv[2])
    else:
        print('\n'.join(text(d) for d in ds))


if __name__ == '__main__':
    main()
