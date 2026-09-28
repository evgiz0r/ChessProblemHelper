"""Crawl Andrey Selivanov's site selivanov.world ("Уральский проблемист") and extract its problems.

The HTML pages of the site show diagrams only as pictures (JPG/PNG with an empty ALT), so no position can be
read from them.  The problems live in the PDFs the pages link to: tourney awards, the originals and yearly
awards of the magazine "Уральский проблемист", jubilee tourneys, Moscow tourneys, ...  Most of those PDFs
were typeset with a chess diagram font (ISDiagram, Ches, GC2004D/Y, Chess Merida/Usual), so the board is
text: every diagram row is a run of glyphs, one per square.  The tool carries a small stdlib-only PDF reader
(object parser, Flate/LZW/ASCII85, ToUnicode CMaps, text-operator interpreter, rotated pages) that recovers
the glyphs with their coordinates, rebuilds the 8x8 boards and reads the text around each one: header above
(number, author, place/source, award), footer below (stipulation, piece count, twins, fairy conditions) and
the solution paragraph "№N. 1.…" further on, with figurine fonts turned into K Q R B S P.

Not read: diagrams embedded as pictures (some PDFs, the Word .doc awards), the 1Echecs fairy-diagram font
(pieces are built from overlaid glyph fragments) and PDFs with anonymous Type3 fonts.

usage:
    python tools/selivanov.py crawl  MIRROR_DIR              # polite (Crawl-delay 3 s), resumable
    python tools/selivanov.py parse  MIRROR_DIR [-o OUT]     # -> knowledge/selivanov.json (.gz if > 50 MB)
"""
import argparse, base64, gzip, heapq, html, json, multiprocessing, os, re, sys, time, urllib.parse, urllib.request, zlib

HOST = 'selivanov.world'
BASE = 'https://' + HOST
UA = ('ChessProblemHelper/1.0 (+https://github.com/evgiz0r/ChessProblemHelper; chess-problem research '
      'crawler; honours robots.txt Crawl-delay)')
DELAY = 3.0                                   # robots.txt: Crawl-delay: 3
MAX_PDF = 40 << 20                            # huge scanned books are useless without OCR
DOCS = ('.pdf', '.doc', '.docx', '.rtf')      # award files come as PDF and as Word documents
SEEDS = ['/', '/news2/', '/news1/', '/newss/', '/kompoz/', '/kompoz/uralskiy_problemist/', '/arhiv/',
         '/projects/', '/projects/sh1/', '/projects/uralskiy_problemist/', '/projects/chess_composition/',
         '/riphey/', '/novosti/', '/link/', '/selivanov/', '/selivanov/history/', '/sitemap/', '/en/']
SKIP = re.compile(r'\.(gif|jpe?g|png|bmp|ico|css|js|svg|swf|flv|mp[34]|avi|wmv|zip|rar|7z|exe|ttf|xlsx?|'
                  r'pgn|cbv|djvu?|txt|ppt)$|/bitrix/|/search/|/calendar/.+|/preyskurant/|'
                  r'/fotogalerei/|/auth/|/personal/|/404\.php', re.I)
KEEP_QUERY = re.compile(r'^(ID|PAGEN_\d+|SECTION_ID|ELEMENT_ID)$')


# ---------------------------------------------------------------- crawl

def canon(url, base=BASE + '/'):
    """Absolute on-host URL in one canonical spelling, or None for off-host / unwanted links."""
    url = html.unescape(url.strip())
    if re.search(r'#[^#]*\.pdf$', url, re.I):             # '#' used literally in a few PDF names
        url = url.replace('#', '%23')
    url = urllib.parse.urljoin(base, url)
    p = urllib.parse.urlsplit(url)
    host = p.netloc.lower().split(':')[0]
    if p.scheme not in ('http', 'https') or host not in (HOST, 'www.' + HOST):
        return None
    path = urllib.parse.quote(urllib.parse.unquote(p.path or '/'), safe="/%()!$&'*+,;=:@~-._")
    path = re.sub(r'/index\.php$', '/', path)
    path = re.sub(r'/(?:%20|%C2%A0)+(?=[^/])', '/', path)     # links to ' name.pdf' 404; the file is 'name.pdf'
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True)]
    if any(not KEEP_QUERY.match(k) for k, _ in q):
        return None                              # print versions, sort orders, logins, calendars ...
    query = urllib.parse.urlencode(sorted(q))
    return BASE + path + ('?' + query if query else '')


def local_path(url):
    p = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(p.path)
    if path.endswith('/'):
        path += 'index.html'
    if p.query:
        path += '_' + re.sub(r'[^\w=.-]', '_', p.query) + '.html'
    return path.lstrip('/')


def priority(url):
    """Lower = sooner.  Problem-bearing documents first, award/magazine indexes next, news, then the rest."""
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lower()
    if path.endswith(('.pdf', '.doc', '.docx', '.rtf')):
        return 0
    if re.match(r'/(en/)?(news2|news1|kompoz|arhiv|riphey|projects)/', path):
        return 1
    if re.match(r'/(en/)?newss/', path):
        return 2
    if path.startswith('/en/'):
        return 4
    if path.startswith('/selivanov/history/'):
        return 5                                 # his compositions: JPG diagrams only
    return 3


LINK = re.compile(r"""(?:href|src)\s*=\s*["']?([^"'\s>]+)""", re.I)
ANCHOR = re.compile(r"""<a\s[^>]*href\s*=\s*["']?([^"'\s>]+)[^>]*>(.*?)</a>""", re.I | re.S)
# news items are fetched only when their title hints at problems (awards, results, magazine issues, site updates)
NEWS_ITEM = re.compile(r'/(en/)?newss/detail\.php')
RELEVANT = re.compile(r'итог|результат|award|result|отч[её]т|обновлен|update|предварит|окончат|final|конкурс|турнир|'
                      r'tourney|журнал|выпуск|номер|№|приз|задач|problem|этюд|study|решени|solving|композиц|'
                      r'composition|альбом|album|чемпионат|championship|wcct|кубок|cup|мемориал|memorial|юк|jt|mt|миниатюр',
                      re.I)


def links_of(body, url):
    text = body.decode('utf-8', 'replace')
    titles = {}
    for href, label in ANCHOR.findall(text):
        c = canon(href, url)
        if c:
            titles[c] = titles.get(c, '') + ' ' + re.sub(r'<[^>]+>', '', label)
    out = set()
    for link in LINK.findall(text):
        if link.startswith(('mailto:', 'javascript:', '#')):
            continue
        c = canon(link, url)
        if not c or SKIP.search(urllib.parse.urlsplit(c).path):
            continue
        if NEWS_ITEM.search(c) and not RELEVANT.search(html.unescape(titles.get(c, ''))):
            continue                                             # plain news: nothing to parse there
        out.add(c)
    return out


def crawl(out, delay=DELAY, limit=None):
    os.makedirs(out, exist_ok=True)
    lock = open(os.path.join(out, '_crawl.lock'), 'w')
    try:                                                         # two crawlers would double the request rate
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except ImportError:
        pass
    except OSError:
        sys.exit('another crawl is already running on ' + out)
    index_file = os.path.join(out, '_index.tsv')        # url <tab> status <tab> local path
    done = {}
    if os.path.exists(index_file):
        for line in open(index_file, encoding='utf-8'):
            u, st, lp = (line.rstrip('\n').split('\t') + ['', ''])[:3]
            if st.startswith('err') or st[:1] == '5':         # transient failures: retry on resume
                done.pop(u, None)
            else:
                done[u] = (st, lp)
    queue, queued, seq = [], set(), 0

    def push(u):
        nonlocal seq
        if u not in done and u not in queued:
            queued.add(u)
            seq += 1
            heapq.heappush(queue, (priority(u), seq, u))

    for s in SEEDS:
        push(canon(s))
    for u, (st, lp) in done.items():                  # resume: re-harvest links of mirrored pages
        if st == '200' and lp.endswith('.html'):
            try:
                for l in links_of(open(os.path.join(out, lp), 'rb').read(), u):
                    push(l)
            except OSError:
                pass
    idx = open(index_file, 'a', encoding='utf-8')
    fetched, last, retries = 0, 0.0, {}
    print(f'{len(done)} urls already done, {len(queue)} queued', file=sys.stderr)
    while queue and (limit is None or fetched < limit):
        _, _, url = heapq.heappop(queue)
        if url in done:
            continue
        time.sleep(max(0.0, last + delay - time.time()))
        last = time.time()
        fetched += 1
        status, lp, body, final = '', '', None, url
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                ctype = r.headers.get('Content-Type', '')
                size = int(r.headers.get('Content-Length') or 0)
                final = canon(r.geturl()) or url
                if 'pdf' in ctype or 'word' in ctype or 'rtf' in ctype or \
                        urllib.parse.unquote(url).lower().endswith(DOCS):
                    if size > MAX_PDF:
                        status = 'toobig:%d' % size
                    else:
                        body = r.read(MAX_PDF + 1)
                        status = 'toobig' if len(body) > MAX_PDF else '200'
                elif 'html' in ctype:
                    body, status = r.read(), '200'
                else:
                    status = 'type:' + ctype.split(';')[0]
        except urllib.error.HTTPError as e:
            status = str(e.code)
        except Exception as e:
            status = 'err:' + type(e).__name__
        if status.startswith('err') and url not in retries:     # network hiccup: retry once, later
            retries[url] = status
            seq += 1
            heapq.heappush(queue, (priority(url) + 0.5, seq, url))
            print(f'[{fetched}] {status} {url} (will retry)', file=sys.stderr)
            continue
        if status == '200' and body is not None and urllib.parse.unquote(url).lower().endswith('.pdf') \
                and not body.startswith(b'%PDF'):
            status = 'notpdf'                                    # soft 404: an HTML error page served as 200
        if status == '200' and final != url:            # redirected: store under the final URL
            done[url] = ('redirect', final)
            idx.write(f'{url}\tredirect\t{final}\n')
            if final in done:
                continue
            url = final
        if status == '200' and body is not None:
            lp = local_path(url)
            if not lp.lower().endswith(DOCS + ('.html',)):
                lp += '.pdf' if body[:5] == b'%PDF-' else '.html'
            dest = os.path.join(out, lp)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(body)
            if lp.endswith('.html'):
                for l in links_of(body, url):
                    push(l)
        done[url] = (status, lp)
        idx.write(f'{url}\t{status}\t{lp}\n')
        idx.flush()
        print(f'[{fetched}] {status} {url}  (queue {len(queue)})', file=sys.stderr)
    print(f'{fetched} fetched this run, {len(done)} urls done, {len(queue)} left in queue', file=sys.stderr)



