"""Problem card: diagram + author/source + a clean solution, as PNG (Playwright/Chromium).

    python tools/card_png.py out.png < spec.json
    python tools/card_png.py out.png --id psis-8687c07e99      # card from a database record, printed solution

spec: {"fen", "author", "source", "stip", "count", "lines": [...]}; a line starting with '#' is a section
label (TRIES, KEY, THEMES), a line starting with two spaces is an indented variation."""
import sys, json, re, html, chess, chess.svg
from playwright.sync_api import sync_playwright
out = sys.argv[1]
if len(sys.argv) > 3 and sys.argv[2] == '--id':
    sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
    from chesscomp import db
    r = db.get(sys.argv[3])
    lines, sec = [], None
    for l in (r.get('solution') or '').split('\n'):
        l = l.strip()
        if not l: continue
        if re.match(r'1\.[^.]', l) and l.endswith('?') or re.match(r'1\.\S+\?', l):
            if sec != 'Tries': lines.append('#Tries'); sec = 'Tries'
            lines.append(l.replace('[', '(').replace(']', ')'))
        elif re.match(r'1\.\S+!', l):
            if sec != 'Key': lines.append('#Key'); sec = 'Key'
            lines.append(l.replace('[', '(').replace(']', ')'))
        elif l.startswith('1...') or l.startswith('mais') or l.startswith('('):
            lines.append('  ' + l.replace('mais', 'but'))
        else:
            if sec != 'Themes': lines.append('#Themes'); sec = 'Themes'
            lines.append(l.split(' - ')[-1])
    spec = {'fen': r['fen'], 'author': r['author'], 'source': r['source'].replace('\n', ', '), 'stip': r['stip'],
            'count': r['count'], 'lines': lines}
else:
    spec = json.load(sys.stdin)
b = chess.Board(spec['fen'] + ' w - - 0 1')
svg = re.sub(r'<desc>.*?</desc>', '', chess.svg.board(b, size=360, coordinates=True), flags=re.S)
rows = []
for l in spec['lines']:
    if l.startswith('#'):
        rows.append(f'<div class="sec">{html.escape(l[1:].strip())}</div>')
    elif l.startswith('  '):
        rows.append(f'<div class="var">{html.escape(l.strip())}</div>')
    else:
        rows.append(f'<div class="main">{html.escape(l)}</div>')
page = f'''<html><body style="margin:0;background:#fff;font-family:Georgia,serif">
<div id="c" style="display:flex;gap:22px;padding:14px;width:760px;box-sizing:border-box">
 <div style="flex:none"><div style="width:360px;height:360px">{svg}</div>
  <div style="font:13px Georgia;color:#333;margin-top:6px;text-align:center">{html.escape(spec.get('stip','#2'))} &nbsp; ({html.escape(spec.get('count',''))})</div></div>
 <div style="flex:1;min-width:0">
  <div style="font:bold 17px Georgia;margin-top:4px">{html.escape(spec['author'])}</div>
  <div style="font:13px Georgia;color:#555;margin-bottom:12px">{html.escape(spec['source'])}</div>
  <style>.sec{{font:bold 12px Helvetica,Arial;letter-spacing:.08em;color:#777;text-transform:uppercase;margin:10px 0 3px}}
  .main{{font:15px Georgia;margin:2px 0}} .var{{font:15px Georgia;margin:2px 0 2px 18px;color:#222}}</style>
  {''.join(rows)}
 </div></div></body></html>'''
with sync_playwright() as p:
    import glob
    exe = next(iter(sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome'))), None)  # web-session Chromium
    br = p.chromium.launch(executable_path=exe, args=['--no-sandbox']) if exe else p.chromium.launch(args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 780, 'height': 420}, device_scale_factor=2)
    pg.set_content(page); pg.wait_for_timeout(300)
    pg.locator('#c').screenshot(path=out); br.close()
print(out)
