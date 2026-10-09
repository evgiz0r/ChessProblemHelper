"""Square diagram with arrows: scheme_png.py out.png FEN "e5c4:r a5c4:r d2f3:g" "c4"  (r/g/b/y arrow colours; last arg = squares to tint)"""
import sys, re, chess, chess.svg
from playwright.sync_api import sync_playwright
out, fen = sys.argv[1], sys.argv[2]
C = {'r': '#d33c', 'g': '#2a2c', 'b': '#27dc', 'y': '#e90c'}
arrows = []
for a in (sys.argv[3].split() if len(sys.argv) > 3 else []):
    mv, col = a.split(':')
    arrows.append(chess.svg.Arrow(chess.parse_square(mv[:2]), chess.parse_square(mv[2:4]), color=C[col]))
fill = {chess.parse_square(s): '#fc06' for s in (sys.argv[4].split() if len(sys.argv) > 4 else [])}
svg = re.sub(r'<desc>.*?</desc>', '', chess.svg.board(chess.Board(fen + ' w - - 0 1'), size=720, coordinates=True, arrows=arrows, fill=fill), flags=re.S)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox']) if __import__('os').path.exists('/opt/pw-browsers/chromium') else p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 720, 'height': 720})
    pg.set_content(f'<body style="margin:0">{svg}</body>'); pg.screenshot(path=out); b.close()
print(out)