# ---------------------------------------------------------------- a tiny PDF reader (stdlib only)

class Name(str):
    pass


class Ref(tuple):
    pass


class Op(bytes):
    pass


WS = b' \t\r\n\x0c\x00'
DELIM = b'()<>[]{}/%'
TOKEN_END = WS + DELIM


def skip_ws(d, i):
    n = len(d)
    while i < n:
        c = d[i]
        if c in WS:
            i += 1
        elif c == 0x25:                                  # % comment
            while i < n and d[i] not in b'\r\n':
                i += 1
        else:
            break
    return i


def parse_obj(d, i):
    """Parse one PDF object at d[i:] -> (value, end).  Operators come back as bytes objects."""
    i = skip_ws(d, i)
    c = d[i:i + 1]
    if c == b'/':
        j = i + 1
        while j < len(d) and d[j] not in TOKEN_END:
            j += 1
        name = re.sub(rb'#([0-9a-fA-F]{2})', lambda m: bytes([int(m.group(1), 16)]), d[i + 1:j])
        return Name(name.decode('latin-1')), j
    if c == b'<':
        if d[i + 1:i + 2] == b'<':
            out, i = {}, i + 2
            while True:
                i = skip_ws(d, i)
                if d[i:i + 2] == b'>>':
                    return out, i + 2
                k, i = parse_obj(d, i)
                v, i = parse_obj(d, i)
                out[k] = v
        j = d.index(b'>', i)
        hx = re.sub(rb'\s', b'', d[i + 1:j])
        if len(hx) % 2:
            hx += b'0'
        return bytes.fromhex(hx.decode('ascii', 'replace')) if re.fullmatch(rb'[0-9a-fA-F]*', hx) else b'', j + 1
    if c == b'[':
        out, i = [], i + 1
        while True:
            i = skip_ws(d, i)
            if d[i:i + 1] == b']':
                return out, i + 1
            if i >= len(d):
                return out, i
            v, i = parse_obj(d, i)
            out.append(v)
    if c == b'(':
        out, depth, i = bytearray(), 1, i + 1
        while i < len(d):
            ch = d[i]
            if ch == 0x5c:                               # backslash
                i += 1
                e = d[i:i + 1]
                if e in b'01234567' and e:
                    m = re.match(rb'[0-7]{1,3}', d[i:i + 3])
                    out.append(int(m.group(0), 8) & 255)
                    i += len(m.group(0))
                    continue
                out += {b'n': b'\n', b'r': b'\r', b't': b'\t', b'b': b'\b', b'f': b'\f'}.get(e, e) \
                    if e not in b'\r\n' else b''
                if e == b'\r' and d[i + 1:i + 2] == b'\n':
                    i += 1
                i += 1
                continue
            if ch == 0x28:
                depth += 1
            elif ch == 0x29:
                depth -= 1
                if not depth:
                    return bytes(out), i + 1
            out.append(ch)
            i += 1
        return bytes(out), i
    j = i
    while j < len(d) and d[j] not in TOKEN_END:
        j += 1
    if j == i:                                          # stray delimiter
        return b'', i + 1
    tok = d[i:j]
    if re.fullmatch(rb'[+-]?(\d+\.?\d*|\.\d+)', tok):
        # "N G R" reference?
        m = re.match(rb'\s+(\d+)\s+R(?=[\s/<>\[\]()%]|$)', d[j:j + 20])
        if m and b'.' not in tok:
            return Ref((int(tok), int(m.group(1)))), j + m.end()
        return (float(tok) if b'.' in tok else int(tok)), j
    if tok == b'true':
        return True, j
    if tok == b'false':
        return False, j
    if tok == b'null':
        return None, j
    return Op(tok), j                                   # operator / keyword


def lzw_decode(data):
    out, table, bits, buf, nbits, prev = bytearray(), [bytes([i]) for i in range(256)] + [None, None], 9, 0, 0, None
    for byte in data:
        buf = (buf << 8) | byte
        nbits += 8
        while nbits >= bits:
            nbits -= bits
            code = (buf >> nbits) & ((1 << bits) - 1)
            if code == 256:
                table, bits, prev = table[:258], 9, None
                continue
            if code == 257:
                return bytes(out)
            if prev is None:
                entry = table[code]
            else:
                entry = table[code] if code < len(table) else prev + prev[:1]
                table.append(prev + entry[:1])
                if len(table) >= (1 << bits) - 1 and bits < 12:
                    bits += 1
            out += entry
            prev = entry
    return bytes(out)


def a85_decode(data):
    data = re.sub(rb'\s', b'', data)
    if data.startswith(b'<~'):
        data = data[2:]
    data = data.split(b'~>')[0]
    return base64.a85decode(data)


