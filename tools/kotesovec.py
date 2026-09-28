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

Diagrams drawn as a single picture (gustav/*.htm, end2008, fairyend, ...) and the PDF books/awards are not parsed.

usage:
    python tools/kotesovec.py crawl  MIRROR_DIR              # fetch every HTML page of the site (1 req/s)
    python tools/kotesovec.py parse  MIRROR_DIR [-o OUT]     # -> knowledge/kotesovec.json
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
    s = re.sub(r'\s+', ' ', s).strip()
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


# conditions stated only in the article text, not in the diagram caption
PAGE_CONDITIONS = {'kotesovec_abc_endings.htm': ['AlphabeticChess']}


def parse(mirror):
    out, pages = [], 0
    for root, dirs, files in os.walk(mirror):
        dirs.sort()
        for fn in sorted(files):
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
          'play', 'twins', 'conditions', 'test', 'solution', 'solution_orig', 'solution_notes', 'comment',
          'orthodox', 'page', 'page_title']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'parse'])
    ap.add_argument('mirror')
    ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'kotesovec.json'))
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.mirror)
        return
    recs, pages = parse(a.mirror)
    seen, uniq = set(), []
    for r in recs:                       # the same diagram is often repeated on several articles
        key = (r['position'], r['stip'], str(r.get('twins')), str(r.get('conditions')))
        if key in seen:
            continue
        seen.add(key)
        uniq.append({k: r[k] for k in FIELDS if r.get(k) is not None or k == 'fen'})
    doc = {'source': 'http://' + HOST + '/', 'note': 'Problems extracted from the HTML articles on Vaclav '
           'Kotesovec\'s website (mostly fairy chess). Positions are in English notation (K Q R B S P) as '
           '"white + black"; fairy pieces use Popeye-style codes (G grasshopper, N nightrider, ...) named in '
           '"conditions". Solutions are converted from German/Czech figurines to English; solution_orig keeps '
           'the original when it differed. Problems published only in the site\'s PDF books and diagrams '
           'shown as whole images are not included.', 'count': len(uniq), 'problems': uniq}
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
