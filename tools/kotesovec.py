"""Crawl Vaclav Kotesovec's site (www.kotesovec.cz, HTTP only) and extract the chess problems in its HTML articles.

The site is a frameset (content.htm + index0.htm) linking to ~350 HTML articles. Problems appear in two layouts:

  * GIF diagrams (circe.htm, onlyg.htm, bauertn.htm, hppopeye.htm, ...): a <td width=220> cell holding the header
    (<b>number - author</b>, <small>source/award</small>), a table bgcolor=#404040 whose rows are little GIFs
    (80.gif = 8 empty squares, bp1.gif = white pawn on a light square, cc0.gif = black grasshopper ...; b = white,
    c = black; k d v s j p = K Q R B S P in Czech; c t l n f = fairy glyphs whose identity the caption gives,
    e.g. "Lion LIf7/LIb4,d4,h4"), then two 160-px tables (stipulation | condition | (w+b); C+ | twin/label) and a
    <td width=400> with the solution (German or Czech figurines, often Popeye output) and commentary.
  * py2web articles (py2web/*.htm): <div class="p2w-diagram">white Kd1 QFa8a4h1 / black ...</div> in Popeye piece
    codes, caption lines below it, and <div class="p2w-solution"> with the Popeye solution.

  * PDF books and awards (books/*.pdf, awards/, souteze/, riface/, ...): diagrams typed in a chess font - Poisson's
    4Echecs in the Word books (U+F0xx code points), the same font mapped to Latin-1 in the InDesign awards of
    Phénix, or Steve Smith's Linares fonts. See the PDF section below. Needs pypdf (optional import; without it
    `parse` stops with a hint, `parse --no-pdf` skips the PDFs).

Diagrams drawn as a single picture (gustav/*.htm, end2008, fairyend, ...) are not parsed.

usage:
    python tools/kotesovec.py crawl  MIRROR_DIR [--pdfs]     # fetch every HTML page (and the PDFs), 1 req/s
    python tools/kotesovec.py parse  MIRROR_DIR [-o OUT] [--no-pdf]   # -> knowledge/kotesovec.json (PDFs need pypdf)
"""
import argparse, gzip, html, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import deque

HOST = 'www.kotesovec.cz'
HOSTS = {HOST, 'kotesovec.cz'}
SEEDS = ['/', '/content.htm', '/index0.htm', '/links0.htm', '/old_news.htm', '/articles.htm']
UA = 'ChessProblemHelper-crawler/1.0 (chess-problem research mirror; polite, 1 req/s)'
SKIP = re.compile(r'\.(gif|jpe?g|png|bmp|ico|css|js|pdf|zip|exe|mp3|ttf|doc|docx|xls|rar|7z|gz|avi|mp4|'
                  r'wmv|mov|tif|nb|cbv|pgn|txt)$', re.I)
# math section: no chess problems there
SKIP_PATH = re.compile(r'^/(math|math_articles|recepty|photos?|best_photos|abstract)\b|^/math\w*\.htm', re.I)


# ---------------------------------------------------------------- crawl

def local_path(out, url):
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path).replace('\\', '/')
    path = path + 'index.html' if path.endswith('/') or not path else path
    dest = os.path.join(out, path.lstrip('/'))
    return os.path.join(dest, 'index.html') if os.path.isdir(dest) else dest


class OnHostRedirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects only within the site; an off-host redirect is reported and not followed."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlparse(newurl).netloc not in HOSTS:
            raise urllib.error.URLError('off-host redirect to ' + newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def crawl(out, delay=1.0):
    opener = urllib.request.build_opener(OnHostRedirects)
    seen, queue, fetched, skipped = set(), deque('http://' + HOST + s for s in SEEDS), 0, []
    while queue:
        url = urllib.parse.urldefrag(queue.popleft())[0]
        url = url.replace('://kotesovec.cz', '://' + HOST).replace('\\', '/')
        if urllib.parse.urlparse(url).path == '':
            url += '/'
        if url in seen:
            continue
        seen.add(url)
        dest = local_path(out, url)
        if os.path.isfile(dest):                     # resumable: reuse what an earlier run fetched
            body = open(dest, 'rb').read()
        else:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': UA})
                with opener.open(req, timeout=30) as r:
                    ctype = r.headers.get('Content-Type', 'text/html')
                    body = r.read() if 'html' in ctype else None
            except Exception as e:
                print('skip', url, e, file=sys.stderr)
                skipped.append(url)
                time.sleep(delay)
                continue
            time.sleep(delay)
            if body is None:
                continue
            fetched += 1
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(body)
            if fetched % 50 == 0:
                print(fetched, 'fetched,', len(queue), 'queued', file=sys.stderr)
        text = body.decode('cp1250', 'replace')
        for link in re.findall(r"""(?:href|src)\s*=\s*["']?([^"'\s>]+)""", text, re.I):
            nxt = urllib.parse.urljoin(url, link.strip().replace('\\', '/'))
            p = urllib.parse.urlparse(nxt)
            if p.scheme == 'http' and p.netloc in HOSTS and not SKIP.search(p.path) \
                    and not SKIP_PATH.search(p.path) and not p.query:
                queue.append(nxt)
    print(f'{len(seen)} urls visited, {fetched} newly fetched, {len(skipped)} failed', file=sys.stderr)


def fetch_pdfs(out, delay=1.0):
    """Download the on-host PDFs linked from the mirrored pages (books, awards; not the maths ones), 1 req/s."""
    opener = urllib.request.build_opener(OnHostRedirects)
    urls = {'http://' + HOST + p for p in PDF_EXTRA}
    for root, _, files in os.walk(out):
        for fn in files:
            if not re.search(r'\.html?$', fn, re.I):
                continue
            rel = os.path.relpath(os.path.join(root, fn), out).replace(os.sep, '/')
            text = open(os.path.join(root, fn), 'rb').read().decode('cp1250', 'replace')
            for link in re.findall(r"""href\s*=\s*["']?([^"'>]+?\.pdf)\b""", text, re.I):
                u = urllib.parse.urljoin('http://' + HOST + '/' + rel, link.strip().replace('\\', '/'))
                p = urllib.parse.urlparse(u)
                if p.netloc in HOSTS and not PDF_SKIP.search(p.path):
                    urls.add('http://' + HOST + p.path)
    got = 0
    for u in sorted(urls):
        dest = local_path(out, u)
        if os.path.isfile(dest):
            continue
        try:
            req = urllib.request.Request(u, headers={'User-Agent': UA})
            with opener.open(req, timeout=120) as r:
                body = r.read()
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(body)
            got += 1
        except Exception as e:
            print('skip', u, e, file=sys.stderr)
        time.sleep(delay)
    print(f'{len(urls)} PDFs linked, {got} downloaded', file=sys.stderr)


# ---------------------------------------------------------------- parse

EN = 'KQRBSP'
GIF_PIECE = {'k': 'K', 'd': 'Q', 'v': 'R', 's': 'B', 'j': 'S', 'p': 'P',       # Czech: kral dama vez strelec jezdec pesec
             'c': 'G', 't': 'N', 'l': 'LI', 'n': 'UU', 'f': 'BH'}             # fairy glyphs; the caption names the real piece
# fairy piece names (English / German / Czech) -> Popeye-style codes
FAIRY = {'grasshopper': 'G', 'grashupfer': 'G', 'grashuepfer': 'G', 'cvrcek': 'G', 'nightrider': 'N', 'nachtreiter': 'N',
         'tatos': 'N', 'nightriderhopper': 'NH', 'nachtreiterhupfer': 'NH', 'lion': 'LI', 'equihopper': 'EQ',
         'ubi-ubi': 'UU', 'pao': 'PA', 'vao': 'VA', 'leo': 'LE', 'mao': 'MA', 'moa': 'MO', 'rookhopper': 'RH',
         'bishophopper': 'BH', 'kangaroo': 'KA', 'zebra': 'Z', 'camel': 'C', 'giraffe': 'GI', 'amazon': 'AM',
         'empress': 'EM', 'princess': 'PR', 'locust': 'L', 'rook-locust': 'LR', 'bishop-locust': 'LB',
         'equistopper': 'QF', 'wazir': 'W', 'fers': 'F', 'alfil': 'A', 'dabbaba': 'D', 'mooses': 'MO', 'moose': 'MO',
         'eagle': 'EA', 'sparrow': 'SP', 'rose': 'RO', 'antelope': 'AN', 'bison': 'BI', 'gnu': 'GN', 'okapi': 'OK',
         'rookrider': 'RR', 'lance': 'LA', 'vizir': 'W', 'contragrasshopper': 'CG', 'dragon': 'DR', 'orphan': 'OR',
         'friend': 'FR', 'imitator': 'I', 'andernach': None}
POPEYE_NAME = {'G': 'Grasshopper', 'N': 'Nightrider', 'NH': 'Nightriderhopper', 'LI': 'Lion', 'EQ': 'Equihopper',
               'UU': 'Ubi-Ubi', 'PA': 'Pao', 'VA': 'Vao', 'LE': 'Leo', 'MA': 'Mao', 'MO': 'Moa', 'RH': 'Rookhopper',
               'BH': 'Bishophopper', 'KA': 'Kangaroo', 'Z': 'Zebra', 'C': 'Camel', 'GI': 'Giraffe', 'AM': 'Amazon',
               'EM': 'Empress', 'PR': 'Princess', 'L': 'Locust', 'LR': 'Rook-Locust', 'LB': 'Bishop-Locust',
               'QF': 'Non-stop Equistopper', 'W': 'Wazir', 'WE': 'Wazir', 'F': 'Fers', 'EA': 'Eagle',
               'SP': 'Sparrow', 'RO': 'Rose', 'AN': 'Antelope', 'CA': 'Camel', 'ZE': 'Zebra', 'I': 'Imitator'}
ORDER = {p: i for i, p in enumerate(EN)}
SQ = re.compile(r'[a-h][1-8]')


def text_of(fragment):
    t = re.sub(r'<script.*?</script>', '', fragment, flags=re.S | re.I)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'<br\s*/?>|<p\b[^>]*>|</p>|</div>|</td>|</tr>|<hr[^>]*>|<li>|</?h\d[^>]*>|\x00', '\n', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    lines = [re.sub(r'[ \t\r\xa0]+', ' ', l).strip() for l in t.split('\n')]
    return '\n'.join(l for l in lines if l)


def ascii_fold(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def english(s, pieces=None):
    """German (K D T L S) or Czech (K D V S J) figurine letters -> English (K Q R B S); ':' and '*' -> 'x'.
    `pieces` (the codes on the board) settles the S = knight / S = bishop ambiguity of a solution without V, J, T, L."""
    mv = r'(?=[a-h]?[1-8]?[:x*-]?[a-h][1-8])'
    czech = re.search(r'(?<![A-Za-z])[VJ]' + mv, s) or (
        pieces is not None and 'S' not in pieces and 'B' in pieces and re.search(r'(?<![A-Za-z])S' + mv, s))
    german = re.search(r'(?<![A-Za-z])[TL]' + mv, s) or re.search(r'[a-h][18]=?[TL]\b', s)
    table = ({'D': 'Q', 'V': 'R', 'S': 'B', 'J': 'S'} if czech and not german else
             {'D': 'Q', 'T': 'R', 'L': 'B'} if german or re.search(r'(?<![A-Za-z])D' + mv, s) else {})
    if table:
        keys = ''.join(table)
        s = re.sub(r'(?<![A-Za-z])([%s])%s' % (keys, mv), lambda m: table[m.group(1)], s)
        s = re.sub(r'(?<=[a-h][18])(=?)([%s])(?![A-Za-z])' % keys, lambda m: m.group(1) + table[m.group(2)], s)
    s = re.sub(r'(?<=[A-Za-z1-8]):(?=[a-h][1-8])', 'x', s)
    s = re.sub(r'(?<=[A-Za-z1-8])\*(?=[a-h][1-8])', 'x', s)
    return s


def stipulation(s):
    s = re.sub(r'\s+', ' ', s.replace('‡', '#')).strip()
    s = re.sub(r'=\s+=', '==', s)
    return re.sub(r'^([A-Za-z-]+)(?=[#=!+])', lambda m: m.group(1).lower(), s)


def fairy_code(name):
    n = ascii_fold(name).lower().replace('nonstop ', '').replace('non-stop ', '')
    for w in (n, n.split()[-1] if n.split() else n):
        for cand in (w, w[:-1] if w.endswith('s') else w, w[:-2] if w.endswith('es') else w):
            if cand in FAIRY:
                return FAIRY[cand]
    return None


def fairy_specs(text):
    """'Lion LIf7/LIb4,d4,h4', 'Nightriders c2,g8' -> {square: code}."""
    out = {}
    for m in re.finditer(r"([A-Za-zÀ-ž][\wÀ-ž'-]*(?: [A-Za-z][\w-]*)?)\s+"
                         r"((?:[A-Z]{0,2}[a-h][1-8](?:\s*[,/]\s*|\s+(?=[A-Z]{0,2}[a-h][1-8]))?)+)", text):
        code = fairy_code(m.group(1))
        if code is None:
            explicit = re.match(r'([A-Z]{1,2})[a-h][1-8]', m.group(2))
            if not explicit or explicit.group(1) in EN:
                continue
            code = explicit.group(1)
        for sq in SQ.findall(m.group(2)):
            out[sq] = code
    return out


def position_str(board, files=8):
    """board {(file, rank): (colour, code)} -> 'Ke1 Qd1 Ga3 + Ke8 Pa7' (white + black [+ neutral])."""
    groups = []
    for colour in 'wbn':
        pcs = sorted(((ORDER.get(c, 9), c, f, r) for (f, r), (col, c) in board.items() if col == colour),
                     key=lambda x: (x[0], x[1], -x[3], x[2]))
        if colour != 'n' or pcs:
            groups.append(' '.join('%s%s%d' % (c, 'abcdefghijklmnop'[f], r) for _, c, f, r in pcs) or '-')
    return ' + '.join(groups)


def to_fen(board, width=8, height=8):
    if width != 8 or height != 8 or any(c not in EN or col == 'n' for col, c in board.values()):
        return None
    kings = sorted(c if col == 'w' else c.lower() for col, c in board.values() if c == 'K')
    if kings != ['K', 'k']:
        return None
    rows = []
    for rank in range(8, 0, -1):
        row, empty = '', 0
        for f in range(8):
            p = board.get((f, rank))
            if p:
                ch = p[1].replace('S', 'N')
                row += (str(empty) if empty else '') + (ch if p[0] == 'w' else ch.lower())
                empty = 0
            else:
                empty += 1
        rows.append(row + (str(empty) if empty else ''))
    return '/'.join(rows)


# --- solution text: split move lines from commentary / program output

NOISE = re.compile(r'moegliche Stellungen|Loesung beendet|solution finished|Zeit\s*=|^Popeye|^time\s*=|'
                   r'potential positions|^\(?Time', re.I)
MOVE_LINE = re.compile(r'^(?:[a-z]\)\s*|[A-Z]\)\s*|\d+\.\s*\.{0,3}\s*[A-Za-z]|\d+\.\.\.|set:|try:|key:)|'
                       r'\b\d+\.\s*[A-Z]{0,2}[a-h]?[1-8]?[-:x*]?[a-h][1-8]', re.I)


def split_solution(txt):
    sol, com = [], []
    for line in txt.split('\n'):
        if NOISE.search(line):
            continue
        moves = len(re.findall(r'\b\d+\.(?:\.\.)?\s*[A-Z]{0,2}[a-h]?[1-8]?[-:x*]?[a-h][1-8]', line))
        words = len(re.findall(r'[a-zA-ZÀ-ž]{4,}', line))
        (sol if moves and moves >= words / 3 else com).append(line)
    return '\n'.join(sol), '\n'.join(com)


AWARD = re.compile(r'^((?:\d+\.?\s*(?:-\s*\d+\.?\s*)?)?(?:spec(?:ial)?\.?\s*|sp\.\s*|ehr\.?\s*|comm\.?\s*)?'
                   r'(?:Pr(?:ize|eis)?\b\.?|H\.?\s?M\b\.?|Hon\.?\s*Mention|Comm(?:endation)?\b\.?|C\b\.|Lob\b\.?|'
                   r'Place\b|pl\.|ehr\.?\s*Erw\.?|Erw\.?|Special Prize|Recommended|Commended|cena|Mention)'
                   r'(?:\s*\([^)]*\))?)\s*', re.I)


def split_source(src):
    if not src:
        return None, None
    m = AWARD.match(src)
    if m and len(m.group(1)) > 1:
        return src[m.end():].strip() or None, m.group(1).strip()
    return src, None


def classify_extra(items, rec):
    """Sort caption items into play spec, twins, correctness, fairy conditions."""
    play, twins, conds = [], [], []
    for e in items:
        e = e.strip(' ,')
        if not e or e in ('*', '-'):
            continue
        if re.fullmatch(r'C[+-]!?|C\?|cooked!?|COOKED!?|C\+ \(.*\)', e):
            rec['test'] = e
        elif re.fullmatch(r'(?:\d+\.)+\.\.(?:\.)?|\d+ (?:solutions?|Lösungen|řešení)|\d+\.\d+\.\.\.', e):
            play.append(e)
        elif re.match(r'[a-h]\)\s', e) or re.match(r'[b-z]\)', e):
            twins.append(english(e))
        elif re.fullmatch(r'[A-Z]{1,3}\d+[A-Za-z]?', e):
            rec.setdefault('number', e)
        else:
            m = re.match(r'((?:\d+\.)+\.\.(?:\.)?)\s+(.+)', e)
            if m:
                play.append(m.group(1))
                e = m.group(2)
            conds.append(e)
    if play:
        rec['play'] = ' '.join(play)
    if twins:
        rec['twins'] = twins
    return conds


SIMPLE_TWIN = re.compile(r'[a-z]\) *(=[a-z]\)|[-+]?[wb]?[KQRBSP]?[a-h][1-8]( ?(->|-|>) ?[a-h][1-8])?[ ,]*)+$')


def finish(rec, board, conds, width=8, height=8):
    specs = {}
    for c in conds:
        specs.update(fairy_specs(c))
    for (f, r), (col, code) in list(board.items()):
        sq = 'abcdefgh'[f] + str(r) if f < 8 and r <= 8 else None
        if sq in specs and code not in 'KP':
            board[(f, r)] = (col, specs[sq])
    fairy = sorted({c for _, c in board.values() if c not in EN})
    rec['position'] = position_str(board)
    rec['fen'] = to_fen(board, width, height)
    for c in fairy:                                  # name the fairy pieces unless the caption already does
        nm = POPEYE_NAME.get(c, c)
        if not any(nm.lower().split()[-1][:6] in ascii_fold(x).lower() for x in conds) and \
                not any(fairy_code(w) == c for x in conds for w in re.findall(r'[\w-]+', x)):
            conds.append('%s=%s' % (c, nm))
    if width != 8 or height != 8:
        conds.append('board %dx%d' % (width, height))
    if conds:
        rec['conditions'] = conds
    stip = rec.get('stip') or ''
    # any orthodox goal (# = +) with an orthodox aim prefix; '==' (double stalemate) and '!' (auto-) are fairy aims
    orth_stip = re.fullmatch(r'(?:ser-|pser-)?[a-z]{0,3}-?[#=+]\d+(?:[.,]\d)?|[#=+]\d*', stip.replace(' ', '')) is not None
    rec['orthodox'] = bool(rec['fen']) and not conds and orth_stip and \
        all(SIMPLE_TWIN.match(t) for t in rec.get('twins', []))
    return rec


# --- format 1: diagrams drawn from little GIFs (80.gif = 8 empty squares, bp1.gif = white pawn on a light square ...)

GIF = re.compile(r'<img\s+src\s*=\s*"?(?:[\w./]*/)?(\d{1,2}|[bcn][a-z])([01])\.gif"?[^>]*>|<br\s*/?>', re.I)


def gif_board(table):
    rows, row = [], []
    for m in GIF.finditer(table):
        if m.group(0).lower().startswith('<br'):
            if row:
                rows.append(row)
            row = []
        elif m.group(1).isdigit():
            row += [None] * int(m.group(1))
        else:
            row.append(m.group(1).lower())
    if row:
        rows.append(row)
    if not rows:
        return None
    width = max(len(r) for r in rows)
    if any(len(r) != width for r in rows):
        return None
    board = {}
    for i, r in enumerate(rows):
        rank = len(rows) - i
        for f, p in enumerate(r):
            if p:
                board[(f, rank)] = ({'b': 'w', 'c': 'b', 'n': 'n'}[p[0]], GIF_PIECE.get(p[1], p[1].upper()))
    return board, width, len(rows)


def parse_gif_diagrams(page):
    recs = []
    starts = [m.start() for m in re.finditer(r'<table\b[^>]*bgcolor\s*=\s*"?#404040', page, re.I)]
    for n, k in enumerate(starts):
        end_board = page.lower().find('</table>', k)
        got = gif_board(page[k:end_board])
        if not got:
            continue
        board, width, height = got
        td = page.rfind('<td', 0, k)
        head = page[td:k]
        head = head[re.search(r'<td[^>]*>', head).end():] if re.search(r'<td[^>]*>', head) else head
        nxt = starts[n + 1] if n + 1 < len(starts) else len(page)
        tail = page[end_board + 8:nxt]
        cut = re.search(r'<hr|<table\s+cellpadding', tail, re.I)
        tail = tail[:cut.start()] if cut else tail
        infos = re.findall(r'<table\s+width\s*=\s*"?160"?[^>]*>(.*?)</table>', tail[:4000], re.S | re.I)[:2]
        cells = [[text_of(c).replace('\n', ' ') for c in re.findall(r'<td[^>]*>(.*?)</td>', t, re.S | re.I)]
                 for t in infos]
        stip = cells[0][0] if cells and cells[0] else ''
        if not stip and cells and len(cells[0]) > 1:           # studies: 'white wins' / 'draw' in the middle cell
            mid = ascii_fold(cells[0][1]).lower()
            stip = '+' if re.search(r'white wins|bily vyhraje|weiss gewinnt|^\+$', mid) else \
                '=' if re.search(r'draw|remiza|remis|^=$', mid) else ''
            if stip:
                cells[0][1] = ''
        if not stip or not re.search(r'[#=+]|\d', stip):
            continue                                        # an illustration (e.g. final position), not a problem
        rec = {}
        hl = [l for l in text_of(head).split('\n') if l]
        bold = re.search(r'<b>(.*?)</b>', head, re.S | re.I)
        small = re.findall(r'<small>(.*?)</small>', head, re.S | re.I)
        if bold:
            a = text_of(bold.group(1)).replace('\n', ' ')
            m = re.match(r'([A-Z]{0,3}\d+[A-Za-z]{0,2})\s+[-–]\s+(.+)', a)
            if m:
                rec['number'], a = m.group(1), m.group(2)
            m = re.match(r'(.*?)\s*(\(.*\))$', a)
            if m and m.group(1):
                a, rec['author_note'] = m.group(1), m.group(2)
            rec['author'] = re.sub(r'\s*\+\s*', ' & ', a)
            src = ' '.join(text_of(s).replace('\n', ' ') for s in small) or None
        else:
            src = ' '.join(hl) or None
        rec['source'], award = split_source(src)
        if award:
            rec['award'] = award
        rec['stip'] = stipulation(stip)
        cnt = cells[0][-1] if cells and len(cells[0]) > 1 else ''
        m = re.search(r'\((\d+\s*\+\s*\d+(?:\s*\+\s*\d+)?)\)', cnt)
        rec['count'] = m.group(1).replace(' ', '') if m else None
        items = []
        for row in cells:
            for c in row[1:] if row is cells[0] else row:
                if c and not re.fullmatch(r'\(\d+\s*\+\s*\d+(?:\s*\+\s*\d+)?\)', c):
                    items += re.split(r'\s*;\s*|(?<=[A-Za-z])\s*,\s+(?=[A-Z]{3,})', c)
        conds = classify_extra(items, rec)
        after = tail
        for t in infos:
            after = after.replace(t, '')
        stray = ''.join(re.sub(r'<td[^>]*>.*?</td>', '', t, flags=re.S | re.I) for t in infos)  # moves put in a bare <tr>
        sol_txt = text_of(stray + '<br>' + re.sub(r'<table\s+width\s*=\s*"?160"?[^>]*>.*?</table>', '', after,
                                                   flags=re.S | re.I))
        sol, com = split_solution(sol_txt)
        if sol:
            rec['solution_orig'] = sol
            rec['solution'] = english(sol, {c for _, c in board.values()})
            if rec['solution'] == sol:
                del rec['solution_orig']
        if com:
            rec['comment'] = com
        recs.append(finish(rec, board, conds, width, height))
    return recs


# --- format 2: py2web pages (<div class="p2w-diagram">white Kd1 QFa8a4h1\nblack Ke8</div>)

def p2w_board(txt):
    board = {}
    for line in txt.strip().split('\n'):
        m = re.match(r'\s*(white|black|neutral)\s+(.*)', line, re.I)
        if not m:
            continue
        col = m.group(1)[0].lower()
        for tok in m.group(2).split():
            t = re.fullmatch(r'([A-Z][A-Z0-9]?)((?:[a-h][1-8])+)', tok)
            if not t:
                return None
            for sq in SQ.findall(t.group(2)):
                board[('abcdefgh'.index(sq[0]), int(sq[1]))] = (col, t.group(1))
    return board or None


def parse_p2w(page, page_name=''):
    recs = []
    for m in re.finditer(r'<div\s+class\s*=\s*"p2w-diagram"\s+id\s*=\s*"([^"]*)"\s*>(.*?)</div>', page, re.S | re.I):
        board = p2w_board(html.unescape(m.group(2)))
        if not board:
            continue
        pid = m.group(1)
        before = page[max(0, page.rfind('<table', 0, m.start()), page.rfind('<hr', 0, m.start()),
                          page.rfind('class="dia"', 0, m.start())):m.start()]
        before = re.sub(r'^[^<]*>', '', before)
        rec = {}
        hl = text_of(before).split('\n')
        bold = re.search(r'<b>(.*?)</b>', before, re.S | re.I)
        if bold and hl:
            num = text_of(bold.group(1))
            if re.fullmatch(r'[A-Z]{0,4}\d+[A-Za-z]?', num):
                rec['number'] = num
            first = hl[0][len(num):].strip() if hl[0].startswith(num) else hl[0]
        else:
            first = hl[-1] if hl and hl[-1] else ''
        if first:
            a, _, src = first.partition(',')
            rec['author'] = a.strip()
            rec['source'], award = split_source(src.strip() or None)
            if award:
                rec['award'] = award
        dedic = [l for l in hl[1:] if l.startswith('(')]
        if dedic:
            rec['source_note'] = ' '.join(dedic)
        sol_div = re.search(r'<div\s+class\s*=\s*"p2w-solution"\s+target\s*=\s*"%s"[^>]*>(.*?)</div>' % re.escape(pid),
                            page[m.end():], re.S | re.I)
        cap_end = min(x for x in (page.find('</td>', m.end()), page.find('<div class="p2w-solution"', m.end()),
                                  page.find('<hr', m.end()), len(page)) if x >= 0)
        cap = [l for l in text_of(page[m.end():cap_end]).split('\n') if l]
        if not cap:
            continue
        items = [x.strip() for x in re.split(r',\s+', cap[0])]
        rec['stip'] = stipulation(items[0])
        rec['count'] = '%d+%d' % (sum(1 for c, _ in board.values() if c == 'w'),
                                  sum(1 for c, _ in board.values() if c == 'b')) + \
            ('+%d' % sum(1 for c, _ in board.values() if c == 'n') if any(c == 'n' for c, _ in board.values()) else '')
        items = items[1:] + [x for l in cap[1:] if not re.search(r'(WinChloe|Popeye|Alybadix)\b.*:', l)
                             for x in re.split(r',\s+(?=[A-Z0-9])', l)]
        items = [i for i in items if not re.match(r'(WinChloe|Popeye|Alybadix)\b[^()]*:|.*\b(CPU|program)\b', i)]
        conds = classify_extra(items, rec)
        if sol_div:
            s = html.unescape(sol_div.group(1))
            s = re.sub(r'\{\s*\}', '\n', s)
            notes = re.findall(r'\{([^}]*)\}', s)
            s = re.sub(r'\{[^}]*\}', '\n', s)
            s = '\n'.join(re.sub(r'[ \t]+', ' ', l).strip() for l in s.split('\n') if l.strip())
            rec['solution'] = s
            notes = [n.strip() for n in notes if n.strip()]
            if notes:
                rec['solution_notes'] = notes
        if 'author' not in rec:                     # e.g. a page of two dedicated originals: byline at the top
            meta = re.search(r'<meta\s+name\s*=\s*"Author"\s+content\s*=\s*"([^"]+)"', page, re.I)
            head = re.search(r'<body[^>]*>(.*?)<div\s+class\s*=\s*"p2w-diagram"', page, re.S | re.I)
            lines = text_of(head.group(1)).split('\n') if head else []
            if meta or lines:
                rec['author'] = meta.group(1) if meta else lines[0]
            if len(lines) > 1 and lines[0] == rec.get('author') and 'source' not in rec:
                rec['source'] = ' '.join(lines[1:])
        recs.append(finish(rec, board, conds + PAGE_CONDITIONS.get(page_name, [])))
    return recs


# ---------------------------------------------------------------- PDF books and awards (needs pypdf)
#
# The PDFs were made with MS Word; diagrams are lines of text in Christian Poisson's "4Echecs" font (private-use
# code points U+F020..U+F0FF). Each square advances 1000 font units: ' ' / ':' are empty light / dark squares, a
# full-width glyph is a piece, two half-width glyphs make one piece (the white queen is 'd'+'e'), zero-width glyphs
# are the hatching behind a piece on a dark square or the board edge, and width-60 glyphs ('/', '!', '$', U+F0CC)
# are the left/right frame. Upper case = black, lower case = white; turned/rotated glyphs are fairy pieces whose
# names the caption gives ("Rose {rose glyph}d1", "{glyphs}=Grasshopper").

PDF_SKIP = re.compile(r'non_attacking|endings_on_an|leaper_and_hopper|math|/scanning/|asymptot', re.I)
# PowerPoint / article layouts where the author and award follow the diagram in an order this parser cannot pair up
PDF_LAYOUT_SKIP = re.compile(r'petkov_75jt_2017|bolero', re.I)
PDF_EXTRA = ['/books/kotesovec_fairy_twomovers_2008-2010.pdf']     # on the host but linked only from a mirror site
# glyph -> colour + piece + rotation (degrees, found by matching each glyph's outline against the turned base piece)
G_FULL = {0x52: 'bK', 0x72: 'wK', 0x44: 'bQ', 0x54: 'bR', 0x74: 'wR', 0x46: 'bB', 0x66: 'wB', 0x43: 'bS', 0x63: 'wS',
          0x50: 'bP', 0x70: 'wP', 0x53: 'bQ180', 0x4f: 'bR180', 0x6f: 'wR180', 0x42: 'bB180', 0x62: 'wB180',
          0x4e: 'bS180', 0x6e: 'wS180', 0x55: 'bQ90', 0x57: 'bQ270', 0x59: 'bR90', 0x79: 'wR90', 0x4c: 'bB90',
          0x4d: 'bB270', 0x6c: 'wB90', 0x6d: 'wB270', 0x47: 'bS90', 0x48: 'bS270', 0x67: 'wS90', 0x68: 'wS270',
          0x7d: 'bP270', 0x7b: 'wP270', 0x5d: 'bP90', 0x5b: 'wP90', 0x80: 'bS45', 0xaa: 'bS135', 0x9d: 'bS225',
          0xfd: 'bS315', 0x94: 'wS45', 0xbb: 'wS45', 0x81: 'wS135', 0x9e: 'wS225', 0xb8: 'wS315',
          0x41: 'bX', 0x61: 'wX', 0x49: 'nI'}                        # X = bow-tie glyph, I = imitator (disc)
G_HALF = {0x64: 'wQ', 0x65: 'wQ', 0x71: 'wQ180', 0x73: 'wQ180', 0x75: 'wQ90', 0x76: 'wQ90', 0x77: 'wQ270',
          0x78: 'wQ270', 0xc1: 'wS', 0xee: 'bS', 0xcb: 'bQ'}
G_FRAME = {0x21, 0x24, 0x2f, 0xcc}
G_EDGE_ROW = {0x2d, 0x5f}                     # top / bottom frame lines of the newer books
G_EMPTY = {0x20, 0x3a}
DEFAULT_FAIRY = {'Q180': 'G', 'S180': 'N', 'I': 'I'}    # turned queen = grasshopper, turned knight = nightrider (usual convention)
GLYPH_DESC = {'180': 'turned', '90': 'rotated', '270': 'rotated', '45': 'rotated', '135': 'rotated', '225': 'rotated',
              '315': 'rotated'}
FAIRY.update({'alfil': 'AL', 'dabbaba': 'DA', 'fers': 'FE', 'camel': 'CA', 'rook-lion': 'RL', 'bishop-lion': 'BL',
              'queen-lion': 'QL', 'nightriderlion': 'NL', 'rose-lion': 'RL', 'royal': None, 'neutral': None,
              'maximummer': None, 'circe': None, 'madrasi': None, 'rose-hopper': 'RH', 'rosehopper': 'RP',
              'edgehog': 'EH', 'kamikaze': None, 'kangourou': 'KA', 'sauterelle': 'G', 'noctambule': 'N',
              'beetle': 'BT', 'double-grasshopper': 'DG', 'kangaroo-lion': 'KL', 'berolina': 'BP', 'flamingo': 'FL',
              'lancer': 'LN', 'bouncer': 'BO', 'wazirs': 'W', 'fou-sauterelle': 'BH', 'tour-sauterelle': 'RH',
              'noctambule-sauterelle': 'NH', 'chameau': 'CA', 'zebre': 'Z', 'girafe': 'GI', 'amazone': 'AM',
              'imperatrice': 'EM', 'princesse': 'PR', 'aigle': 'EA', 'moineau': 'SP', 'tour-lion': 'RL', 'fou-lion': 'BL',
              'dame-lion': 'LI', 'cavalier-sauterelle': 'SH', 'elan': 'MO', 'pion': None, 'roi': None, 'moose': 'MO', 'eagle': 'EA', 'mao': 'MA', 'moa': 'MO'})
POPEYE_NAME.update({'AL': 'Alfil', 'DA': 'Dabbaba', 'FE': 'Fers', 'RL': 'Rook-Lion', 'BL': 'Bishop-Lion'})


def _pua(ch):
    o = ord(ch)
    return o - 0xf000 if 0xf000 <= o <= 0xf0ff else None


# Steve Smith's Linares diagram fonts (Word awards): one character per square, 'w' / 'd' = empty light / dark,
# PNBRQK / pnbrqk = white / black on a light square, )HG$!I / 0hg41i on a dark one. Turned and neutral pieces use the
# same characters in sister fonts, so those PDFs are read with the font of every character (see pdf_lines).
LIN_FONTS = ['LinaresDiagram', 'LinaresRotated90', 'LinaresRotated180', 'LinaresRotated270', 'LinaresNeutral',
             'LinaresNeutralRotated90', 'LinaresNeutralRotated180', 'LinaresNeutralRotated270']
LIN_PIECE = dict(zip('PNBRQK)HG$!Ipnbrqk0hg41i', ['w' + t for t in 'PSBRQK' * 2] + ['b' + t for t in 'PSBRQK' * 2]))


def _lin(ch):
    o = ord(ch) - 0xe000
    return (o >> 8, chr(o & 0xff)) if 0 <= o < 0x100 * len(LIN_FONTS) else None


def lin_piece(ch):
    font, c = _lin(ch)
    if c not in LIN_PIECE:
        return None
    name = LIN_FONTS[font]
    rot = re.search(r'Rotated(\d+)', name)
    col = 'n' if 'Neutral' in name else LIN_PIECE[c][0]
    return col, LIN_PIECE[c][1] + (rot.group(1) if rot else '')


def glyph_tokens(line):
    """Split a text line into plain text and chess-font pieces: ['1.', ('w', 'S'), 'h5!', ...]."""
    out, half = [], None
    for ch in line:
        c = _pua(ch)
        if c is None:
            if _lin(ch):
                p = lin_piece(ch)
                out.append(p if p else ' ')
            else:
                out.append(ch)
            continue
        if c in G_HALF:
            if half is None:
                half = G_HALF[c]
            else:
                a, b = half, G_HALF[c]
                out.append(('n' if a[0] != b[0] else a[0], a[1:]))
                half = None
        elif c in G_FULL:
            out.append((G_FULL[c][0], G_FULL[c][1:]))
        elif c == 0x20:
            out.append(' ')
    return out


def ascii_tokens(line):
    """glyph_tokens for the Latin-1 mapped font: 'tg6' -> [('w','R'), 'g6'], 'yY=Pao' -> two rotated rooks, '='...;
    French files ç / é (used where c / e would read as a piece) become c / e."""
    line = re.sub(r'([çé])(?=[1-8])', lambda m: {'ç': 'c', 'é': 'e'}[m.group(1)], line).replace('×', 'x')
    line = line.replace('‡', '#').replace('…', '...')
    out, i = [], 0
    sq = r'[x:]?[a-h][1-8]'
    while i < len(line):
        prev = line[i - 1] if i else ' '
        m = re.match(r'([A-Za-z]{1,4})=', line[i:]) if not prev.isalpha() else None
        if m and all(ord(c) in G_FULL or ord(c) in G_HALF for c in m.group(1)):
            out += [t for t in glyph_tokens(''.join(chr(0xf000 + ord(c)) for c in m.group(1))) if t != ' ']
            i += len(m.group(1))
            continue
        m = re.match(r'(de|sq|[DTFCRSYNOBtcrynoGHLMUW])(?=%s)' % sq, line[i:]) if not prev.isalpha() else None
        if m:
            code = m.group(1)
            out += glyph_tokens(''.join(chr(0xf000 + ord(c)) for c in code))
            i += len(code)
            continue
        out.append(line[i])
        i += 1
    return out


def pdf_board_row(line):
    lin = [_lin(ch) for ch in line if _lin(ch)]
    if lin:                                       # Linares: '[wdRdNGwd]'
        cs = [c for _, c in lin]
        if set(cs) & set('_-'):
            return None
        chars = [ch for ch in line if _lin(ch)]
        if '[' in cs and ']' in cs:
            chars = chars[cs.index('[') + 1:len(cs) - 1 - cs[::-1].index(']')]
        return [None if _lin(ch)[1] in 'wd' else lin_piece(ch) for ch in chars]
    cs = [c for c in map(_pua, line) if c is not None]
    fr = [i for i, c in enumerate(cs) if c in G_FRAME]
    if len(fr) >= 2:
        cs = cs[fr[0] + 1:fr[1]]
    elif len(fr) == 1:
        cs = cs[fr[0] + 1:] if fr[0] < len(cs) / 2 else cs[:fr[0]]
    if any(c in G_EDGE_ROW for c in cs):
        return None
    squares, half = [], None
    for c in cs:
        if c in G_EMPTY:
            squares.append(None)
        elif c in G_FULL:
            squares.append((G_FULL[c][0], G_FULL[c][1:]))
        elif c in G_HALF:
            if half is None:
                half = G_HALF[c]
            else:
                squares.append(('n' if half[0] != G_HALF[c][0] else half[0], half[1:]))
                half = None
    return squares if half is None else None


def is_board_line(line):
    pua = sum(1 for ch in line if _pua(ch) is not None or _lin(ch))
    return pua >= 4 and pua >= 0.8 * len(line.strip())


def pdf_lines(path):
    try:
        import pypdf
    except ImportError:
        sys.exit('parsing the PDF books needs pypdf: pip install pypdf  (or run parse with --no-pdf)')
    lines = []
    reader = pypdf.PdfReader(path)
    for n, page in enumerate(reader.pages, 1):
        try:
            fonts = [str(f.get_object().get('/BaseFont', '')) for f in
                     page.get('/Resources', {}).get('/Font', {}).values()]
            if any('Linares' in f for f in fonts):
                chunks = []

                def visit(text, cm, tm, font, size, chunks=chunks):
                    name = str(font.get('/BaseFont', '')).split('+')[-1] if font else ''
                    if name in LIN_FONTS:
                        base = 0xe000 + 0x100 * LIN_FONTS.index(name)
                        text = ''.join(chr(base + ord(c)) if ord(c) < 256 and c not in ' \n' else c for c in text)
                    chunks.append(text)
                page.extract_text(visitor_text=visit)
                text = ''.join(chunks)
            else:
                text = page.extract_text() or ''
        except Exception as e:                    # a broken page should not stop the whole book
            print('pdf page skipped', path, n, e, file=sys.stderr)
            continue
        for l in text.split('\n'):
            lines += [(n, x) for x in ascii_board(l.rstrip())]
    return lines


def ascii_board(line):
    """InDesign PDFs (Phénix awards) map the chess font to plain Latin-1 instead of U+F0xx: '/ :de: : :/'. Move such
    board rows, and the '!--------!' / '$________$' frames glued to the header or caption, back to U+F0xx."""
    pua = lambda t: ''.join(chr(0xf000 + ord(c)) if ord(c) < 256 else c for c in t)
    m = re.search(r'!-{8,}!|\$_{8,}\$', line)
    if m:
        return [x for x in (line[:m.start()].rstrip(), pua(m.group()), line[m.end():].strip()) if x]
    if re.fullmatch(r'/[^/]{3,60}/\s*', line) and all(ord(c) < 256 for c in line) and \
            not re.search(r'[a-z]{4}|[A-Z][a-z]{3}', line):
        return [pua(line.strip()) + ASCII_MARK]
    return [line]


ASCII_MARK = '\u200b'                      # tags a board row that came through ascii_board()


PDF_HEAD = re.compile(r'^\s*((?:[IVXLC]+|\d+[a-z]?)\.|\d+(?=\s\s))\s+([A-ZÀ-Ž][^\d]{2,60}?)\s*$')
PDF_COUNT = re.compile(r'\((\d+)\s*\+\s*(\d+)(?:\s*\+\s*(\d+))?\)')
PDF_AWARD = re.compile(r'(\d°|\bPrix|\bRecommand|\bMention|\bPrize|\bPreis|\bPlatz|\bPr\.|Mention|Commend|Lob|Place|Special|Hon\.?|H\.M\.|cena|uznání|Comm\.)', re.I)


def is_head(line):
    """'226. Václav Kotěšovec', 'IV. Dr. Zdeněk Mach', '12. J. Novák + V. Kotěšovec' - not '2. Honorable Mention'."""
    m = PDF_HEAD.match(line)
    if not m or PDF_AWARD.search(m.group(2)):
        return False
    words = m.group(2).split()
    particles = {'+', '&', 'a', 'and', 'et', 'und', 'de', 'van', 'von', 'der', 'la', 'le', 'di', 'da', 'del', 'ten'}
    return len(words) <= 8 and all(w[0].isupper() or w in particles for w in words)


def is_person(line):
    """'M. Caillaud', 'Juraj Lörinc', 'L. Salai Jr, E. Klemanič,' - an author line, not a fairy piece or condition."""
    line = re.sub(r'\b([A-Z]) \.', r'\1.', line.strip().rstrip(','))
    if re.search(r'[\d()=/]', line) or not is_head('0. ' + line):
        return False
    words = [w for w in re.split(r'[\s,&+]+', line) if w]
    if any(fairy_code(w) or ascii_fold(w).lower() in FAIRY for w in words) or any(_pua(c) is not None for c in line):
        return False
    return bool(re.search(r'\b[A-Z]\.', line))              # needs an initial: 'M. Caillaud', 'J.-M. Loustau'


def glyph_text(tokens, names):
    """Tokens back to text, pieces as letters (K Q R B S; pawns dropped, fairy pieces by their resolved code)."""
    out, last = [], None
    for t in tokens:
        if isinstance(t, tuple):
            typ = t[1]
            code = '' if typ == 'P' else names.get(typ, DEFAULT_FAIRY.get(typ, typ))
            if code != last:                      # '{white G}{black G}=Grasshopper' -> 'G=Grasshopper'
                out.append(code)
            last = code
        else:
            out.append(t)
            last = None
    return re.sub(r'[ \t]+', ' ', ''.join(out)).strip()


def name_code(name):
    """Code for a piece name from the caption: the table, else initials ('Pawn+Grasshopper' -> 'PG')."""
    name = name.strip(' .,:;()')
    n = ascii_fold(name).lower()
    code = next((FAIRY[x] for x in (n, n[:-1], n[:-2]) if x in FAIRY), None)
    if code is None and name and ' ' not in name:
        code = fairy_code(name)                   # plural / German / Czech spellings of a one-word name
    if code or not name or not name[0].isalpha() or name.lower() in ('c', 'b', 'a', 'and', 'or', 'with'):
        return code
    parts = [p for p in re.split(r'[-+ ]+', ascii_fold(name)) if p and p[0].isalpha()]
    if not parts or not parts[0][0].isupper():
        return None
    return (''.join(p[0] for p in parts) if len(parts) > 1 else parts[0][:2]).upper()


def fairy_names(caption_tokens, board_types=()):
    """{'S45': 'RO', ...} from 'Rose {glyph}d1', '{glyph}{glyph}=Grasshopper', 'Nightriderhopper {glyph}b5/{glyph}b2'
    and, when one fairy glyph and one fairy name are left over, from a bare 'Wazirs' line."""
    flat, types = [], []
    for t in caption_tokens:
        if isinstance(t, tuple):
            flat.append('\x01%d\x02' % len(types))
            types.append(t[1])
        else:
            flat.append(t)
    s = ''.join(flat)
    found, used = {}, set()
    for m in re.finditer(r'((?:\x01\d+\x02\s*)+)=\s*([A-Za-z][\w+-]*(?: [A-Za-z][\w-]*)?)', s):
        code = name_code(m.group(2))
        used.add(m.start(2))
        for i in re.findall(r'\x01(\d+)\x02', m.group(1)):
            if code and types[int(i)] not in EN:
                found[types[int(i)]] = code
    for m in re.finditer(r"([A-Za-z][\w'+-]*)\s*((?:(?:\x01\d+\x02)+[a-h]?\d{0,2}(?:\s*[,/]\s*[a-h]\d{1,2})*\s*[,/]?\s*)+)", s):
        code = name_code(m.group(1))
        used.add(m.start(1))
        for i in re.findall(r'\x01(\d+)\x02', m.group(2)):
            if code and types[int(i)] not in EN:
                found.setdefault(types[int(i)], code)
    for m in re.finditer(r'((?:\x01\d+\x02)+)\s+([A-Z][\w+-]*(?: [A-Z][\w-]*)?)', s):   # '{G}{g}  Grasshopper'
        code = name_code(m.group(2))
        for i in re.findall(r'\x01(\d+)\x02', m.group(1)):
            if code and types[int(i)] not in EN:
                found.setdefault(types[int(i)], code)
    left = {t for t in list(types) + list(board_types) if t not in EN and t not in found and t not in DEFAULT_FAIRY}
    words = {fairy_code(w) for w in re.findall(r'[A-Za-z][\w-]+', re.sub(r'\x01\d+\x02', ' ', s))} - {None}
    words -= set(found.values()) | set(DEFAULT_FAIRY.values())
    if len(left) == 1 and len(words) == 1:
        found[left.pop()] = words.pop()
    return found


def parse_pdf(path, url):
    lines = pdf_lines(path)
    recs, i, n = [], 0, len(lines)
    boards = []                                   # (start, end) of every board in the text
    while i < n:
        if is_board_line(lines[i][1]):
            j = i + 1                             # a new top edge (U+F0F0 overlays) starts a new board
            while j < n and is_board_line(lines[j][1]) and '\uf0f0' not in lines[j][1]:
                j += 1
            boards.append((i, j))
            i = j
        else:
            i += 1
    heads = [k for k, (_, l) in enumerate(lines) if is_head(l)]
    # figurines in the running text are chess-font glyphs (U+F0xx) in Word books, plain letters in InDesign awards
    ascii_doc = any(ASCII_MARK in l for _, l in lines)

    def tokens(line):
        return glyph_tokens(line) if not ascii_doc or any(_pua(c) is not None for c in line) else ascii_tokens(line)
    for bi, (i, j) in enumerate(boards):
        rows = [r for r in (pdf_board_row(lines[k][1]) for k in range(i, j)) if r is not None]
        if len(rows) < 3 or len({len(r) for r in rows}) != 1 or len(rows[0]) < 3:
            continue
        # header: 'number. Author' at most 8 lines above, after the previous board
        prev_end = boards[bi - 1][1] if bi else 0
        hk = [k for k in heads if max(prev_end, i - 8) <= k < i]
        if hk:
            h = hk[-1]
            m = PDF_HEAD.match(lines[h][1])
            rec = {'number': m.group(1).rstrip('.'), 'author': m.group(2).strip()}
        else:                   # articles and awards: 'Author' / source / award right above the board, no number
            above = [k for k in range(max(prev_end, i - 7), i) if lines[k][1].strip()]
            last_text = max([k for k in above if PDF_COUNT.search(lines[k][1]) or re.search(r'\d\.', lines[k][1])
                             and not PDF_AWARD.search(lines[k][1])] + [-1])
            h, label = None, None
            for k in above:
                m = re.match(r'\s*(?:(Annexe\s+\w+|Ann\d+|[A-Z]{0,3}\d+[a-z]?)\s+[-–]\s+)?(.+)$', lines[k][1])
                if k > last_text and is_head('0. ' + re.sub(r'\b([A-Z]) \.', r'\1.', m.group(2).strip())):
                    h, label = k, m.group(1)
                    break
            if h is None:
                continue                          # a scheme or a final position, not a problem
            name = re.sub(r'\b([A-Z]) \.', r'\1.', m.group(2).strip())
            while h + 1 < i and re.match(r'\s*[&+]\s+\S', lines[h + 1][1]):      # 'G. Doukhan' / '& J.-M. Loustau'
                h += 1
                name += ' ' + re.sub(r'\b([A-Z]) \.', r'\1.', lines[h][1].strip())
            rec = {'author': re.sub(r'\s*\+\s*', ' & ', name)}
            if label:
                rec['number'] = label
        meta = [lines[k][1].strip() for k in range(h + 1, i) if lines[k][1].strip() and not
                re.fullmatch(r'\d+', lines[k][1].strip()) and not is_board_line(lines[k][1])]
        award = [x for x in meta if PDF_AWARD.search(x) and not re.match(r'\d', x) or re.match(r'\d+\.\s*(Prize|Hon|Comm|Place|Lob|Special)', x)]
        src = [x for x in meta if x not in award]
        if src:
            rec['source'] = ' '.join(src)
        if award:
            rec['award'] = ' '.join(award)
        # caption: the non-empty lines right below the board
        cap, k = [], j
        while k < n and len(cap) < 10:
            t = lines[k][1].strip()
            if not t or all(_pua(c) == 0x20 for c in t):
                if cap:
                    break
                k += 1
                continue
            if is_board_line(lines[k][1]) or is_head(lines[k][1]) or is_person(t) or t.endswith(':') or \
                    re.match(r'(?:[a-zA-Z]\)\s*)?\d+\.(?:\.\.|…)?\s*[-A-Za-z\uf020-\uf0ff]', t) and not PDF_COUNT.search(t) or \
                    (len(t) > 50 and len(t.split()) >= 6 and not PDF_COUNT.search(t)):
                break                             # awards run the caption straight into the next text
            cap.append(lines[k][1])
            k += 1
        cap_tokens = [tokens(c) for c in cap]
        names = fairy_names([t for c in cap_tokens for t in c + [' ']], {sq[1] for r in rows for sq in r if sq})
        cap_text = [glyph_text(c, names) for c in cap_tokens]
        joined = ' '.join(cap_text)
        cm = PDF_COUNT.search(joined)
        if not cm:
            continue
        first = cap_text[0]
        st = re.match(r'\s*((?:[a-zA-Z-]*!?[#=+]\s?=?\s?\d*(?:[.,]\d)?)|[+=]|\S+)', first)
        rec['stip'] = stipulation(st.group(1)) if st else None
        rest = (first[st.end():] if st else first) + '\n' + '\n'.join(cap_text[1:])
        rest = PDF_COUNT.sub('\n', rest)
        items = []
        for l in rest.split('\n'):
            l = l.strip()
            if not l:
                continue
            l = re.sub(r'\bC\+(?=\s|$)', '\nC+\n', l)
            l = re.sub(r'\s(?=[a-z]\)\s)', '\n', ' ' + l)
            items += [x.strip() for x in l.split('\n') if x.strip()]
        conds = classify_extra(items, rec)
        board, height = {}, len(rows)
        for r_i, row in enumerate(rows):
            for f, sq in enumerate(row):
                if sq:
                    col, typ = sq
                    code = typ if typ in EN else names.get(typ, DEFAULT_FAIRY.get(typ))
                    if code is None:
                        code = typ
                        desc = '%s=unidentified fairy piece (%s %s glyph)' % (
                            typ, GLYPH_DESC.get(typ[1:], ''), {'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'S': 'knight',
                                                               'P': 'pawn'}.get(typ[0], 'special'))
                        if desc not in conds:
                            conds.append(desc)
                    board[(f, height - r_i)] = (col, code)
        w_cnt = sum(1 for c, _ in board.values() if c == 'w')
        b_cnt = sum(1 for c, _ in board.values() if c == 'b')
        n_cnt = sum(1 for c, _ in board.values() if c == 'n')
        rec['count'] = '+'.join(x for x in cm.groups() if x)
        found = '%d+%d' % (w_cnt, b_cnt) + ('+%d' % n_cnt if n_cnt else '')
        if found != rec['count']:                 # the caption's count disagrees with the decoded board: a glyph
            print(f'{path} p.{lines[i][0]}: board {found} != caption ({rec["count"]}), skipped', file=sys.stderr)
            continue                              # was lost or misread, so do not trust this position
        # solution / commentary: text up to the next problem header or board
        stop = min([x for x in heads if x > k] + [b[0] for b in boards[bi + 1:bi + 2]] + [n])
        body = []
        for x in range(k, stop):
            t = glyph_text(tokens(lines[x][1]), names)
            if t and not re.fullmatch(r'\d+', t):
                body.append(t)
        sol, com = split_solution('\n'.join(body))
        if sol:
            rec['solution'] = english(sol)
        if com:
            rec['comment'] = com[:4000]
        rec['page'] = url
        rec['pdf_page'] = lines[i][0]
        recs.append(finish(rec, board, conds, len(rows[0]), height))
    return recs


# conditions stated only in the article text, not in the diagram caption
PAGE_CONDITIONS = {'kotesovec_abc_endings.htm': ['AlphabeticChess']}


def parse(mirror, pdf=True):
    out, pages = [], 0
    for root, dirs, files in os.walk(mirror):
        dirs.sort()
        for fn in sorted(files):
            if fn.lower().endswith('.pdf') and pdf:
                rel = os.path.relpath(os.path.join(root, fn), mirror).replace(os.sep, '/')
                if not PDF_SKIP.search('/' + rel) and not PDF_LAYOUT_SKIP.search(rel):
                    got = parse_pdf(os.path.join(root, fn), 'http://' + HOST + '/' + rel)
                    print(f'{rel}: {len(got)} problems', file=sys.stderr)
                    out += got
                    pages += 1
                continue
            if not re.search(r'\.html?$', fn, re.I):
                continue
            path = os.path.join(root, fn)
            page = open(path, 'rb').read().decode('cp1250', 'replace')
            if re.search(r'charset\s*=\s*"?utf-8', page[:2000], re.I):
                page = open(path, 'rb').read().decode('utf-8', 'replace')
            pages += 1
            rel = os.path.relpath(path, mirror).replace(os.sep, '/')
            title = re.search(r'<title>(.*?)</title>', page, re.S | re.I)
            title = text_of(title.group(1)) if title else ''
            for rec in parse_gif_diagrams(page) + parse_p2w(page, fn):
                rec['page'] = 'http://' + HOST + '/' + ('' if rel == 'index.html' else rel)
                rec['page_title'] = title
                out.append(rec)
    return out, pages


FIELDS = ['number', 'position', 'fen', 'stip', 'count', 'author', 'author_note', 'source', 'source_note', 'award',
          'play', 'twins', 'conditions', 'test', 'solution', 'solution_orig', 'solution_notes',
          'comment', 'orthodox', 'page', 'pdf_page', 'page_title']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'parse'])
    ap.add_argument('mirror')
    ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'kotesovec.json'))
    ap.add_argument('--pdfs', action='store_true', help='crawl: also download the linked on-host PDFs')
    ap.add_argument('--no-pdf', action='store_true', help='parse: skip the PDFs (they need pypdf)')
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.mirror)
        if a.pdfs:
            fetch_pdfs(a.mirror)
        return
    recs, pages = parse(a.mirror, pdf=not a.no_pdf)
    seen, uniq = {}, []
    for r in recs:                       # the same problem is often repeated in several articles and books
        key = (r['position'], r['stip'])
        if key in seen:                  # keep the first copy, fill in what it lacks from the later one
            first = seen[key]
            for k in FIELDS:
                if first.get(k) is None and r.get(k) is not None:
                    first[k] = r[k]
            first.setdefault('also_in', [])
            if r['page'] != first['page'] and r['page'] not in first['also_in']:
                first['also_in'].append(r['page'])
            continue
        seen[key] = r
        uniq.append(r)
    uniq = [{k: r[k] for k in FIELDS + ['also_in'] if r.get(k) or k in ('fen', 'orthodox')} for r in uniq]
    doc = {'source': 'http://' + HOST + '/', 'note': 'Problems from Vaclav Kotesovec\'s website (mostly fairy '
           'chess): the HTML articles and the PDF books/awards (234 best chess problems, 360 fairy echoes, Fairy '
           'twomovers 2008-2010, tourney awards). Positions are in English notation (K Q R B S P) as "white + black" '
           '[+ neutral]; fairy pieces use Popeye-style codes (G grasshopper, N nightrider, ...) named in '
           '"conditions". Solutions are converted to English figurines; solution_orig keeps an HTML original that '
           'differed. PDF records carry pdf_page; comment holds the book\'s commentary (Czech/English, cut at '
           '4000 characters). PDF diagrams whose decoded piece count disagreed with the printed count were left out.', 'count': len(uniq), 'problems': uniq}
    data = json.dumps(doc, ensure_ascii=False, indent=1)
    out = a.out
    if len(data.encode('utf-8')) > 50_000_000:
        out = out if out.endswith('.gz') else out + '.gz'
        with gzip.open(out, 'wt', encoding='utf-8') as f:
            f.write(data)
    else:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(data)
    orth = [r for r in uniq if r['orthodox']]
    print(f'{pages} pages, {len(recs)} diagrams, {len(uniq)} unique, {len(orth)} orthodox, '
          f'{sum(1 for r in uniq if r.get("solution"))} with solution -> {out}', file=sys.stderr)


if __name__ == '__main__':
    main()
