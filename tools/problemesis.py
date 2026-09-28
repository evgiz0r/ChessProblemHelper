"""Crawl Christian Poisson's Problemesis site (christian.poisson.free.fr) and extract its problems.

Every diagram on the site sits in the same table layout: a header cell (number - author, source, award),
the diagram image whose ALT text lists the position in French notation ("Re5 Pb5 Da5 + Rc5 Pa7"), a row
with the stipulation and the piece count, optional rows for twins and fairy conditions, and a side cell
holding the solution (in a textarea's onFocus, the textarea itself, or plain HTML).

usage:
    python tools/problemesis.py crawl  MIRROR_DIR              # fetch every HTML page of the site
    python tools/problemesis.py parse  MIRROR_DIR [-o OUT]     # -> knowledge/problemesis.json
"""
import argparse, hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request
from collections import deque

HOST = 'christian.poisson.free.fr'
SEEDS = ['/', '/problemesis/problemesis.php', '/recherche/index.html',
         '/problemesis98/index98.html', '/problemesis99/index99.html', '/problemesis2000/index00.html',
         '/problemesis2001/index01.html', '/problemesis2002/', '/problemesis2003/', '/problemesis2004/',
         '/problemesis2005/']
SKIP = re.compile(r'\.(gif|jpe?g|png|bmp|ico|css|js|pdf|epub|zip|exe|mp3|ttf|doc)$|download\.php|xiti', re.I)
FR2EN = {'R': 'K', 'D': 'Q', 'T': 'R', 'F': 'B', 'C': 'S', 'P': 'P'}


# ---------------------------------------------------------------- crawl

