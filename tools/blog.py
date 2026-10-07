"""The daily problem blog: posts live in blog/posts/*.json, the site is generated into docs/blog/.

    python tools/blog.py build                 # render docs/blog/index.html, one page per post, feed.xml
    python tools/blog.py check "<FEN>" [#2]    # publishing gate: exit 1 on a fatal flaw or an anticipation
    python tools/blog.py next-theme            # the theme used least recently (blog/themes.json)
    python tools/blog.py stats                 # the progress table as text

Post fields (see the daily-problem skill): date, slug, title, theme, fen, stip, author, source, teaser,
solution (lines: '#Label' starts a section, two leading spaces indent a variation), comment {what, flaws,
pluses, process, lesson}, mentor_questions, mentor_issue, stats {minutes, solves, kernels, searches},
feedback (his answers, summarised by a later run), improvement (what the run changed in the kit).
"""
import sys, os, json, glob, html, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
POSTS = os.path.join(ROOT, 'blog', 'posts')
OUT = os.path.join(ROOT, 'docs', 'blog')
THEMES = os.path.join(ROOT, 'blog', 'themes.json')
SITE = 'https://evgiz0r.github.io/ChessProblemHelper/blog/'
BLOG_TITLE = 'A #2 a day'

GLYPH = {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
         'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}

def load_posts():
    posts = []
    for f in sorted(glob.glob(os.path.join(POSTS, '*.json'))):
        with open(f, encoding='utf-8') as fh:
            p = json.load(fh)
        p.setdefault('slug', os.path.splitext(os.path.basename(f))[0])
        posts.append(p)
    posts.sort(key=lambda p: (p['date'], p['slug']))
    for i, p in enumerate(posts, 1):
        p['number'] = i
    return posts

def count(fen):
    w = sum(1 for c in fen.split()[0] if c.isalpha() and c.isupper())
    b = sum(1 for c in fen.split()[0] if c.isalpha() and c.islower())
    return f'({w}+{b})'

def board_svg(fen, size=360, small=False):
    rows = fen.split()[0].split('/')
    sq = 40
    s = [f'<svg class="board{" mini" if small else ""}" viewBox="0 0 360 360" role="img" aria-label="Diagram {html.escape(fen)}">',
         '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<line x1="0" y1="0" x2="0" y2="6" stroke="var(--hatch)" stroke-width="1.6"/></pattern></defs>']
    for r, row in enumerate(rows):
        f = 0
        for ch in row:
            if ch.isdigit():
                for _ in range(int(ch)):
                    dark = (r + f) % 2 == 1
                    s.append(f'<rect x="{f*sq+20}" y="{r*sq+10}" width="{sq}" height="{sq}" fill="{"url(#hatch)" if dark else "var(--paper)"}"/>')
                    f += 1
            else:
                dark = (r + f) % 2 == 1
                s.append(f'<rect x="{f*sq+20}" y="{r*sq+10}" width="{sq}" height="{sq}" fill="{"url(#hatch)" if dark else "var(--paper)"}"/>')
                s.append(f'<text x="{f*sq+40}" y="{r*sq+41}" text-anchor="middle" font-size="32" class="pc">{GLYPH[ch]}</text>')
                f += 1
    s.append('<rect x="20" y="10" width="320" height="320" fill="none" stroke="var(--rule)" stroke-width="1.6"/>')
    if not small:
        for f in range(8):
            s.append(f'<text x="{f*sq+40}" y="348" text-anchor="middle" font-size="11" fill="var(--grey)">{"abcdefgh"[f]}</text>')
        for r in range(8):
            s.append(f'<text x="12" y="{r*sq+34}" text-anchor="middle" font-size="11" fill="var(--grey)">{8-r}</text>')
    s.append('</svg>')
    return ''.join(s)

CSS = """
:root{--paper:#fff;--ink:#000;--rule:#000;--grey:#767472;--hatch:#b9b7b4;--award:#a51c16;--tint:#f2f1ee}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#161514;--ink:#ecebe8;--rule:#ecebe8;--grey:#a19f9b;--hatch:#5d5b58;--award:#e0645c;--tint:#22211f}}
*{box-sizing:border-box} html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;font-size:17px;line-height:1.55}
.wrap{max-width:860px;margin:0 auto;padding:28px 16px 72px}
header{border-bottom:2px solid var(--rule);padding-bottom:10px;margin-bottom:26px;display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
header h1{font-size:26px;font-weight:600;margin:0} header a{color:var(--ink);text-decoration:none}
header nav{font-size:15px;color:var(--grey)} header nav a{color:var(--grey);margin-left:14px}
h2{font-size:22px;margin:0 0 4px} h3{font-size:16px;text-transform:uppercase;letter-spacing:.06em;color:var(--grey);margin:26px 0 6px;font-weight:600}
.meta{color:var(--grey);font-size:15px;margin-bottom:18px}
.tag{display:inline-block;border:1px solid var(--hatch);padding:0 8px;font-size:13px;margin-left:6px}
.cols{display:grid;grid-template-columns:minmax(260px,360px) 1fr;gap:34px;align-items:start}
@media(max-width:720px){.cols{grid-template-columns:1fr;gap:20px}}
figure{margin:0} figcaption{text-align:center;font-size:15px;line-height:1.35;margin-bottom:8px}
figcaption .who{font-weight:600}
svg.board{width:100%;height:auto;display:block}
svg.board .pc{font-family:'DejaVu Sans','Segoe UI Symbol','Apple Symbols',serif;fill:var(--ink)}
.under{display:flex;justify-content:space-between;margin-top:6px;font-size:16px}.under .count{color:var(--grey)}
.fen{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;color:var(--grey);overflow-wrap:anywhere;margin-top:6px}
details{border-top:1px solid var(--hatch);margin-top:22px;padding-top:10px}
summary{cursor:pointer;font-weight:600}
.sol{font-size:16px;margin-top:10px}.sol .sec{font:600 12px/1.4 Helvetica,Arial,sans-serif;letter-spacing:.08em;color:var(--grey);text-transform:uppercase;margin:12px 0 3px}
.sol .var{margin-left:22px}
ul{padding-left:22px} li{margin:3px 0}
.q{background:var(--tint);border-left:2px solid var(--rule);padding:10px 14px;margin-top:10px}
.list{list-style:none;padding:0;margin:0}.list li{display:grid;grid-template-columns:96px 1fr;gap:18px;align-items:center;border-bottom:1px solid var(--hatch);padding:14px 0}
.list a{color:var(--ink)} svg.mini{width:96px}
table{border-collapse:collapse;font-size:14px;width:100%} th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--hatch)} th{color:var(--grey);font-weight:600}
footer{margin-top:44px;border-top:1px solid var(--hatch);padding-top:12px;font-size:14px;color:var(--grey)} a{color:var(--ink)}
"""

def page(title, body, desc=''):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="alternate" type="application/atom+xml" title="{BLOG_TITLE}" href="feed.xml">
<style>{CSS}</style></head><body><div class="wrap">
<header><h1><a href="index.html">{BLOG_TITLE}</a></h1><nav>a twomover composed every day by an AI learning from Evgeni Bourd<a href="../">solver</a><a href="feed.xml">feed</a></nav></header>
{body}
<footer>Composed with <a href="https://github.com/evgiz0r/chessproblemhelper">ChessProblemHelper</a>: a solver, a critique taught by IM Evgeni Bourd, and a notebook of lessons. Every diagram is checked by the solver before it is published; flaws are named first.</footer>
</div></body></html>
"""

def sol_html(lines):
    out = ['<div class="sol">']
    for l in lines:
        if l.startswith('#'):
            out.append(f'<div class="sec">{html.escape(l[1:].strip())}</div>')
        elif l.startswith('  '):
            out.append(f'<div class="var">{html.escape(l.strip())}</div>')
        else:
            out.append(f'<div>{html.escape(l)}</div>')
    out.append('</div>')
    return ''.join(out)

def ul(items):
    return '<ul>' + ''.join(f'<li>{html.escape(i)}</li>' for i in items) + '</ul>' if items else '<p>None noted.</p>'

def post_html(p, prev, nxt):
    c = p.get('comment', {})
    st = p.get('stats', {})
    qs = p.get('mentor_questions', [])
    issue = p.get('mentor_issue')
    issue_link = f' <a href="https://github.com/evgiz0r/chessproblemhelper/issues/{issue}">Answer on GitHub, issue {issue}</a>.' if issue else ''
    fb = p.get('feedback', [])
    body = f"""<article>
<h2>No. {p['number']}: {html.escape(p['title'])}</h2>
<div class="meta">{p['date']}<span class="tag">{html.escape(p.get('theme_name', p.get('theme', '')))}</span></div>
<div class="cols"><div><figure><figcaption><span class="who">{html.escape(p['author'])}</span><br>{html.escape(p['source'])}</figcaption>
{board_svg(p['fen'])}<div class="under"><span>{html.escape(p['stip'].replace('#', 'Mate in ') if p['stip'] == '#2' else p['stip'])}</span><span class="count">{count(p['fen'])}</span></div>
<div class="fen">{html.escape(p['fen'])}</div></figure></div>
<div><p>{html.escape(p.get('teaser', ''))}</p>
<details><summary>Solution</summary>{sol_html(p['solution'])}</details>
<details><summary>Comment</summary>
<h3>What it is</h3><p>{html.escape(c.get('what', ''))}</p>
<h3>Flaws</h3>{ul(c.get('flaws', []))}
<h3>Pluses</h3>{ul(c.get('pluses', []))}
<h3>How it was made</h3><p>{html.escape(c.get('process', ''))}</p>
<h3>Lesson</h3><p>{html.escape(c.get('lesson', ''))}</p>
{('<h3>What changed in the kit</h3><p>' + html.escape(p['improvement']) + '</p>') if p.get('improvement') else ''}
</details>
{('<details open><summary>Questions for the mentor</summary><div class="q">' + ul(qs) + issue_link + '</div></details>') if qs else ''}
{('<details><summary>Mentor feedback</summary>' + ul(fb) + '</details>') if fb else ''}
</div></div>
<p class="meta" style="margin-top:28px">{st.get('minutes', '?')} minutes, {st.get('solves', '?')} solves, {st.get('kernels', '?')} kernels tried.
{' <a href="' + prev['slug'] + '.html">Previous</a>' if prev else ''}{' <a href="' + nxt['slug'] + '.html">Next</a>' if nxt else ''}</p>
</article>"""
    return page(f"No. {p['number']}: {p['title']}", body, p.get('teaser', ''))

def stats_rows(posts):
    rows = []
    for p in posts[-30:]:
        st = p.get('stats', {})
        rows.append((p['date'], p['number'], p.get('theme_name', p.get('theme', '')), count(p['fen']), st.get('minutes', ''),
                     st.get('solves', ''), st.get('kernels', ''), len(p.get('comment', {}).get('flaws', []))))
    return rows

def index_html(posts):
    items = ''.join(f"""<li><a href="{p['slug']}.html">{board_svg(p['fen'], small=True)}</a><div><a href="{p['slug']}.html"><b>No. {p['number']}: {html.escape(p['title'])}</b></a>
<div class="meta" style="margin:2px 0 0">{p['date']}<span class="tag">{html.escape(p.get('theme_name', p.get('theme', '')))}</span> {html.escape(p['stip'])} {count(p['fen'])}</div>
<div>{html.escape(p.get('teaser', ''))}</div></div></li>""" for p in reversed(posts))
    rows = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(x))}</td>' for x in r) + '</tr>' for r in reversed(stats_rows(posts)))
    body = f"""<p>Every day the kit picks a theme, composes an orthodox mate in two, checks it with its own solver and judge, and publishes it here with its flaws named first. Each post ends with what the day taught and the questions it raised for the mentor.</p>
<ul class="list">{items}</ul>
<h3>Progress</h3><table><tr><th>Date</th><th>No.</th><th>Theme</th><th>Units</th><th>Minutes</th><th>Solves</th><th>Kernels</th><th>Flaws named</th></tr>{rows}</table>"""
    return page(BLOG_TITLE, body, 'A chess twomover composed every day.')

def feed_xml(posts):
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    entries = ''.join(f"""<entry><title>No. {p['number']}: {html.escape(p['title'])}</title><link href="{SITE}{p['slug']}.html"/>
<id>{SITE}{p['slug']}.html</id><updated>{p['date']}T06:00:00Z</updated><summary>{html.escape(p.get('teaser', ''))}</summary></entry>""" for p in reversed(posts[-30:]))
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>{BLOG_TITLE}</title><link href="{SITE}"/><id>{SITE}</id><updated>{now}</updated>{entries}</feed>
"""

def build():
    posts = load_posts()
    os.makedirs(OUT, exist_ok=True)
    for i, p in enumerate(posts):
        with open(os.path.join(OUT, p['slug'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(post_html(p, posts[i - 1] if i else None, posts[i + 1] if i + 1 < len(posts) else None))
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html(posts))
    with open(os.path.join(OUT, 'feed.xml'), 'w', encoding='utf-8') as f:
        f.write(feed_xml(posts))
    print(f'built {len(posts)} posts into docs/blog/')

FATAL = {'unsound', 'cook', 'promoted force', 'unprovided check', 'check key'}

def check(fen, stip='#2'):
    """Publishing gate. Fatal: unsound, cooked, promoted force, unprovided check in the set play, checking
    key, a major dual (thematic variation), a major king escape in the diagram, an anticipation (the same
    position, or its mirror, in the Problemesis database or on the blog). Everything else is a warning the
    post must name among its flaws."""
    import chess
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    from chesscomp.critique import critique
    from chesscomp import db
    fen = fen.split()[0]
    p = Problem.from_fen(fen + ' w - - 0 1', stip)
    res = analyse(p, time_limit=120)
    c = critique(p, res)
    fatal, warn = [], []
    for f in c['findings']:
        line = f"[{f['rule']}] {f['msg']}"
        if f['rule'] in FATAL or (f['severity'] == 'major' and f['rule'] in ('dual', 'king escape in diagram')):
            fatal.append(line)
        elif f['severity'] in ('major', 'minor'):
            warn.append(line)
    def norm(pl):
        return '/'.join(re.sub(r'\d', lambda m: '1' * int(m.group()), r) for r in pl.split('/'))
    def mirror(pl):
        return '/'.join(r[::-1] for r in norm(pl).split('/'))
    mine = {norm(fen), mirror(fen)}
    for rec in db.records():
        if rec.get('fen') and norm(rec['fen'].split()[0]) in mine:
            fatal.append(f"[anticipation] same position as {rec['id']} ({rec.get('author')}, {rec.get('source')})")
    today = datetime.date.today().isoformat()
    for q in load_posts():
        if q['date'] != today and norm(q['fen'].split()[0]) in mine:   # today's post is the one being checked
            fatal.append(f"[repeat] already published as No. {q['number']} ({q['date']})")
    print(f"keys: {res.get('keys')}")
    for l in fatal: print('FATAL', l)
    for l in warn: print('warn ', l)
    if [f for f in c['findings'] if f['severity'] == 'plus']:
        for f in c['findings']:
            if f['severity'] == 'plus': print('plus ', f"[{f['rule']}] {f['msg']}")
    print('GATE: ' + ('FAIL' if fatal else 'PASS'))
    return 0 if not fatal else 1

def next_theme():
    themes = json.load(open(THEMES, encoding='utf-8'))['themes']
    last = {}
    for p in load_posts():
        last[p.get('theme')] = p['date']
    themes.sort(key=lambda t: (last.get(t['id'], '0000'), t.get('order', 99)))
    t = themes[0]
    print(json.dumps({**t, 'last_used': last.get(t['id'])}, indent=1, ensure_ascii=False))

def stats():
    for r in stats_rows(load_posts()):
        print(' | '.join(str(x) for x in r))

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'build': build()
    elif cmd == 'check': sys.exit(check(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '#2'))
    elif cmd == 'next-theme': next_theme()
    elif cmd == 'stats': stats()
    else: print(__doc__); sys.exit(2)
