"""Picture views of a position: the text views of tools/board_views.py drawn on the board (E. Bourd, 6 Nov 2026:
"think about those different visualizations as they might relate visually").

    python tools/board_pictures.py "<FEN>" out.png [plain|rays|arrows|field|all]    # all = the four side by side

- plain:  the diagram alone (what a model gets when it is shown the board).
- rays:   `annotated` drawn: every line piece's lines of sight to the first unit (White blue, Black red), a faint
          continuation behind that unit (x-ray), knight jumps and pawn captures as short arrows.
- arrows: `relations` drawn: an arrow from every unit to every unit it attacks or defends (White blue, Black red).
- field:  `kingzone` drawn: each square shaded by the number of White units guarding it (0 none .. 3+ dark),
          the black king's field outlined, empty field squares no White unit guards (flights) in yellow.
"""
import glob, re, sys
import chess, chess.svg

WHITE, BLACK = '#1f5fd1', '#d12f1f'
DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]


def _ray(s, d):
    f, r = chess.square_file(s), chess.square_rank(s)
    while True:
        f, r = f + d[0], r + d[1]
        if not (0 <= f < 8 and 0 <= r < 8):
            return
        yield chess.square(f, r)


def _dirs(p):
    out = []
    if p.piece_type in (chess.ROOK, chess.QUEEN):
        out += DIRS[:4]
    if p.piece_type in (chess.BISHOP, chess.QUEEN):
        out += DIRS[4:]
    return out


def _xy(t, off=0.0, d=(0, 0)):
    """Centre of square t in chess.svg's 390-unit board (15-unit margin, 45-unit squares), shifted sideways."""
    x = 15 + chess.square_file(t) * 45 + 22.5
    y = 15 + (7 - chess.square_rank(t)) * 45 + 22.5
    n = (d[0] ** 2 + d[1] ** 2) ** 0.5 or 1
    return x - d[1] / n * off, y - d[0] / n * off      # perpendicular offset (screen y points down)


def _line(a, b_, col, white, dash=False, head=True, width=3.0):
    d = (chess.square_file(b_) - chess.square_file(a), chess.square_rank(b_) - chess.square_rank(a))
    off = 2.5 if white else -2.5
    x1, y1 = _xy(a, off, d)
    x2, y2 = _xy(b_, off, d)
    k = 13 / max(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5, 1)   # stop short of the target's centre
    x2, y2 = x2 - (x2 - x1) * k, y2 - (y2 - y1) * k
    extra = ' stroke-dasharray="5,4" opacity="0.55"' if dash else ' opacity="0.9"'
    mk = f' marker-end="url(#h{"w" if white else "b"})"' if head else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{width}"{extra}{mk}/>'


DEFS = (f'<defs><marker id="hw" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{WHITE}"/></marker>'
        f'<marker id="hb" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{BLACK}"/></marker></defs>')


def rays(b):
    """annotated, drawn: lines of sight to the first unit, dashed x-ray to the next one, knight and pawn jumps."""
    out = []
    for s, p in b.piece_map().items():
        col = WHITE if p.color else BLACK
        if p.piece_type in (chess.BISHOP, chess.ROOK, chess.QUEEN):
            for d in _dirs(p):
                sqs = list(_ray(s, d))
                if not sqs:
                    continue
                stop = next((i for i, t in enumerate(sqs) if b.piece_at(t)), None)
                out.append(_line(s, sqs[stop] if stop is not None else sqs[-1], col, p.color))
                if stop is not None and stop + 1 < len(sqs):
                    rest = sqs[stop + 1:]
                    out.append(_line(sqs[stop], next((t for t in rest if b.piece_at(t)), rest[-1]), col, p.color,
                                     dash=True, head=False))
        elif p.piece_type in (chess.KNIGHT, chess.PAWN):
            for t in b.attacks(s):
                out.append(_line(s, t, col, p.color, width=2.2))
    return out


def arrows(b):
    """relations, drawn: an arrow from every unit to every unit it attacks or defends."""
    return [_line(s, t, WHITE if p.color else BLACK, p.color)
            for s, p in b.piece_map().items() for t in b.attacks(s) if b.piece_at(t)]


def field(b):
    """kingzone, drawn: the black king's field shaded by the number of White guards; flights yellow."""
    shade = {1: '#9ec5ff', 2: '#5a9bf0', 3: '#1f5fd1'}
    out = []
    k = b.king(chess.BLACK)
    for t in list(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        n = min(len(b.attackers(chess.WHITE, t)), 3)
        mine = b.piece_at(t) and b.piece_at(t).color == chess.BLACK
        col = '#888888' if mine else ('#ffd400' if n == 0 else shade[n])
        x = 15 + chess.square_file(t) * 45
        y = 15 + (7 - chess.square_rank(t)) * 45
        out.append(f'<rect x="{x}" y="{y}" width="45" height="45" fill="{col}" opacity="0.55"/>')
        if n:
            out.append(f'<text x="{x + 40}" y="{y + 12}" font-size="11" font-family="sans-serif" font-weight="700" '
                       f'text-anchor="end" fill="#0b2a66">{n}</text>')
    x = 15 + chess.square_file(k) * 45
    y = 15 + (7 - chess.square_rank(k)) * 45
    out.append(f'<rect x="{x - 45 + 1.5}" y="{y - 45 + 1.5}" width="132" height="132" fill="none" stroke="#0b2a66" stroke-width="2.5"/>')
    return out


def svg(b, kind, size=400):
    s = re.sub(r'<desc>.*?</desc>', '', chess.svg.board(b, size=size, coordinates=True), flags=re.S)
    overlay = {'rays': rays, 'arrows': arrows, 'field': field}.get(kind)
    if kind == 'field':                       # shading goes under the pieces
        i = s.index('<use ')
        s = s[:i] + ''.join(field(b)) + s[i:]
    elif overlay:
        s = s.replace('</svg>', DEFS + ''.join(overlay(b)) + '</svg>')
    return s


def render(html, out, width, height, scale=1):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = next(iter(sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome'))), None)
        br = p.chromium.launch(executable_path=exe, args=['--no-sandbox']) if exe else p.chromium.launch(args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': width, 'height': height}, device_scale_factor=scale)
        pg.set_content(html)
        pg.screenshot(path=out, full_page=True)
        br.close()


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        sys.exit(__doc__)
    fen, out = argv[0], argv[1]
    kind = argv[2] if len(argv) > 2 else 'all'
    b = chess.Board(fen if len(fen.split()) > 1 else fen + ' w - - 0 1')
    if kind == 'all':
        cells = ''.join(f'<div style="text-align:center;font:600 18px sans-serif">{k}<br>{svg(b, k, 400)}</div>'
                        for k in ('plain', 'rays', 'arrows', 'field'))
        html = (f'<html><body style="margin:0;background:#fff"><div style="display:grid;grid-template-columns:'
                f'400px 400px;gap:16px;padding:12px">{cells}</div></body></html>')
        render(html, out, 840, 900, scale=2)
    else:
        html = f'<html><body style="margin:0;background:#fff">{svg(b, kind, 400)}</body></html>'
        render(html, out, 400, 400, scale=2)
    print(out)


if __name__ == '__main__':
    main()