def crawl(out, delay=0.05):
    seen, queue = set(), deque('http://' + HOST + s for s in SEEDS)
    while queue:
        url = urllib.parse.urldefrag(queue.popleft())[0]
        if url in seen:
            continue
        seen.add(url)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                if 'html' not in r.headers.get('Content-Type', 'text/html'):
                    continue
                body = r.read()
        except Exception as e:
            print('skip', url, e, file=sys.stderr)
            continue
        path = urllib.parse.urlparse(url).path
        path = path + 'index.html' if path.endswith('/') else path
        dest = os.path.join(out, path.lstrip('/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as f:
            f.write(body)
        text = body.decode('latin-1')
        for link in re.findall(r"""(?:href|src)\s*=\s*["']?([^"'\s>]+)|['"]([^'"\s]+\.html?)['"]""", text, re.I):
            link = link[0] or link[1]
            nxt = urllib.parse.urljoin(url, link)
            p = urllib.parse.urlparse(nxt)
            if p.scheme == 'http' and p.netloc == HOST and not SKIP.search(p.path):
                queue.append(nxt)
        time.sleep(delay)
    print(len(seen), 'urls visited', file=sys.stderr)


# ---------------------------------------------------------------- parse

def text_of(fragment):
    t = re.sub(r'<script.*?</script>', '', fragment, flags=re.S | re.I)
    t = re.sub(r'\s+', ' ', t)                        # source line breaks are not text line breaks
    t = re.sub(r'<br\s*/?>|<p\b[^>]*>|</div>|</td>|\x00', '\n', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    t = t.replace('\x85', '…').replace('\x87', '‡').replace('\xd7', '×')
    lines = [re.sub(r'[ \t\r\xa0]+', ' ', l).strip() for l in t.split('\n')]
    return '\n'.join(l for l in lines if l)


def english(s):
    """French solution notation -> English (K Q R B S), '#' for mate, 'x' for captures."""
    s = s.replace('‡', '#').replace('…', '...').replace('×', 'x').replace('®', '->')
    s = re.sub(r'(?<![A-Za-z])([RDTFC])(?=[a-h]?[1-8]?x?[a-h][1-8])', lambda m: FR2EN[m.group(1)], s)
    s = re.sub(r'=([DTFC])\b', lambda m: '=' + FR2EN[m.group(1)], s)
    return s


def stipulation(s):
    return re.sub(r'\s+', ' ', s.replace('‡', '#')).strip()


def to_fen(alt):
    """ALT text 'Re5 Pb5 + Rc5 Pa7' -> FEN, or None if it is not an orthodox 8x8 position."""
    if alt.count('+') != 1:
        return None
    board = {}
    for colour, side in zip((str.upper, str.lower), alt.split('+')):
        for tok in side.split():
            m = re.fullmatch(r'([RDTFCP])([a-h])([1-8])', tok)
            if not m:
                return None
            sq = (m.group(2), int(m.group(3)))
            if sq in board:
                return None
            board[sq] = colour(FR2EN[m.group(1)].replace('S', 'N'))
    if sorted(p for p in board.values() if p in 'Kk') != ['K', 'k']:
        return None
    rows = []
    for rank in range(8, 0, -1):
        row, empty = '', 0
        for f in 'abcdefgh':
            p = board.get((f, rank))
            if p:
                row += (str(empty) if empty else '') + p
                empty = 0
            else:
                empty += 1
        rows.append(row + (str(empty) if empty else ''))
    return '/'.join(rows)


def solution_of(block):
    m = re.search(r'onFocus\s*=\s*"this\.value=\'(.*?)\'"', block, re.S | re.I)
    if m:
        return text_of(m.group(1).replace('\\n', '\x00').replace("\\'", "'"))
    m = re.search(r'<textarea[^>]*>(.*?)</textarea', block, re.S | re.I)
    if m and 'cliquer ici' not in m.group(1):
        return text_of(m.group(1).replace('\n', '\x00'))
    # inline: the rowspan cell that is not the header
    for c in re.findall(r'<td[^>]*rowspan\s*=\s*"?4"?[^>]*>(.*?)</td>', block, re.S | re.I):
        t = text_of(c)
        if t and re.search(r'\d\.', t):
            return t
    return None


NAME = re.compile(r"[A-Z][\w'.-]*( [\w'.-]+)* [A-ZÉÈÖÜÄ][A-ZÉÈÖÜÄ'-]+( [A-ZÉÈÖÜÄ'-]+)*")
PLAY = re.compile(r'[\d.]+\.*( \+ [\d.]+\.*)?|\d+ solutions?')
TWIN = re.compile(r'[a-z]\) ')
SIMPLE_TWIN = re.compile(r'[a-z]\) (=[a-z]\)|[-+]?[wb]?[KQRBSP][a-h][1-8]( ?(->|-) ?[a-h][1-8])?[ ,]*)+$')


def parse_block(block):
    alt = re.search(r'<img[^>]*\balt\s*=\s*"([^"]*\+[^"]*)"', block, re.S | re.I)
    if not alt:
        return None
    alt_text = ' '.join(alt.group(1).split())
    head = re.search(r'<td[^>]*colspan\s*=\s*"?2"?[^>]*>(.*?)</td>', block, re.S | re.I)
    head_lines = text_of(head.group(1)).split('\n') if head and 'img' not in head.group(1).lower() else []
    rows = [text_of(r) for r in re.findall(r'<tr[^>]*>(.*?)</tr>', block[alt.end():], re.S | re.I)]
    stip, count, extra = None, None, []
    for r in filter(None, rows):
        m = re.search(r'\((\d+\s*\+\s*\d+(?:\s*\+\s*\d+)?)\)', r)
        if stip is None and m:
            stip = stipulation(r[:m.start()])
            count = m.group(1).replace(' ', '')
            extra += r[m.end():].replace('C+', '').replace('C-', '').split('\n')
        elif stip is not None:
            extra += r.split('\n')
    extra = [e.strip() for e in extra if e.strip()]
    play = [e for e in extra if PLAY.fullmatch(e)]
    twins = [english(e) for e in extra if TWIN.match(e) and e not in play]
    conditions = [e for e in extra if e not in play and not TWIN.match(e)]
    rec = {'position': alt_text, 'fen': to_fen(alt_text), 'stip': stip, 'count': count}
    if head_lines:
        m = re.match(r'([A-Z]{0,3}\d+[a-z]?)\s*[-–]\s*(.+)', head_lines[0])
        rec['number'], authors = (m.group(1), [m.group(2)]) if m else (None, [head_lines[0]])
        rest = head_lines[1:]
        while rest and NAME.fullmatch(rest[0]):     # joint authors, one per line
            authors.append(rest.pop(0))
        rec['author'] = ' & '.join(authors)
        rec['source'] = '\n'.join(rest) or None
    if play:
        rec['play'] = ' '.join(play)
    if twins:
        rec['twins'] = twins
    if conditions:
        rec['conditions'] = conditions
    sol = solution_of(block)
    if sol:
        rec['solution_fr'] = sol
        rec['solution'] = english(sol)
    rec['orthodox'] = bool(rec['fen']) and not conditions and all(SIMPLE_TWIN.match(t) for t in twins)
    return rec


def parse(mirror):
    out = []
    for root, dirs, files in os.walk(mirror):
        dirs.sort()
        for fn in sorted(files):
            if not re.search(r'\.(html?|php)$', fn):
                continue
            path = os.path.join(root, fn)
            page = open(path, encoding='latin-1').read()
            rel = os.path.relpath(path, mirror).replace(os.sep, '/')
            title = re.search(r'<title>(.*?)</title>', page, re.S | re.I)
            title = text_of(title.group(1)) if title else ''
            blocks = re.split(r'<table\s+cellpadding\s*=\s*"?0"?\s*>', page, flags=re.I)[1:]
            for b in blocks:
                b = re.split(r'</table>', b, flags=re.I)[0]
                rec = parse_block(b)
                if rec:
                    rec['page'] = 'http://' + HOST + '/' + rel.split(HOST + '/')[-1]
                    rec['page_title'] = title
                    out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'parse'])
    ap.add_argument('mirror')
    ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'problemesis.json'))
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.mirror)
        return
    recs = parse(a.mirror)
    seen, uniq = {}, []
    for r in recs:                       # the same diagram is often repeated on comment/award pages
        key = '|'.join((r['position'], r['stip'] or '', str(r.get('twins')), str(r.get('conditions'))))
        if key in seen:
            first = seen[key]
            first['pages'].append(r['page'])
            for k in ('solution', 'solution_fr', 'number', 'source'):   # fill gaps from the repeat
                if not first.get(k) and r.get(k):
                    first[k] = r[k]
            continue
        r = {'id': 'psis-' + hashlib.sha1(key.encode()).hexdigest()[:10], **r, 'pages': [r.pop('page')]}
        seen[key] = r
        uniq.append(r)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump({'source': 'http://' + HOST + '/', 'note': 'Problems extracted from the Problemesis web '
                   'magazine (C. Poisson). Positions, stipulations and solutions are converted to English '
                   'notation; solution_fr keeps the original.', 'count': len(uniq), 'problems': uniq},
                  f, ensure_ascii=False, indent=1)
    orth = [r for r in uniq if r['orthodox']]
    print(f'{len(recs)} diagrams, {len(uniq)} unique, {len(orth)} orthodox, '
          f'{sum(1 for r in uniq if r.get("solution"))} with solution -> {a.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