def predictor(data, parms):
    pred = parms.get('Predictor', 1) if isinstance(parms, dict) else 1
    if pred < 10:
        return data
    cols = parms.get('Columns', 1) * parms.get('Colors', 1) * parms.get('BitsPerComponent', 8) // 8
    bpp = max(1, parms.get('Colors', 1) * parms.get('BitsPerComponent', 8) // 8)
    out, prev = bytearray(), bytearray(cols)
    for r in range(0, len(data), cols + 1):
        ft, row = data[r], bytearray(data[r + 1:r + 1 + cols])
        for k in range(len(row)):
            a = row[k - bpp] if k >= bpp else 0
            b = prev[k] if k < len(prev) else 0
            c = prev[k - bpp] if k >= bpp else 0
            if ft == 1:
                row[k] = (row[k] + a) & 255
            elif ft == 2:
                row[k] = (row[k] + b) & 255
            elif ft == 3:
                row[k] = (row[k] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[k] = (row[k] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out += row
        prev = row
    return bytes(out)


class PDF:
    def __init__(self, data):
        self.d = data
        self.offsets, self.cache = {}, {}
        for m in re.finditer(rb'(?:^|(?<=[\r\n\s>]))(\d+)\s+(\d+)\s+obj\b', data):
            self.offsets[int(m.group(1))] = m.end()      # later definitions (incremental updates) win
        self.objstm = {}
        for num in list(self.offsets):
            head = data[self.offsets[num]:self.offsets[num] + 200]
            if b'/ObjStm' in head:
                try:
                    self._load_objstm(num)
                except Exception:
                    pass

    def _load_objstm(self, num):
        dct, raw = self.get(num)
        body = self.decode(dct, raw)
        n, first = self.resolve(dct.get('N', 0)), self.resolve(dct.get('First', 0))
        nums = [int(x) for x in body[:first].split()]
        for k in range(n):
            onum, off = nums[2 * k], nums[2 * k + 1]
            if onum not in self.offsets:
                self.objstm[onum] = (body, first + off)

    def get(self, num):
        """Object number -> value (a stream comes back as (dict, raw_bytes))."""
        if num in self.cache:
            return self.cache[num]
        self.cache[num] = None
        try:
            if num in self.offsets:
                v, i = parse_obj(self.d, self.offsets[num])
                j = skip_ws(self.d, i)
                if isinstance(v, dict) and self.d[j:j + 6] == b'stream':
                    j += 6
                    if self.d[j:j + 2] == b'\r\n':
                        j += 2
                    elif self.d[j:j + 1] in (b'\n', b'\r'):
                        j += 1
                    ln = v.get('Length')
                    if isinstance(ln, Ref):
                        ln = self.resolve(ln)
                    if isinstance(ln, int) and self.d[j + ln:j + ln + 30].lstrip().startswith(b'endstream'):
                        raw = self.d[j:j + ln]
                    else:
                        raw = self.d[j:self.d.index(b'endstream', j)]
                    v = (v, raw)
            elif num in self.objstm:
                body, off = self.objstm[num]
                v = parse_obj(body, off)[0]
            else:
                v = None
        except Exception:
            v = None
        self.cache[num] = v
        return v

    def resolve(self, v, depth=0):
        while isinstance(v, Ref) and depth < 20:
            v, depth = self.get(v[0]), depth + 1
        return v

    def decode(self, dct, raw):
        filters = self.resolve(dct.get('Filter'))
        parms = self.resolve(dct.get('DecodeParms'))
        filters = filters if isinstance(filters, list) else [filters] if filters else []
        parms = parms if isinstance(parms, list) else [parms] * len(filters)
        data = raw
        for f, p in zip(filters, parms):
            p = self.resolve(p) or {}
            if f in ('FlateDecode', 'Fl'):
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    do = zlib.decompressobj()
                    try:
                        data = do.decompress(data)
                    except zlib.error:
                        data = b''
                data = predictor(data, p)
            elif f in ('LZWDecode', 'LZW'):
                data = predictor(lzw_decode(data), p)
            elif f in ('ASCII85Decode', 'A85'):
                data = a85_decode(data)
            elif f in ('ASCIIHexDecode', 'AHx'):
                data = bytes.fromhex(re.sub(rb'[^0-9a-fA-F]', b'', data.split(b'>')[0]).decode())
            else:
                return None                            # images (DCT, CCITT, JBIG2 ...)
        return data

    def stream(self, v):
        v = self.resolve(v)
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], dict):
            return self.decode(v[0], v[1]) or b''
        return b''

    def pages(self):
        """[(page_dict)] in document order, with inherited Resources resolved."""
        root = None
        for num in sorted(self.offsets):
            v = self.get(num)
            if isinstance(v, dict) and v.get('Type') == 'Catalog':
                root = v
        for num in self.objstm:
            if root:
                break
            v = self.get(num)
            if isinstance(v, dict) and v.get('Type') == 'Catalog':
                root = v
        out, seen = [], set()

        def walk(node, res):
            node_d = self.resolve(node)
            if not isinstance(node_d, dict) or (isinstance(node, Ref) and node in seen):
                return
            if isinstance(node, Ref):
                seen.add(node)
            res = node_d.get('Resources', res)
            kids = self.resolve(node_d.get('Kids'))
            if kids:
                for k in kids:
                    walk(k, res)
            elif node_d.get('Type') == 'Page' or 'Contents' in node_d:
                p = dict(node_d)
                p['Resources'] = res
                out.append(p)
        if root:
            walk(root.get('Pages'), None)
        if not out:                                    # broken catalog: take every Page object
            for num in sorted(self.offsets):
                v = self.get(num)
                if isinstance(v, dict) and v.get('Type') == 'Page':
                    out.append(v)
        return out


def parse_cmap(data):
    """ToUnicode CMap -> ({code: str}, code byte length)."""
    m, nbytes = {}, 1
    for rng in re.findall(rb'begincodespacerange(.*?)endcodespacerange', data, re.S):
        h = re.findall(rb'<([0-9a-fA-F]+)>', rng)
        if h:
            nbytes = max(nbytes, len(h[0]) // 2)

    def u(hx):
        b = bytes.fromhex(hx.decode())
        try:
            return b.decode('utf-16-be')
        except UnicodeDecodeError:
            return ''
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', data, re.S):
        for a, b in re.findall(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]*)>', blk):
            m[int(a, 16)] = u(b)
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', data, re.S):
        for a, b, rest in re.findall(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*(<[0-9a-fA-F]*>|\[[^\]]*\])', blk):
            lo, hi = int(a, 16), int(b, 16)
            if rest.startswith(b'['):
                for k, hx in enumerate(re.findall(rb'<([0-9a-fA-F]*)>', rest)):
                    m[lo + k] = u(hx)
            else:
                base = bytes.fromhex(rest[1:-1].decode())
                if not base:
                    continue
                for k in range(min(hi - lo + 1, 65536)):
                    bb = base[:-1] + bytes([(base[-1] + k) & 255]) if len(base) > 1 else bytes([(base[0] + k) & 255])
                    if len(base) >= 2 and base[-1] + k > 255:
                        v = int.from_bytes(base, 'big') + k
                        bb = v.to_bytes(len(base), 'big')
                    try:
                        m[lo + k] = bb.decode('utf-16-be')
                    except UnicodeDecodeError:
                        pass
    return m, nbytes


class Font:
    def __init__(self, pdf, fd):
        fd = pdf.resolve(fd)
        fd = fd if isinstance(fd, dict) else {}
        self.name = str(pdf.resolve(fd.get('BaseFont')) or '').split('+')[-1]
        self.type0 = fd.get('Subtype') == 'Type0'
        self.nbytes = 2 if self.type0 else 1
        self.cmap = {}
        tu = fd.get('ToUnicode')
        if tu is not None:
            self.cmap, nb = parse_cmap(pdf.stream(tu))
            if self.type0:
                self.nbytes = nb if nb in (1, 2) else 2
        self.diff, self.codec = {}, 'cp1252'
        enc = pdf.resolve(fd.get('Encoding'))
        base = enc.get('BaseEncoding') if isinstance(enc, dict) else enc
        if base == 'MacRomanEncoding':
            self.codec = 'mac_roman'
        if isinstance(enc, dict):
            code = 0
            for x in pdf.resolve(enc.get('Differences')) or []:
                if isinstance(x, int):
                    code = x
                else:
                    self.diff[code] = str(x)
                    code += 1
        self.widths, self.dw, self.first = {}, 1000, 0
        if self.type0:
            desc = pdf.resolve(fd.get('DescendantFonts'))
            desc = pdf.resolve(desc[0]) if desc else {}
            self.dw = pdf.resolve(desc.get('DW', 1000)) or 1000
            w = pdf.resolve(desc.get('W')) or []
            k = 0
            while k < len(w):
                c0 = pdf.resolve(w[k])
                nxt = pdf.resolve(w[k + 1]) if k + 1 < len(w) else None
                if isinstance(nxt, list):
                    for n_, ww in enumerate(nxt):
                        self.widths[c0 + n_] = pdf.resolve(ww)
                    k += 2
                else:
                    for c in range(c0, (nxt or c0) + 1):
                        self.widths[c] = pdf.resolve(w[k + 2]) if k + 2 < len(w) else self.dw
                    k += 3
        else:
            self.first = pdf.resolve(fd.get('FirstChar', 0)) or 0
            for n_, ww in enumerate(pdf.resolve(fd.get('Widths')) or []):
                self.widths[self.first + n_] = pdf.resolve(ww)
            desc = pdf.resolve(fd.get('FontDescriptor')) or {}
            self.dw = pdf.resolve(desc.get('MissingWidth', 0)) or 500

    def codes(self, s):
        if self.nbytes == 2:
            return [int.from_bytes(s[k:k + 2], 'big') for k in range(0, len(s) - 1, 2)]
        return list(s)

    def text(self, code):
        if code in self.cmap:
            return self.cmap[code]
        if code in self.diff:
            name = self.diff[code]
            if re.fullmatch(r'uni[0-9A-F]{4}', name):
                return chr(int(name[3:], 16))
            return GLYPHS.get(name, '')
        if self.nbytes == 1:
            return bytes([code]).decode(self.codec, 'replace')
        return ''

    def width(self, code):
        w = self.widths.get(code, self.dw)
        return (w if isinstance(w, (int, float)) else self.dw) / 1000.0


GLYPHS = dict(zip('space exclam quotedbl numbersign dollar percent ampersand quotesingle parenleft parenright asterisk '
                  'plus comma hyphen period slash zero one two three four five six seven eight nine colon semicolon '
                  'less equal greater question at'.split(), [chr(c) for c in range(0x20, 0x41)]))
GLYPHS.update(zip('bracketleft backslash bracketright asciicircum underscore grave'.split(), '[\\]^_`'))
GLYPHS.update(zip('braceleft bar braceright asciitilde'.split(), '{|}~'))
GLYPHS.update({'endash': '–', 'emdash': '—', 'multiply': '×', 'quoteright': "'", 'quoteleft': "'", 'ellipsis': '…',
               'quotedblleft': '“', 'quotedblright': '”', 'guillemotleft': '«', 'guillemotright': '»', 'bullet': '•',
               'arrowright': '→', 'arrowboth': '↔', 'degree': '°', 'nbspace': ' ', 'afii61352': '№', 'minus': '−',
               'afii10023': 'Ё', 'afii10071': 'ё'})
GLYPHS.update({c: c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'})
GLYPHS.update({'afii%d' % (10017 + k + (k > 5)): chr(0x410 + k) for k in range(32)})     # А..Я (Ё sits after Е)
GLYPHS.update({'afii%d' % (10065 + k + (k > 5)): chr(0x430 + k) for k in range(32)})     # а..я
for _c, _n in (('W', 'KQRBSP'), ('B', 'KQRBSP')):                                       # figurine glyph names
    GLYPHS.update({_c + name: p for name, p in zip(('King', 'Queen', 'Rook', 'Bishop', 'Knight', 'Pawn'), _n)})


def mul(a, b):
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2],
            a[2] * b[1] + a[3] * b[3], a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


def page_glyphs(pdf, page, fonts_cache):
    """Run the page's content stream(s); return [(x, y, size, fontname, text, code, advance)]."""
    contents = pdf.resolve(page.get('Contents'))
    if isinstance(contents, list):
        data = b'\n'.join(pdf.stream(c) for c in contents)
    else:
        data = pdf.stream(page.get('Contents'))
    out = []
    run_content(pdf, data, pdf.resolve(page.get('Resources')) or {}, [1, 0, 0, 1, 0, 0], fonts_cache, out, 0)
    # rotated pages (landscape layouts, /Rotate 90): turn coordinates so that the text runs left to right
    votes = {}
    for g in out:
        dx, dy = g[7]
        key = (0 if abs(dx) >= abs(dy) and dx > 0 else 2 if abs(dx) >= abs(dy) else 1 if dy > 0 else 3)
        votes[key] = votes.get(key, 0) + 1
    rot = max(votes, key=votes.get) if votes else 0
    turn = {0: lambda x, y: (x, y), 1: lambda x, y: (y, -x), 2: lambda x, y: (-x, -y), 3: lambda x, y: (-y, x)}[rot]
    return [turn(g[0], g[1]) + g[2:7] for g in out]


def run_content(pdf, data, res, ctm, fonts_cache, out, depth):
    fonts = pdf.resolve(res.get('Font')) or {}
    xobjs = pdf.resolve(res.get('XObject')) or {}
    stack, gstack = [], []
    tm = tlm = [1, 0, 0, 1, 0, 0]
    font, size, tc, tw, th, tl, rise = None, 0, 0, 0, 1, 0, 0
    i, n = 0, len(data)
    while i < n:
        i = skip_ws(data, i)
        if i >= n:
            break
        try:
            v, i = parse_obj(data, i)
        except (ValueError, IndexError):
            break
        if not isinstance(v, Op):
            stack.append(v)
            continue
        op = v
        if op == b'BI':                                 # inline image: skip to EI
            k = data.find(b'EI', i)
            while k != -1 and not (data[k - 1:k] in WS and data[k + 2:k + 3] in WS + b''):
                k = data.find(b'EI', k + 2)
            i = n if k == -1 else k + 2
            stack = []
            continue
        a = stack
        stack = []
        try:
            if op == b'q':
                gstack.append(ctm)
            elif op == b'Q':
                ctm = gstack.pop() if gstack else ctm
            elif op == b'cm' and len(a) >= 6:
                ctm = mul([float(x) for x in a[-6:]], ctm)
            elif op == b'BT':
                tm = tlm = [1, 0, 0, 1, 0, 0]
            elif op == b'Tf' and len(a) >= 2:
                key, size = a[-2], float(a[-1])
                fk = (id(fonts), key)
                if fk not in fonts_cache:
                    fonts_cache[fk] = Font(pdf, fonts.get(key)) if key in fonts else None
                font = fonts_cache[fk]
            elif op == b'Tc':
                tc = float(a[-1])
            elif op == b'Tw':
                tw = float(a[-1])
            elif op == b'Tz':
                th = float(a[-1]) / 100
            elif op == b'TL':
                tl = float(a[-1])
            elif op == b'Ts':
                rise = float(a[-1])
            elif op in (b'Td', b'TD') and len(a) >= 2:
                if op == b'TD':
                    tl = -float(a[-1])
                tlm = mul([1, 0, 0, 1, float(a[-2]), float(a[-1])], tlm)
                tm = tlm
            elif op == b'Tm' and len(a) >= 6:
                tlm = tm = [float(x) for x in a[-6:]]
            elif op == b'T*':
                tlm = mul([1, 0, 0, 1, 0, -tl], tlm)
                tm = tlm
            elif op in (b'Tj', b"'", b'"', b'TJ'):
                if op in (b"'", b'"'):
                    tlm = mul([1, 0, 0, 1, 0, -tl], tlm)
                    tm = tlm
                    if op == b'"' and len(a) >= 3:
                        tw, tc = float(a[-3]), float(a[-2])
                items = a[-1] if op == b'TJ' else [a[-1]]
                if not isinstance(items, list):
                    items = [items]
                for it in items:
                    if isinstance(it, (int, float)):
                        tm = mul([1, 0, 0, 1, -it / 1000.0 * size * th, 0], tm)
                        continue
                    if not isinstance(it, bytes) or font is None:
                        continue
                    for code in font.codes(it):
                        m = mul(mul([size * th, 0, 0, size, 0, rise], tm), ctm)
                        fs = (m[2] * m[2] + m[3] * m[3]) ** 0.5 or size
                        out.append((m[4], m[5], fs, font.name, font.text(code), code,
                                    font.width(code) * (m[0] * m[0] + m[1] * m[1]) ** 0.5, (m[0], m[1])))
                        adv = (font.width(code) * size + tc + (tw if code == 32 and font.nbytes == 1 else 0)) * th
                        tm = mul([1, 0, 0, 1, adv, 0], tm)
            elif op == b'Do' and a and depth < 5:
                xo = xobjs.get(a[-1])
                xv = pdf.resolve(xo)
                if isinstance(xv, tuple) and xv[0].get('Subtype') == 'Form':
                    fm = [float(x) for x in (pdf.resolve(xv[0].get('Matrix')) or [1, 0, 0, 1, 0, 0])]
                    sub = pdf.resolve(xv[0].get('Resources')) or res
                    run_content(pdf, pdf.decode(xv[0], xv[1]) or b'', sub, mul(fm, ctm), fonts_cache, out,
                                depth + 1)
        except (ValueError, TypeError, IndexError, ZeroDivisionError):
            pass
    return out


# ---------------------------------------------------------------- chess fonts

def _table(order, first, step_piece, step_sq, step_col):
    """Build {char: (colour, piece)} for fonts laid out in regular blocks."""
    out = {}
    for n, p in enumerate(order):
        for col in (0, 1):
            for dark in (0, 1):
                out[first + n * step_piece + col * step_col + dark * step_sq] = ('wb'[col], p)
    return out


def _letters(white_light, white_dark, black_light, black_dark):
    out = {}
    for chars, col in ((white_light, 'w'), (white_dark, 'w'), (black_light, 'b'), (black_dark, 'b')):
        for ch, p in zip(chars, 'KQRBSP'):
            out[ord(ch)] = (col, p)
    return out


# ISDiagram (the typesetting font of "Уральский проблемист"): '!'..'8' = wP bP wS bS wB bB wR bR wQ bQ wK bK,
# each on a light then a dark square; two sets of empty squares and frames.
ISDIAGRAM = _table('PSBRQK', 0x21, 4, 1, 2)
# GC2004D: per piece four consecutive characters (white light, white dark, black light, black dark).
GC2004 = {}
for _p, _c in zip('KQRBSP', (0x30, 0x47, 0x57, 0x6D, 0xA9, 0xB9)):
    for _k, _v in enumerate((('w', _p), ('w', _p), ('b', _p), ('b', _p))):
        GC2004[_c + _k] = _v
# Chess Merida / Usual / Cases (A. Marroquin): lower case = piece on a light square, upper case = on a dark one.
MARROQUIN = _letters('kqrbnp', 'KQRBNP', 'lwtvmo', 'LWTVMO')
DIAGRAM_FONTS = [   # (font-name regex, pieces, empty squares, frame characters)
    (re.compile(r'ISDiag', re.I), ISDIAGRAM, {0x39, 0x3A, 0x3F, 0x40}, set(range(0x3B, 0x3F)) | {0x41, 0x42} |
     set(range(0x49, 0x51))),
    (re.compile(r'^Ches($|,)', re.I), {**ISDIAGRAM, **{ord(c): ('w', p) for c, p in zip('moqsu', 'SBRQK')}},
     {0x39, 0x3A, 0x3F, 0x40}, set(range(0x3B, 0x3F)) | {0x41, 0x42} | set(range(0x49, 0x51))),
    (re.compile(r'GC2004[DY]', re.I), GC2004, {0x4F, 0x50, 0xA3, 0xA4}, set(range(0x4B, 0x4F)) | set(range(0x51, 0x55))),
    (re.compile(r'Merida|Chess ?Usual|Chess ?Cases', re.I), MARROQUIN, {0x20, 0x2B, 0x2D},
     set(range(0x21, 0x2B)) | {0x2C, 0x2E, 0x2F} | set(range(0x30, 0x3A)) | set(range(0xC0, 0xF0))),
]
# 1Echecs (fairy sections): French letters, lower case white, upper case black; digits overlay a piece to turn it
# into a fairy one; other letters are fairy pieces.
ECHECS = {ord(c): (col, p) for chars, col in (('rdtfcp', 'w'), ('RDTFCP', 'b')) for c, p in zip(chars, 'KQRBSP')}
DIAGRAM_FONTS.append((re.compile('Echecs'), ECHECS, {0x20, 0x3A}, set(range(0x21, 0x30)) | {0x5B, 0x5D, 0x5F, 0x7C}))
# figurine fonts used inside solutions: character -> English piece letter
_CHES = {'k': 'P', 'l': 'P', 'm': 'S', 'n': 'S', 'o': 'B', 'p': 'B', 'q': 'R', 'r': 'R', 's': 'Q', 't': 'Q', 'u': 'K',
         'v': 'K'}
_CHES.update({chr(c): p for c, (_, p) in ISDIAGRAM.items()})       # '!'..'8' as in ISDiagram
FIGURINES = [
    (re.compile(r'^Ches($|,)', re.I), _CHES),
    (re.compile(r'^Cheq($|,)', re.I), {'!': 'P', '%': 'S', ')': 'B', '-': 'R', '1': 'Q', '5': 'K'}),
    (re.compile(r'^(Chess|ChessAlpha|ChessFigurine)($|,)', re.I),
     {'k': 'K', 'l': 'K', 'q': 'Q', 'w': 'Q', 'r': 'R', 't': 'R', 'b': 'B', 'n': 'B', 'h': 'S', 'j': 'S', 'p': 'P',
      'o': 'P'}),
]
SYMBOLS = {'\uf0ae': '→', '\uf0ab': '↔', '\uf0e0': '→', '\uf0e8': '→', '\uf0b4': '×', '\uf0bc': '…', '\uf02d': '-',
           '\uf0de': '⇒', '\uf0a5': '∞', '\uf0b1': '±', '\uf020': ' '}         # Symbol / Wingdings in text
UNICODE_FIG = {'♔': 'K', '♕': 'Q', '♖': 'R', '♗': 'B', '♘': 'S', '♙': 'P',
               '♚': 'K', '♛': 'Q', '♜': 'R', '♝': 'B', '♞': 'S', '♟': 'P'}


def font_char(t):
    """Symbol fonts map to U+F0xx; bring them back to their 8-bit character."""
    if len(t) != 1:
        return None
    o = ord(t)
    return o - 0xF000 if 0xF000 <= o <= 0xF0FF else o


def classify(glyph):
    """-> ('square', piece_or_None_or_'?') / ('frame',) / ('text', str)"""
    x, y, size, fname, t, code = glyph[:6]
    ch = font_char(t)
    if 'GC2004X' in fname:
        return 'ignore', None                                    # square outlines drawn over every cell
    for rx, pieces, empties, frame in DIAGRAM_FONTS:
        if rx.search(fname):
            if ch is None:
                ch = code
            if ch in pieces:
                return 'square', pieces[ch]
            if ch in empties:
                return 'square', None
            if ch in frame:
                return 'frame', None
            if rx.pattern == 'Echecs' and 0x30 <= ch <= 0x39:
                return 'mod', None                               # zero-width marks drawn over a piece
            if ch in (0x20, 0xA0):
                return 'space', None
            return 'square', '?'
    for rx, table in FIGURINES:
        if rx.search(fname):
            return 'text', table.get(t, t)
    if re.search(r'Echecs|Diagram|Chess|Cheq', fname, re.I) and t and 0xF000 <= ord(t[0]) <= 0xF0FF:
        return 'fairy', None                                     # unmapped chess font (fairy diagrams)
    return 'text', UNICODE_FIG.get(t, SYMBOLS.get(t, t))


# ---------------------------------------------------------------- boards and text from one PDF page

def find_boards(items):
    """items: [(x, y, size, kind, piece, id)] of diagram-font glyphs, kind 'square' / 'frame' / 'space'.
    -> [board]: dict(x0, x1, top, bottom, step, cells[8][8], ids)."""
    lines, cur = [], []
    for it in sorted(items, key=lambda t: -t[1]):              # baselines
        if cur and abs(cur[0][1] - it[1]) > it[2] * 0.25:
            lines.append(cur)
            cur = []
        cur.append(it)
    if cur:
        lines.append(cur)
    rows = []
    for ln in lines:
        rows.extend(line_rows(ln))
    boards, used = [], set()
    rows.sort(key=lambda r: (-r[0][1], r[0][0]))
    for i, r in enumerate(rows):
        if i in used:
            continue
        step = (r[-1][0] - r[0][0]) / 7 or r[0][2]
        stack, last = [i], r
        for j in range(i + 1, len(rows)):
            if j in used or len(stack) == 8:
                continue
            q = rows[j]
            dy = last[0][1] - q[0][1]
            if abs(q[0][0] - r[0][0]) < step * 0.4 and 0.6 * step < dy < 1.5 * step and \
                    abs((q[-1][0] - q[0][0]) / 7 - step) < step * 0.15:
                stack.append(j)
                last = q
        if len(stack) == 8:
            used.update(stack)
            cells = [[c[4] for c in rows[j]] for j in stack]
            boards.append({'x0': r[0][0], 'x1': r[-1][0] + step, 'top': r[0][1] + step, 'bottom': rows[stack[-1]][0][1],
                           'step': step, 'cells': cells, 'ids': {i for j in stack for c in rows[j] for i in c[5]}})
    return boards


def line_rows(ln):
    """One baseline of diagram glyphs -> board rows: 8 cells (x, y, size, 'square', piece, ids) on a regular grid.
    Glyphs drawn over one another (zero-width marks, half-width parts) are merged into their cell."""
    ln = sorted((s[:3] + ('mod',) + s[4:] if s[6] < s[2] * 0.02 and s[3] != 'space' else s for s in ln),
                key=lambda s: s[0])                              # zero-width glyphs are marks over a square
    squares = [s for s in ln if s[3] in ('square', 'mod')]
    widths = sorted(s[6] for s in squares if s[3] == 'square' and s[6] > s[2] * 0.5)
    if len(widths) < 8:
        return []
    step = widths[len(widths) // 2]
    seps = [s[0] for s in ln if s[3] in ('frame', 'space')]
    rows, run, x0, last = [], {}, None, None

    def close():
        if run and sorted(run) == list(range(len(run))) and len(run) % 8 == 0:
            cells = []
            for k in range(len(run)):
                gl = run[k]
                marks = any(g[3] == 'mod' for g in gl)
                pieces = {g[4] for g in gl if g[3] == 'square' and g[4] is not None}
                parts = all(g[6] < step * 0.7 for g in gl)          # built from fragments: not a known glyph
                piece = '?' if marks or len(pieces) > 1 or '?' in pieces or (parts and gl) else \
                    (pieces.pop() if pieces else None)
                sq = [g for g in gl if g[3] == 'square']
                if not sq:
                    return
                cells.append((x0 + k * step, sq[0][1], sq[0][2], 'square', piece, tuple(g[5] for g in gl)))
            for k in range(0, len(cells), 8):
                rows.append(cells[k:k + 8])

    for s in squares:
        if x0 is not None and (s[0] - last > step * 1.4 or any(last < x <= s[0] + 0.5 for x in seps)):
            close()
            run, x0 = {}, None
        if x0 is None:
            x0 = s[0]
        k = int((s[0] - x0) / step + 0.35)
        run.setdefault(k, []).append(s)
        last = s[0]
    close()
    return rows


def text_lines(glyphs):
    """[(x, y, size, text, advance)] -> [(y, x0, x1, size, text)] top to bottom."""
    lines = []
    for g in sorted(glyphs, key=lambda g: (-g[1], g[0])):
        for ln in lines:
            if abs(ln[0] - g[1]) < max(ln[3], g[2]) * 0.35:
                ln[4].append(g)
                break
        else:
            lines.append([g[1], g[0], g[0], g[2], [g]])
    out = []
    for y, _, _, size, gs in lines:
        gs.sort(key=lambda g: g[0])
        txt, prev = '', None
        for g in gs:
            if prev is not None and g[0] - (prev[0] + prev[4]) > prev[2] * 0.18 and \
                    not txt.endswith(' ') and g[3] != ' ':
                txt += ' '
            txt += g[3]
            prev = g
        txt = re.sub(r'\s+', ' ', txt).strip().replace('ѐ', 'ё')
        if txt:
            out.append((y, gs[0][0], gs[-1][0] + gs[-1][4], size, txt))
    out.sort(key=lambda l: -l[0])
    return out


# ---------------------------------------------------------------- notation helpers

RU2EN = {'Кр': 'K', 'Ф': 'Q', 'Л': 'R', 'С': 'B', 'К': 'S', 'п': 'P'}
LAT = str.maketrans('асеохрАСЕВКМНОРТХ', 'aceoxpACEBKMHOPTX')


def english(s):
    """Russian solution notation -> English (K Q R B S)."""
    s = s.replace('…', '...').replace('×', 'x')
    s = re.sub(r'(?<![А-Яа-яЁё])([асе])(?=[1-8])', lambda m: m.group(1).translate(LAT), s)   # Cyrillic a/c/e files
    s = re.sub(r'(?<![А-Яа-яЁёA-Za-z])(Кр|Ф|Л|С|К|п)(?=[a-h]?[1-8]?[:x-]?[a-h][1-8]|[:x][a-h]|[a-h]?~)',
               lambda m: RU2EN[m.group(1)], s)
    s = re.sub(r'=(Ф|Л|С|К)', lambda m: '=' + RU2EN[m.group(1)], s)
    return s


def has_ru_pieces(s):
    return bool(re.search(r'(?<![А-Яа-яЁёA-Za-z])(Кр|Ф|Л|С|К)[a-h]?[1-8]?[:x-]?[a-h][1-8]', s))


def fen_of(cells):
    if any(c == '?' for row in cells for c in row):
        return None
    kings = [c for row in cells for c in row if c and c[1] == 'K']
    if sorted(k[0] for k in kings) != ['b', 'w']:
        return None
    rows = []
    for row in cells:
        r, e = '', 0
        for c in row:
            if c is None:
                e += 1
                continue
            letter = c[1].replace('S', 'N')
            r += (str(e) if e else '') + (letter if c[0] == 'w' else letter.lower())
            e = 0
        rows.append(r + (str(e) if e else ''))
    return '/'.join(rows)


def position_of(cells):
    side = {'w': [], 'b': []}
    for r, row in enumerate(cells):
        for f, c in enumerate(row):
            if c and c != '?':
                side[c[0]].append(('KQRBSP'.index(c[1]), c[1] + 'abcdefgh'[f] + str(8 - r)))
            elif c == '?':
                side['w'].append((9, '?' + 'abcdefgh'[f] + str(8 - r)))
    return ' '.join(t for _, t in sorted(side['w'])) + ' + ' + ' '.join(t for _, t in sorted(side['b']))


COUNT = re.compile(r'\(?\b(\d{1,2})\s*\+\s*(\d{1,2})(?:\s*\+\s*(\d{1,2}))?\)?')
STIP = re.compile(r'(?:^|\s)((?:ser-?|pser-?)?(?:h|s|r|hs|sh)?\s*[#=]\s*\d+(?:[.,]\d)?\*?|[+=]$|[+=](?=\s)|'
                  r'Мат в \d+ ход\w*|(?:Mat u|Mate in|Matt in|Mat w|Mat en) \d+|Выигрыш|Ничья|Win|Draw|Выигр\.?)', re.I)
AWARD = re.compile(r'(приз|отзыв|похвал|комменд|спец|премия|медаль|место|диплом|\bprize|\bHM\b|hon\.? ?men|comm|'
                   r'uznanie|zmienka|\bcena\b|\bprix\b|preis|\blob\b|pohvala|nagrada|mention|'
                   r'special|place|\b\d+\s*-?\s*[йя]?\s*(п\.?\s?о|пох)|\b[1-9]\s?(pr|hm|c)\b)', re.I)
NUMBER = re.compile(r'^\s*[•·*►]?\s*(?:(?:№|N[o°º]\.?|Nr\.?)\s*(\d+[a-zа-я]?)\s*\.?\s*[-–—]?\s*|'
                    r'(\d{2,5})(?:\s*[-–—]\s*(?=\*|\d\s*\.)|\.?\s+(?=[A-ZА-ЯЁ][a-zа-яё]?\.\s?[A-ZА-ЯЁ])))(.*)$')
TWIN = re.compile(r'^\s*[a-f]\)(\s|(?=[A-Za-zА-Яа-я+–-]))')
PLACE = re.compile(r"\(?[A-ZА-ЯЁ][A-Za-zА-Яа-яЁё.’'-]*(?:[ -][A-Za-zА-Яа-яЁё.’'-]+){0,2}\)?")   # a town or a country
NOT_PLACE = re.compile(r'конкурс|впервые|публику|\b[ЮМТ]К\b|турнир|мемориал|memorial|tourney|\b[JMT]T\b|олимп|'
                       r'чемпионат|кубок|журнал|problemist|проблемист|шахмат|schach|chess|приз|отзыв', re.I)
PLAY = re.compile(r'^\s*\*?\s*(\d+\s*(реш\w*|solutions?|sol)\.?|[\d.…\s]+(twins?|=\s*\d+\s*C\+|C\+)?|twins?|'
                  r'ход ч[её]рных|black to move|см\. (текст|ниже)|see (text|below)|duplex|дуплекс)\s*[.,;]?\s*$', re.I)
NOISE = re.compile(r'[CС]\+|[CС]-|\(?\w\)?|[\W\d]+|[KQRBNPkqrbnp1-8/]*/[KQRBNPkqrbnp1-8/]*|(FEN|fen):.*')
AUTHOR = re.compile(r"^([A-ZА-ЯЁ][a-zа-яё]?\.\s?){1,2}\s?[A-ZА-ЯЁ][\w'’-]+(\s*\(.*\))?(\s*[,и&]\s*([A-ZА-ЯЁ][a-zа-яё]?\.\s?)"
                    r"{1,2}\s?[A-ZА-ЯЁ][\w'’-]+(\s*\(.*\))?)*[,.]?$")


def norm_stip(s):
    s = s.strip()
    low = s.lower()
    if low.startswith(('выигр', 'win')):
        return '+'
    if low.startswith(('ничья', 'draw')):
        return '='
    m = re.match(r'(?:мат в|mat u|mate in|matt in|mat w|mat en) (\d+)', low)
    if m:
        return '#' + m.group(1)
    s = re.sub(r'\s+', '', s).replace(',', '.')
    return re.sub(r'^(p?ser)?-?([hsr]{0,2})(?=[#=])', lambda m: (m.group(1).lower() + '-' if m.group(1) else '') +
                  m.group(2).lower(), s, flags=re.I)


def parse_footer(lines):
    """Stipulation/count line(s) under a diagram -> (stip, count, twins, conditions, play)."""
    stip = count = None
    twins, conds, play = [], [], []
    for t in lines:
        t = ' ' + t.strip() + ' '
        m = COUNT.search(t)
        if count is None and m:
            count = '+'.join(g for g in m.groups() if g)
            t = t[:m.start()] + ' ' + t[m.end():]
        sm = STIP.search(t) if stip is None else None
        if sm and (sm.start() < 3 or count is not None or len(t) < 14):
            stip = norm_stip(sm.group(1))
            t = t[:sm.start()] + ' ' + t[sm.end():]
        elif stip is None and count is None and not TWIN.match(t):
            if not ftr_like(t):
                break                                        # not a footer line at all
        for seg in re.split(r'(?=\b[a-f]\))|\s{3,}', t):   # "b) Kb1", "2 решения", conditions
            seg = seg.strip(' ,;')
            if not seg:
                continue
            if TWIN.match(seg + ' '):
                twins.append(seg)
            elif PLAY.search(seg):
                play.append(seg)
            elif len(re.sub(r'\W', '', seg)) > 2 and not NOISE.fullmatch(seg) and \
                    not re.search(r'[1-8KQRBNPkqrbnp]/[1-8KQRBNPkqrbnp].*/', seg):
                conds.append(seg)
    return stip, count, twins, conds, play


def ftr_like(t):
    return bool(PLAY.search(t.strip()) or FAIRY.search(t))


def parse_header(lines):
    rec = {}
    lines = [l for l in lines if l.strip()]
    if not lines:
        return rec
    m = NUMBER.match(lines[0])
    rest = lines[1:]
    if m:
        rec['number'] = m.group(1) or m.group(2)
        if m.group(3).strip():
            rest = [m.group(3).strip()] + rest
    award, other = [], []
    for l in rest:
        (award if AWARD.search(l) and len(l) < 60 else other).append(l)
    other = [o for o in other if not re.match(r'\d+\.\s*[KQRBS]?$', o.strip())]       # stray "1." of a solution
    first = next((k for k, o in enumerate(other) if AUTHOR.match(o)), None)
    if first and re.search(r'\d', other[0]):                   # "Martin-Žilina 2000-01" above the author's name
        other.insert(0, other.pop(first))
    authors = []
    while other and (not authors or AUTHOR.match(other[0])):  # joint authors, often one per line
        authors.append(other.pop(0).strip(' ,'))
    if authors:
        rec['author'] = ', '.join(authors)
    place, source = [], []
    for o in other:
        for seg in re.split(r',\s*(?![^()]*\))', o):         # "(Россия), ЮК А. Селиванов-50"
            seg = seg.strip(' ,')
            if not seg:
                continue
            if PLACE.fullmatch(seg) and not NOT_PLACE.search(seg):
                place.append(seg.strip('()'))
            else:
                source.append(seg)
    if place:
        rec['place'] = ', '.join(place)
    if source:
        rec['source'] = ', '.join(source)
    if award:
        rec['award'] = ', '.join(award)
    return rec


# ---------------------------------------------------------------- one PDF -> records

def pdf_records(path, url):
    data = open(path, 'rb').read()
    if not data.startswith(b'%PDF') or b'/Encrypt' in data[-4000:]:
        return [], {'error': 'not a readable PDF'}
    pdf = PDF(data)
    fonts_cache = {}
    recs, doc_lines, zones, stats = [], [], [], {'boards': 0, 'fairy_font': 0}
    title = None
    pages = []
    for page in pdf.pages():
        try:
            pages.append(page_glyphs(pdf, page, fonts_cache))
        except RecursionError:
            pages.append([])
    alias = anonymous_diagram_fonts(pages)
    for pn, glyphs in enumerate(pages):
        if alias:
            glyphs = [g[:3] + ('ISDiagram',) + g[4:] if g[3] in alias else g for g in glyphs]
        squares, text, fairy = [], [], 0
        for n, g in enumerate(glyphs):
            kind, val = classify(g)
            if kind in ('square', 'frame', 'space', 'mod'):
                squares.append((g[0], g[1], g[2], kind, val, n, g[6]))
            elif kind == 'text' and val:
                text.append((g[0], g[1], g[2], val, g[6]))
            elif kind == 'fairy':
                fairy += 1
        stats['fairy_font'] += fairy
        boards = find_boards(squares)
        used = set().union(*(b['ids'] for b in boards)) if boards else set()
        for sq in squares:                     # diagram-font glyphs outside boards are figurines in the text
            if sq[5] in used:
                continue
            g = glyphs[sq[5]]
            fig = next((t for rx, t in FIGURINES if rx.search(g[3])), None)
            if sq[3] == 'frame':
                continue
            if fig is not None:
                text.append((sq[0], sq[1], sq[2], fig.get(g[4], g[4]), g[6]))
            elif sq[3] == 'square' and sq[4] and sq[4] != '?':
                text.append((sq[0], sq[1], sq[2], sq[4][1], g[6]))
            elif sq[3] == 'space':
                text.append((sq[0], sq[1], sq[2], ' ', g[6]))
        stats['boards'] += len(boards)
        lines = text_lines(text)
        if title is None:
            for l in lines:
                t = re.split(r'\s№\s*\d', l[4])[0].strip()
                if len(t) > 3 and not NUMBER.match(t):
                    title = t
                    break
        # column limits for boards that share a band
        for b in boards:
            peers = sorted((o for o in boards if not (o['bottom'] > b['top'] or o['top'] < b['bottom'])),
                           key=lambda o: o['x0'])
            k = peers.index(b)
            b['cx0'] = (peers[k - 1]['x1'] + b['x0']) / 2 if k else b['x0'] - 4 * b['step']
            b['cx1'] = (peers[k + 1]['x0'] + b['x1']) / 2 if k + 1 < len(peers) else b['x1'] + 4 * b['step']
        for b in boards:
            col = [g for g in text if b['cx0'] <= g[0] < b['cx1']]
            above = [g for g in col if b['top'] - b['step'] * 0.5 < g[1] < b['top'] + b['step'] * 7]
            # stop the header at the previous board's footer: the nearest board above in this column
            higher = [o for o in boards if o is not b and o['bottom'] > b['top'] and
                      not (o['x1'] < b['cx0'] or o['x0'] > b['cx1'])]
            if higher:
                lim = min(o['bottom'] for o in higher) - max(o['step'] for o in higher) * 2.2
                above = [g for g in above if g[1] < lim]
            cand = list(reversed(text_lines(above)))[:7]      # nearest first
            hdr_l = []
            for k, l in enumerate(cand):                          # a numbered header: take it whole
                if NUMBER.match(l[4]) and all(cand[j][0] - cand[j + 1][0] < cand[j][3] * 2.2 for j in range(k)):
                    hdr_l = cand[:k + 1]
                    break
            if not hdr_l:
                for l in cand:                                   # else: contiguous short lines above the board
                    if (hdr_l and hdr_l[-1][0] - l[0] > l[3] * 1.9) or len(hdr_l) == 4 or \
                            crosses(l, b, boards, text) or re.search(r'\b1\.\s*\S{0,2}[a-h][1-8]', l[4]):
                        break
                    hdr_l.append(l)
            hdr_l = hdr_l[::-1]
            hdr = [l[4] for l in hdr_l]
            below = [g for g in col if b['bottom'] - b['step'] * 5 < g[1] < b['bottom'] - b['step'] * 0.4]
            ftr_l = []
            for l in text_lines(below):
                if (ftr_l and ftr_l[-1][0] - l[0] > l[3] * 1.9) or re.search(r'\b1\.\s*\S{0,2}[a-h][1-8]', l[4]) \
                        or NUMBER.match(l[4]) or crosses(l, b, boards, text):
                    break
                ftr_l.append(l)
            ftr_l = ftr_l[:4]
            ftr = [l[4] for l in ftr_l]
            ztop = max([l[0] + l[3] * 0.5 for l in hdr_l] + [b['top']])
            zbot = min([l[0] - l[3] * 0.3 for l in ftr_l] + [b['bottom'] - b['step'] * 0.2])
            rec = parse_header(hdr)
            stip, count, twins, conds, play = parse_footer(ftr)
            if count is None:                                    # count sometimes sits in the header
                for h in hdr:
                    if COUNT.fullmatch(h.strip()):
                        count = COUNT.fullmatch(h.strip()).group(0).strip('()').replace(' ', '')
            cells = b['cells']
            fen = fen_of(cells)
            if count is None:
                w = sum(1 for row in cells for c in row if c and c[0] == 'w')
                bl = sum(1 for row in cells for c in row if c and c[0] == 'b')
                count = f'{w}+{bl}'
            r = {'position': position_of(cells), 'fen': fen, 'stip': stip, 'count': count}
            r.update(rec)
            if twins:
                r['twins'] = [english(t) for t in twins]
            if conds:
                r['conditions'] = conds
            if play:
                r['play'] = ' '.join(play)
            r['_page'], r['_pos'] = pn, (pn, -zbot)           # where the text after this diagram starts
            recs.append(r)
            zones.append((pn, ztop, zbot, b['cx0'], b['cx1']))
        for l in lines:
            doc_lines.append((pn, l))
    # running text (outside the diagram zones) for solutions
    running, starts = [], []
    for pn, (y, x0, x1, size, txt) in doc_lines:
        inzone = any(pn == z[0] and z[2] < y < z[1] and x0 < z[4] and x1 > z[3] for z in zones)
        if not inzone:
            running.append(txt)
        elif running and running[-1] != ZONE:
            running.append(ZONE)                                 # a diagram block interrupts the text here
        else:
            continue
        starts.append((pn, -y))
    sol_index = solution_paragraphs(running)
    stats['numbered'] = [(num, sol) for num, occ in sol_index.items() for _, sol in occ if sol]
    for r in recs:
        num = r.get('number')
        # numbers restart in every section of an award: prefer the paragraph that follows this diagram
        here = next((k for k, st in enumerate(starts) if st > r['_pos']), len(starts))
        occ = sol_index.get(num, []) if num else []
        cands = [o[1] for o in occ if o[0] >= here and o[1]] + [o[1] for o in reversed(occ) if o[0] < here and o[1]]
        # unnumbered layouts: the solution is printed right under the diagram
        tail = []
        for ln in running[here:here + 12]:
            if NUMBER.match(ln) or ln == ZONE:
                break
            tail.append(ln)
        numbered = len(cands)
        m = MOVE_START.search(' '.join(tail))
        if m and cut_commentary(' '.join(tail)[m.start():]):
            cands.append(cut_commentary(' '.join(tail)[m.start():]))
        # keep the first candidate whose first move fits the diagram, in English or in German notation
        chosen = next(((c, f) for c in cands for f in ((german, english) if looks_german(c) else (english, german))
                       if first_moves_ok(r['fen'], r.get('stip'), f(c))), None)
        if chosen is None:                   # nothing to verify against (fairy piece, no move): trust the number
            chosen = next(((c, german if looks_german(c) else english) for c in cands[:numbered]
                           if first_moves_ok(r['fen'], r.get('stip'), english(c)) is None), (None, None))
        sol, conv = chosen
        if sol:
            if has_ru_pieces(sol):
                r['solution_ru'] = sol
            elif conv is german:
                r['solution_de'] = sol
            r['solution'] = conv(sol)
    for r in recs:
        r['source_doc'] = title
        if not r.get('source') and title:
            r['source'] = title
        r['page'] = url + '#page=%d' % (r.pop('_page') + 1)
        r.pop('_pos')
    return recs, stats


LINES = {'N': (), 'K': (), 'R': ((1, 0), (-1, 0), (0, 1), (0, -1)), 'B': ((1, 1), (1, -1), (-1, 1), (-1, -1))}
LINES['Q'] = LINES['R'] + LINES['B']


FIRST_MOVE = re.compile(r'(?<![\d.])1\.\s*(?!\.)([KQRBSP]?)([a-h]?[1-8]?)[:x-]?([a-h][1-8])')


def first_moves_ok(fen, stip, sol, every=False):
    """Can the first move of the solution (every first move: tries and key, with every=True) be played in this
    diagram?  -> True / False, or None when there is nothing to test.  With every=True -> number of moves checked
    when all of them fit, else False."""
    moves = list(FIRST_MOVE.finditer(sol or ''))
    if not fen or not moves:
        return None
    board = {}
    for r, row in enumerate(fen.split('/')):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                board[(f, 7 - r)] = ch
                f += 1
    white = not (stip or '').startswith('h')                  # helpmates start with Black
    for m in (moves if every else moves[:1]):
        if not move_fits(board, white, (m.group(1) or 'P').replace('S', 'N'), m.group(2),
                         ('abcdefgh'.index(m.group(3)[0]), int(m.group(3)[1]) - 1)):
            return False
    return len(moves) if every else True


def move_fits(board, white, p, hint, to):
    for (fx, fy), c in board.items():
        if c != (p if white else p.lower()):
            continue
        dx, dy = to[0] - fx, to[1] - fy
        if hint and hint not in 'abcdefgh'[fx] + str(fy + 1):
            continue
        if p == 'N' and sorted((abs(dx), abs(dy))) == [1, 2] or p == 'K' and max(abs(dx), abs(dy)) == 1:
            return True
        if p == 'P':
            d = 1 if white else -1
            if (dx == 0 and (dy == d or dy == 2 * d and fy == (1 if white else 6))) or (abs(dx) == 1 and dy == d):
                return True
        for ux, uy in LINES.get(p, ()):
            x, y = fx + ux, fy + uy
            while 0 <= x < 8 and 0 <= y < 8:
                if (x, y) == to:
                    return True
                if (x, y) in board:
                    break
                x, y = x + ux, y + uy
    return False


def anonymous_diagram_fonts(pages):
    """Fonts renamed on export (TT1234o00, TTE1A2B3Ct00...) that are really ISDiagram: they only use its
    characters, with its empty squares and frames."""
    used = {}
    for glyphs in pages:
        for g in glyphs:
            if not any(rx.search(g[3]) for rx, *_ in DIAGRAM_FONTS) and not any(rx.search(g[3]) for rx, _ in FIGURINES):
                used.setdefault(g[3], set()).add(font_char(g[4]) if g[4] else None)
    out = set()
    for name, chars in used.items():
        chars.discard(0x20)
        if chars and all(c is not None and 0x21 <= c <= 0x50 for c in chars) and \
                ({0x3F, 0x40} <= chars or {0x39, 0x3A} <= chars) and ({0x49, 0x4A} <= chars or {0x3B, 0x3C} <= chars):
            out.add(name)
    return out


def crosses(line, b, boards, text):
    """Does the page line at this height run across the column limits (i.e. is it body text, not a header)?"""
    y = line[0]
    for lim in (b['cx0'], b['cx1']):
        if any(abs(g[1] - y) < g[2] * 0.35 and g[3].strip() and g[0] < lim < g[0] + g[4] + g[2] * 0.3
               for g in text):
            return True
    return False


MOVE_START = re.compile(r'(\*\s*1\s*\.\s*\.\.\.|\*?\s*1\s*\.\s*\.\.\.|\*?\s*1\s*…|\b1\s*\.\s*(?=[A-Za-zА-Яа-я~?]|\.\.\.)|'
                        r'\*\s*1\s*\.|(?<![\d.])1\.(?=[a-hKQRBSPКрФЛСп]))')


def is_movey(s):
    letters = re.findall(r'[A-Za-zА-Яа-яЁё]', s)
    if not letters:
        return True
    cyr = sum(1 for c in letters if 'А' <= c <= 'я' or c in 'Ёё')
    moves = len(re.findall(r'[a-h][1-8]', s))
    return cyr / len(letters) < 0.45 or moves * 4 > len(s.split())


ZONE = '\x00'


def cut_commentary(tail):
    """Solution text up to the first sentence that is plain Russian commentary."""
    parts = re.split(r'(?<=[.!?»)])\s+(?=[А-ЯЁ](?:[а-яё]|\s+[а-яё]{2}))', tail)
    keep = []
    for p in parts:
        if keep and not is_movey(p):
            break
        keep.append(p)
    sol = ' '.join(keep).strip()
    # runs of Russian words: dropped when more moves follow (inline remarks), else the solution ends there
    for m in reversed(list(re.finditer(r'(?:(?<![\w(])[А-ЯЁа-яё]+\b[\s,.;:!?–-]*){3,}', sol))):
        if len(m.group(0)) < 12 or m.start() < 4:
            continue
        if re.search(r'\d\.\s*\S{0,6}[a-h][1-8]', sol[m.end():]):
            sol = sol[:m.start()] + ' ' + sol[m.end():]
        else:
            sol = sol[:m.start()]
    sol = re.sub(r'\s+', ' ', sol).strip(' ,;:–-')
    return sol if len(sol) >= 4 else None


def looks_german(s):
    return len(re.findall(r'(?<![A-Za-z])[DTL][a-h]?[1-8]?[:x-]?[a-h][1-8]', s)) > \
        len(re.findall(r'(?<![A-Za-z])[QR][a-h]?[1-8]?[:x-]?[a-h][1-8]', s))


DE2EN = {'D': 'Q', 'T': 'R', 'L': 'B', 'S': 'S', 'K': 'K', 'B': 'P'}


def german(s):
    """German notation (K D T L S B) -> English."""
    s = english(s)
    s = re.sub(r'(?<![A-Za-z])([DTLB])(?=[a-h]?[1-8]?[:x-]?[a-h][1-8]|[:x][a-h]|[a-h]?~)', lambda m: DE2EN[m.group(1)], s)
    return re.sub(r'=([DTL])\b', lambda m: '=' + DE2EN[m.group(1)], s)


def solution_paragraphs(lines):
    """{problem number: [(line index, solution text or None), ...]} from the running text lines."""
    out, cur, buf, at = {}, None, [], 0

    def flush():
        if cur is None:
            return
        para = ' '.join(buf)
        m = MOVE_START.search(para)
        sol = cut_commentary(para[m.start():]) if m else None
        out.setdefault(cur, []).append((at, sol))

    for k, ln in enumerate(lines):
        if ln == ZONE:
            continue
        m = NUMBER.match(ln)
        if m:
            flush()
            cur, buf, at = m.group(1) or m.group(2), [m.group(3)], k
        elif cur is not None:
            buf.append(ln)
    flush()
    return out


FAIRY = re.compile(r'circe|цирце|madras|мадрас|grassh|кузнеч|nightrider|ночн|andernach|андернах|isardam|patrol|'
                   r'maxi|mini|kamikaze|ghost|take ?& ?make|zero|нуль|koko|coco|anti|функцион|functionar|ser-?|'
                   r'sat\b|masand|transmut|vao|pao|leo|lion|equihopper|royal|neutral|нейтрал', re.I)
FIELDS = ('position', 'fen', 'stip', 'count', 'author', 'place', 'source', 'award', 'number', 'twins', 'conditions',
          'play', 'solution', 'solution_ru', 'solution_de', 'solution_page', 'orthodox', 'page', 'also_on', 'source_doc',
          'listed_as')
ORTHO_STIP = r'(ser-)?(h|s|r)?#\d+(\.5)?\*?|[+=]'
NOTE = ('Problems extracted from the PDF awards and magazine issues on selivanov.world (A. Selivanov, '
        '"Уральский проблемист"). The site shows diagrams as pictures, but its PDFs are typeset with chess '
        'diagram fonts, so boards are rebuilt from the font glyphs. Positions and solutions use English '
        'piece letters (K Q R B S P); solution_ru keeps the original where Russian letters were converted. '
        'page is the PDF URL with #page=N; also_on lists other documents showing the same diagram.')


def parse(mirror):
    """-> (records, stats) for every document in the mirror."""
    index = {}
    for line in open(os.path.join(mirror, '_index.tsv'), encoding='utf-8'):
        u, st, lp = (line.rstrip('\n').split('\t') + ['', ''])[:3]
        if st == '200' and lp:
            index[lp] = u
    anchors = link_texts(mirror, index)
    out, stats = [], {'documents': 0, 'with_problems': 0, 'boards': 0, 'no_boards': [], 'errors': []}
    # Word files (.doc) are mirrored too, but their diagrams are embedded pictures: only PDFs are read
    docs = [(lp, os.path.join(mirror, lp), index[lp]) for lp in sorted(index) if lp.lower().endswith('.pdf')]
    with multiprocessing.Pool() as pool:                         # documents are independent: use all cores
        results = pool.map(doc_records, docs, chunksize=1)
    solutions = {}                                               # (series, number) -> [(url, solution)]
    for (lp, _, url), (recs, numbered, err) in zip(docs, results):
        for num, sol in numbered:
            solutions.setdefault((series(lp), num), []).append((url, sol))
    for (lp, _, url), (recs, numbered, err) in zip(docs, results):
        stats['documents'] += 1
        for r in recs:
            if not r.get('solution') and r.get('number') and r['fen']:
                link_solution(r, solutions.get((series(lp), r['number']), []), url)
        if err:
            stats['errors'].append(f'{lp}: {err}')
        elif recs:
            if url in anchors:
                for r in recs:
                    r['listed_as'] = anchors[url]
            stats['with_problems'] += 1
            stats['boards'] += len(recs)
            out.extend(recs)
        else:
            stats['no_boards'].append(lp)
    return out, stats


def series(lp):
    """Magazine a document belongs to (its problem numbers run on across issues), else the document itself."""
    parts = lp.split('/')
    if len(parts) > 2 and parts[:2] == ['download', 'Magazins']:
        return {'UrPro': 'UP'}.get(parts[2], parts[2])
    if len(parts) > 1 and parts[0] == 'download' and parts[1] in ('SK', 'UP'):
        return parts[1]
    return lp


def length_fits(stip, sol):
    """The last move number of the solution must be the one the stipulation asks for (#3 -> '3.')."""
    m = re.search(r'[#=](\d+)', stip or '')
    nums = [int(k) for k in re.findall(r'(?<![\d.])(\d{1,2})\.(?!\d)', sol)]
    return bool(m and nums) and max(nums) == int(m.group(1)) + (1 if re.search(r'\.5', stip) else 0)


def link_solution(r, cands, url):
    """Solutions of magazine originals are printed in later issues: take one whose every first move (tries and
    key) fits the diagram, and at least two of them, so that a stray number cannot attach a foreign solution."""
    for src, sol in cands:
        for conv in ((german, english) if looks_german(sol) else (english, german)):
            n = first_moves_ok(r['fen'], r.get('stip'), conv(sol), every=True)
            if n and n >= 2 and length_fits(r.get('stip'), sol):
                if has_ru_pieces(sol):
                    r['solution_ru'] = sol
                elif conv is german:
                    r['solution_de'] = sol
                r['solution'] = conv(sol)
                if src != url:
                    r['solution_page'] = src
                return


def doc_records(job):
    lp, path, url = job
    try:
        recs, stats = pdf_records(path, url)
        return recs, stats.get('numbered', []), None
    except Exception as e:                                       # one broken file must not stop the run
        return [], [], f'{type(e).__name__}: {e}'


def link_texts(mirror, index):
    """document URL -> 'page heading: link text' of the first site page that links to it."""
    out = {}
    for lp, url in sorted(index.items()):
        if not lp.endswith('.html'):
            continue
        try:
            page = open(os.path.join(mirror, lp), encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S | re.I)
        h1 = text_of(h1.group(1)) if h1 else ''
        body = page[page.find('<h1'):] if '<h1' in page else page
        for m in re.finditer(r'<a\s[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', body, re.S | re.I):
            target = canon(m.group(1), url)
            if not target or target in out or not urllib.parse.unquote(target).lower().endswith(DOCS):
                continue
            label = text_of(m.group(2))
            # the anchor alone is often just "pdf" or "#2": add the text before it on the same line
            prefix = body[:m.start()]
            cut = max(prefix.lower().rfind(t) for t in ('<br', '<p', '<tr', '<li', '<td', '</td', '<h'))
            before = text_of(prefix[max(cut, m.start() - 300):]) if cut >= 0 else ''
            before = re.sub(r'^[^<]*>', '', before)
            if len(label) < 12 and before:
                label = (before.split('\n')[-1] + ' ' + label).strip()
            out[target] = (h1 + ': ' if h1 else '') + label
    return out


def text_of(fragment):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', fragment, flags=re.S | re.I)
    t = re.sub(r'<br\s*/?>|</p>|</div>|</td>|</li>', '\n', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '', t)).replace('\xa0', ' ')
    return '\n'.join(l for l in (re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')) if l)


def best(recs):
    """Among copies of one diagram keep the most informative one, remember where the others are."""
    def score(r):
        return (bool(r.get('solution')), bool(r.get('award')), bool(r.get('author')), bool(r.get('stip')),
                len(r.get('solution') or ''))
    recs = sorted(recs, key=score, reverse=True)
    keep = dict(recs[0])
    for r in recs[1:]:                                           # fill gaps from the other copies
        for k in ('stip', 'count', 'author', 'place', 'award', 'source', 'number', 'twins', 'conditions', 'play'):
            if not keep.get(k) and r.get(k):
                keep[k] = r[k]
    also = sorted({r['page'] for r in recs[1:]} - {keep['page']})
    if also:
        keep['also_on'] = also
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'parse'])
    ap.add_argument('mirror')
    ap.add_argument('-o', '--out', default=os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'knowledge',
                                                                        'selivanov.json')))
    ap.add_argument('--limit', type=int, help='crawl: stop after this many requests')
    ap.add_argument('-v', '--verbose', action='store_true', help='parse: list documents without diagrams')
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.mirror, limit=a.limit)
        return
    recs, stats = parse(a.mirror)
    groups = {}
    for r in recs:                      # the same diagram reappears in originals, awards and reprints
        key = (r['fen'] or r['position'], str(r.get('conditions', '')).lower())
        groups.setdefault(key, {}).setdefault(r.get('stip'), []).append(r)
    merged = []
    for by_stip in groups.values():     # a copy whose stipulation was not read joins the most common one
        loose = by_stip.pop(None, [])
        if by_stip:
            max(by_stip.values(), key=len).extend(loose)
        elif loose:
            by_stip[None] = loose
        merged.extend(by_stip.values())
    uniq = []
    for g in merged:
        r = best(g)
        r['orthodox'] = bool(r['fen']) and not r.get('conditions') and \
            not any(FAIRY.search(t) for t in r.get('twins', [])) and bool(re.fullmatch(ORTHO_STIP, r.get('stip') or '#2'))
        uniq.append({k: r[k] for k in FIELDS if k in r})
    doc = {'source': BASE + '/', 'note': NOTE, 'count': len(uniq), 'problems': uniq}
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    out = a.out
    if len(text.encode('utf-8')) > 50 << 20:
        out = out if out.endswith('.gz') else out + '.gz'
        with gzip.open(out, 'wt', encoding='utf-8') as f:
            f.write(text)
    else:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text)
    orth = [r for r in uniq if r['orthodox']]
    print(f"{stats['documents']} documents, {stats['with_problems']} with diagrams, {len(recs)} diagrams, "
          f"{len(uniq)} unique, {len(orth)} orthodox, {sum(1 for r in uniq if r.get('solution'))} with solution "
          f"-> {out}", file=sys.stderr)
    for e in stats['errors']:
        print('error:', e, file=sys.stderr)
    if a.verbose:
        for lp in stats['no_boards']:
            print('no diagrams:', lp, file=sys.stderr)


if __name__ == '__main__':
    main()
