"""Crawl the site of the French problem magazine Phénix (www.phenix-echecs.fr) and extract its problems.

Where the problems live:
  * PDFs (la_revue/telechargement_inedits/, la_revue/telechargement/, articles/*.pdf, errata, demolition and
    solving contests, tourney announcements): the originals ("inédits") of many issues, most of them followed
    by the solutions, three complete issues, several awards.  They are typeset with the 1Echecs chess font, so
    a diagram is text: every board row is a run of font glyphs.  A small stdlib-only PDF reader (objects and
    object streams, Flate/ASCIIHex/ASCII85, font widths, ToUnicode maps, the text operators) recovers the
    glyphs with their coordinates; the boards are rebuilt from them, and the text around each board gives the
    number, author(s), source/award, stipulation, piece count, twins and conditions.  Numbered solution
    paragraphs ("10177 - Abdelaziz Onkoud" + moves + comment) are attached by problem number.
  * HTML award pages (la_revue/articles/*.php, "jugements"): the diagram of the winner of each section as a
    picture, with author, source, award, stipulation, twins, the judge's comment and the solution as text.
    The pictures are decoded (baseline JPEG, PNG and GIF readers, luminance only) and every square is
    matched against reference patches of the diagram font's pieces.
  * Skipped: pictures of other kinds, scanned PDFs, PDFs set without a chess font (diagram pictures), the
    solutions quoted in running award text (not keyed by number), and anything members-only (there is none
    public: the paper issues are only sold).

usage:
    python tools/phenix.py crawl  MIRROR_DIR              # polite: 1 request/s, resumable, stays on the host
    python tools/phenix.py parse  MIRROR_DIR [-o OUT]     # -> knowledge/phenix.json (.json.gz if > 50 MB)
"""
import argparse, gzip, html, json, math, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request, zlib
from collections import deque

HOST = 'www.phenix-echecs.fr'
BASE = 'https://' + HOST
SEEDS = ['/', '/index.html', '/la_revue/la_revue.php', '/la_revue/jugements.php', '/la_revue/index_auteurs.php',
         '/la_revue/concours_demolitions.php', '/la_revue/la_revue_errata.php', '/divers/resultats_de_concours.php',
         '/divers/concours_solutions.php', '/divers/articles.php', '/Messigny/AFCE.php', '/FIDE/FIDE.php'] + \
        ['/la_revue/la_revue_%d.php' % y for y in range(2016, 2027)]
UA = 'ChessProblemHelper-crawler/1.0 (+personal chess-problem study archive; 1 req/s)'
KEEP = re.compile(r'(\.(php|html?|pdf)|/)$', re.I)
SKIP = re.compile(r'SpryAssets|/boutons/|mailto:|javascript:', re.I)
DIAGRAM = re.compile(r'diagramm?es?/[^/]+\.(jpe?g|png|gif)$', re.I)     # award pages: the diagrams are pictures
FR2EN = {'R': 'K', 'D': 'Q', 'T': 'R', 'F': 'B', 'C': 'S', 'P': 'P'}


# ---------------------------------------------------------------- crawl

def local_path(out, url):
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path)
    path = path + 'index.html' if path.endswith('/') else path
    return os.path.join(out, path.lstrip('/'))


def crawl(out, delay=1.0):
    """Breadth-first over every on-host HTML page, downloading the linked PDFs and the diagram pictures of
    the award pages too. Files already in the mirror are not fetched again (an interrupted crawl can simply
    be restarted)."""
    seen, queue, fetched = set(), deque(BASE + s for s in SEEDS), 0
    while queue:
        url = urllib.parse.urldefrag(queue.popleft())[0]
        if url in seen:
            continue
        seen.add(url)
        dest = local_path(out, url)
        if os.path.exists(dest):
            body = open(dest, 'rb').read()
        else:
            body = None
            for attempt in range(3):                   # the server sometimes resets the connection
                try:
                    req = urllib.request.Request(urllib.parse.quote(url, safe=':/?&=%#+'), headers={'User-Agent': UA})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        if urllib.parse.urlparse(r.geturl()).netloc == HOST:
                            body = r.read()
                    break
                except urllib.error.HTTPError as e:
                    print('skip', url, e, file=sys.stderr)
                    break
                except Exception as e:
                    print('retry' if attempt < 2 else 'skip', url, e, file=sys.stderr)
                    time.sleep(delay * 5 * (attempt + 1))
            if body is None:
                time.sleep(delay)
                continue
            fetched += 1
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                f.write(body)
            time.sleep(delay)
        if not re.search(r'\.(php|html?)$', dest, re.I):
            continue
        text = body.decode('utf-8', 'replace')
        text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
        links = re.findall(r"""href\s*=\s*["']([^"'>]+)["']""", text, re.I)
        links += [s for s in re.findall(r"""<img[^>]*?src\s*=\s*["']([^"'>]+)["']""", text, re.I) if DIAGRAM.search(s)]
        for link in links:
            link = html.unescape(link.strip())
            if SKIP.search(link):
                continue
            nxt = urllib.parse.urldefrag(urllib.parse.urljoin(url, link))[0]
            p = urllib.parse.urlparse(nxt)
            if p.netloc in (HOST, HOST[4:]) and p.scheme in ('http', 'https') and not p.query and \
                    (KEEP.search(p.path) or DIAGRAM.search(p.path)):
                queue.append(BASE + re.sub(r'^(/\.\.)+', '', p.path))
    print(len(seen), 'urls visited,', fetched, 'fetched', file=sys.stderr)


# ---------------------------------------------------------------- a tiny PDF text reader (stdlib only)

OBJ_START = re.compile(rb'(?<![\d])(\d+)\s+(\d+)\s+obj\b')


class PDF:
    """Just enough of PDF to get the positioned glyphs back: objects (also inside object streams),
    Flate/ASCIIHex/ASCII85 streams, fonts with their widths and ToUnicode maps, pages and forms."""

    def __init__(self, data):
        self.objs = {}
        starts = list(OBJ_START.finditer(data))
        for m, nxt in zip(starts, starts[1:] + [None]):
            body = data[m.end():nxt.start() if nxt else len(data)]
            e = body.rfind(b'endobj')
            self.objs[int(m.group(1))] = body[:e] if e >= 0 else body
        for n, body in list(self.objs.items()):
            head = self.head(n)
            if re.search(rb'/Type\s*/ObjStm', head):
                try:
                    self._objstm(n, head)
                except Exception:
                    pass

    def _objstm(self, n, head):
        s = self.stream(n)
        first = int(re.search(rb'/First\s+(\d+)', head).group(1))
        count = int(re.search(rb'/N\s+(\d+)', head).group(1))
        nums = [int(x) for x in s[:first].split()[:2 * count]]
        pairs = list(zip(nums[::2], nums[1::2]))
        for k, (num, off) in enumerate(pairs):
            end = pairs[k + 1][1] if k + 1 < len(pairs) else len(s) - first
            self.objs.setdefault(num, s[first + off:first + end])

    def head(self, n):
        b = self.objs.get(n, b'')
        m = re.search(rb'>>\s*stream\b', b)
        return b[:m.start() + 2] if m else b

    def stream(self, n):
        b = self.objs.get(n, b'')
        m = re.search(rb'>>\s*stream\r?\n?', b)
        if not m:
            return b''
        head, raw = b[:m.start() + 2], b[m.end():]
        e = raw.rfind(b'endstream')
        raw = raw[:e] if e >= 0 else raw
        filters = re.findall(rb'/(FlateDecode|Fl|ASCIIHexDecode|AHx|ASCII85Decode|A85|LZWDecode|DCTDecode|'
                             rb'CCITTFaxDecode|JBIG2Decode|JPXDecode|RunLengthDecode)\b',
                             re.search(rb'/Filter\s*(\[[^\]]*\]|/\w+)', head).group(1)
                             if re.search(rb'/Filter', head) else b'')
        for f in filters:
            try:
                if f in (b'FlateDecode', b'Fl'):
                    raw = zlib.decompressobj().decompress(raw)
                elif f in (b'ASCIIHexDecode', b'AHx'):
                    h = re.sub(rb'[^0-9A-Fa-f]', b'', raw.split(b'>')[0])
                    raw = bytes.fromhex((h + b'0' * (len(h) % 2)).decode())
                elif f in (b'ASCII85Decode', b'A85'):
                    import base64
                    raw = base64.a85decode(re.sub(rb'\s', b'', raw).split(b'~>')[0] + b'~>', adobe=True)
                else:
                    return b''
            except Exception:
                return b''
        return raw

    def ref(self, s, key):
        m = re.search(rb'/' + key + rb'\s+(\d+)\s+\d+\s+R', s)
        return int(m.group(1)) if m else None

    def sub(self, s, key):
        """The body of the dictionary /key << ... >> (inline or referenced) inside s."""
        m = re.search(rb'/' + key + rb'\s*(\d+\s+\d+\s+R|<<)', s)
        if not m:
            return b''
        if m.group(1) != b'<<':
            return self.head(int(m.group(1).split()[0]))
        i = j = m.end()
        depth = 1
        while depth and j < len(s):
            if s[j:j + 2] == b'<<':
                depth += 1
                j += 2
            elif s[j:j + 2] == b'>>':
                depth -= 1
                j += 2
            else:
                j += 1
        return s[i:j - 2]

    def pages(self):
        order, seen = [], set()

        def walk(n):
            if n in seen:
                return
            seen.add(n)
            d = self.head(n)
            if re.search(rb'/Type\s*/Pages\b', d):
                kids = re.search(rb'/Kids\s*\[(.*?)\]', d, re.S)
                for k in re.findall(rb'(\d+)\s+\d+\s+R', kids.group(1)) if kids else []:
                    walk(int(k))
            elif re.search(rb'/Type\s*/Page\b', d):
                order.append(n)
        cat = [n for n in self.objs if re.search(rb'/Type\s*/Catalog\b', self.head(n))]
        for c in cat:
            r = self.ref(self.head(c), rb'Pages')
            if r:
                walk(r)
        return order


def parse_cmap(s):
    m = {}
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', s, re.S):
        for a, b, c in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f\s]*>|\[[^\]]*\])', blk):
            c = re.sub(rb'\s', b'', c) if c.startswith(b'<') else c
            a, b = int(a, 16), int(b, 16)
            if c.startswith(b'['):
                for k, h in enumerate(re.findall(rb'<([0-9A-Fa-f\s]*)>', c)):
                    m[a + k] = bytes.fromhex(re.sub(rb'\s', b'', h).decode()).decode('utf-16-be', 'replace')
                continue
            c = bytes.fromhex(c[1:-1].decode()).decode('utf-16-be', 'replace')
            for k in range(a, min(b, a + 4096) + 1):
                m[k] = c[:-1] + chr(ord(c[-1]) + k - a) if c else ''
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', s, re.S):
        for a, b in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f\s]*)>', blk):
            m[int(a, 16)] = bytes.fromhex(re.sub(rb'\s', b'', b).decode()).decode('utf-16-be', 'replace')
    return m


GLYPHS = {'quoteright': '’', 'quoteleft': '‘', 'endash': '–', 'emdash': '—', 'multiply': '×', 'ellipsis': '…',
          'guillemotleft': '«', 'guillemotright': '»', 'degree': '°', 'quotedblleft': '“', 'quotedblright': '”',
          'bullet': '•', 'space': ' ', 'hyphen': '-', 'period': '.', 'comma': ',', 'colon': ':', 'semicolon': ';',
          'parenleft': '(', 'parenright': ')', 'plus': '+', 'equal': '=', 'slash': '/', 'exclam': '!',
          'question': '?', 'numbersign': '#', 'quotesingle': "'", 'bracketleft': '[', 'bracketright': ']',
          'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7',
          'eight': '8', 'nine': '9', 'asterisk': '*', 'greater': '>', 'less': '<', 'dagger': '†',
          'daggerdbl': '‡', 'section': '§', 'underscore': '_', 'percent': '%', 'ampersand': '&',
          'arrowright': '→', 'uni00A0': ' ', 'nbspace': ' ', 'minus': '−', 'quotedbl': '"', 'periodcentered': '·'}


def glyph_char(name):
    if name in GLYPHS:
        return GLYPHS[name]
    if re.fullmatch(r'uni[0-9A-Fa-f]{4}', name):
        return chr(int(name[3:], 16))
    if '_' in name:
        return ''.join(glyph_char(p) for p in name.split('_'))
    if len(name) == 1:
        return name
    import unicodedata
    base = {'acute': '́', 'grave': '̀', 'circumflex': '̂', 'dieresis': '̈', 'caron': '̌',
            'cedilla': '̧', 'tilde': '̃', 'ring': '̊', 'ogonek': '̨', 'breve': '̆',
            'hungarumlaut': '̋', 'dotaccent': '̇', 'macron': '̄'}
    for acc, comb in base.items():
        if name.endswith(acc) and len(name) == len(acc) + 1:
            return unicodedata.normalize('NFC', name[0] + comb)
    return {'oe': 'œ', 'OE': 'Œ', 'ae': 'æ', 'AE': 'Æ', 'germandbls': 'ß', 'fi': 'fi', 'fl': 'fl', 'ff': 'ff',
            'ffi': 'ffi', 'ffl': 'ffl', 'dotlessi': 'ı', 'lslash': 'ł', 'Lslash': 'Ł', 'oslash': 'ø',
            'Oslash': 'Ø', 'dcroat': 'đ', 'Dcroat': 'Đ'}.get(name, '')


class Font:
    def __init__(self, pdf, d):
        m = re.search(rb'/BaseFont\s*/([^\s/<>\[\]]+)', d)
        self.name = m.group(1).decode('latin-1').split('+')[-1] if m else '?'
        self.chess = 'echec' in self.name.lower()
        self.two = b'/Type0' in d
        self.map, self.w, self.dw = {}, {}, 1000.0
        if self.two:
            desc = re.search(rb'/DescendantFonts\s*\[?\s*(\d+)\s+\d+\s+R', d)
            dd = pdf.head(int(desc.group(1))) if desc else b''
            if desc and dd.lstrip().startswith(b'['):          # array object holding the reference
                r = re.search(rb'(\d+)\s+\d+\s+R', dd)
                dd = pdf.head(int(r.group(1))) if r else b''
            m = re.search(rb'/DW\s+([\d.]+)', dd)
            self.dw = float(m.group(1)) if m else 1000.0
            wr = re.search(rb'/W\s*(\d+\s+\d+\s+R|\[)', dd)
            if wr:
                if wr.group(1) == b'[':
                    j, depth = wr.end(), 1
                    k = j
                    while depth and k < len(dd):
                        depth += {91: 1, 93: -1}.get(dd[k], 0)
                        k += 1
                    warr = dd[j:k - 1]
                else:
                    warr = pdf.objs.get(int(wr.group(1).split()[0]), b'').strip()[1:-1]
                toks = re.findall(rb'\[|\]|-?[\d.]+', warr)
                i = 0
                try:
                    while i < len(toks):
                        a = int(float(toks[i]))
                        if toks[i + 1] == b'[':
                            i += 2
                            c = a
                            while toks[i] != b']':
                                self.w[c] = float(toks[i])
                                c += 1
                                i += 1
                            i += 1
                        else:
                            for c in range(a, int(float(toks[i + 1])) + 1):
                                self.w[c] = float(toks[i + 2])
                            i += 3
                except (IndexError, ValueError):
                    pass
        else:
            fc = re.search(rb'/FirstChar\s+(\d+)', d)
            wa = re.search(rb'/Widths\s*(\[[^\]]*\]|\d+\s+\d+\s+R)', d)
            if fc and wa:
                arr = wa.group(1)
                if not arr.startswith(b'['):
                    arr = pdf.objs.get(int(arr.split()[0]), b'')
                for k, v in enumerate(re.findall(rb'-?[\d.]+', arr)):
                    self.w[int(fc.group(1)) + k] = float(v)
            self.dw = 500.0
            enc = pdf.sub(d, rb'Encoding') or (re.search(rb'/Encoding\s*/(\w+)', d) or [b'', b''])[0]
            codec = 'mac_roman' if b'MacRoman' in enc else 'cp1252'
            for c in range(256):
                self.map[c] = bytes([c]).decode(codec, 'replace')
        tu = pdf.ref(d, rb'ToUnicode')
        if tu:
            self.map.update(parse_cmap(pdf.stream(tu)))
        if not self.two:                  # glyph names beat the (sometimes wrong) ToUnicode maps of macOS
            diff = re.search(rb'/Differences\s*\[(.*?)\]', pdf.sub(d, rb'Encoding'), re.S)
            code = 0
            for t in re.findall(rb'\d+|/[^\s/\[\]]+', diff.group(1)) if diff else []:
                if t[:1] == b'/':
                    ch = glyph_char(t[1:].decode('latin-1'))
                    if ch:
                        self.map[code] = ch
                    code += 1
                else:
                    code = int(t)
        if self.chess:                   # symbol fonts map to the private use area: U+F0xx -> xx
            self.map = {k: ''.join(chr(ord(ch) - 0xF000) if 0xF000 <= ord(ch) < 0xF100 else ch for ch in v)
                        for k, v in self.map.items()}

    def codes(self, b):
        return [b[i] << 8 | b[i + 1] for i in range(0, len(b) - 1, 2)] if self.two else list(b)

    def char(self, c):
        ch = self.map.get(c)
        if not ch:
            ch = chr(c) if not self.two else '¿' if self.chess else ''
        if self.chess and ch.endswith(' ') and len(ch) > 1:      # 1Echecs ToUnicode pads some glyphs
            ch = ch.rstrip(' ')
        return ch


TOK = re.compile(rb'\s*(?:(%[^\r\n]*)|(\()|(<<|>>|\[|\]|\{|\})|(<[0-9A-Fa-f\s]*>)|(/[^\s/\[\]()<>{}%]*)|'
                 rb'([-+]?(?:\d+\.?\d*|\.\d+))|([A-Za-z\'"*][A-Za-z0-9*]*))')
ESC = {ord('n'): 10, ord('r'): 13, ord('t'): 9, ord('b'): 8, ord('f'): 12}


def lit_string(s, i):
    out, depth = bytearray(), 1
    while i < len(s):
        c = s[i]
        if c == 0x5c:
            i += 1
            c = s[i] if i < len(s) else 0
            if c in ESC:
                out.append(ESC[c])
            elif 0x30 <= c <= 0x37:
                j = i
                while j < i + 3 and j < len(s) and 0x30 <= s[j] <= 0x37:
                    j += 1
                out.append(int(s[i:j], 8) & 255)
                i = j
                continue
            elif c in (10, 13):
                pass
            else:
                out.append(c)
        elif c == 0x28:
            depth += 1
            out.append(c)
        elif c == 0x29:
            depth -= 1
            if depth == 0:
                return bytes(out), i + 1
            out.append(c)
        else:
            out.append(c)
        i += 1
    return bytes(out), i


def tokens(s):
    i, n = 0, len(s)
    while i < n:
        m = TOK.match(s, i)
        if not m:
            i += 1
            continue
        i = m.end()
        if m.group(1):
            continue
        if m.group(2):
            v, i = lit_string(s, i)
            yield 's', v
        elif m.group(3):
            yield 'd', m.group(3)
        elif m.group(4):
            h = re.sub(rb'\s', b'', m.group(4)[1:-1])
            yield 's', bytes.fromhex((h + b'0' * (len(h) % 2)).decode())
        elif m.group(5):
            yield 'n', m.group(5)[1:].decode('latin-1')
        elif m.group(6):
            yield 'f', float(m.group(6))
        elif m.group(7):
            if m.group(7) == b'BI':                       # skip inline images
                e = s.find(b'EI', i)
                i = e + 2 if e >= 0 else n
                continue
            yield 'o', m.group(7).decode('latin-1')


def mul(a, b):
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2],
            a[2] * b[1] + a[3] * b[3], a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


class Run:
    """One text-showing operation: position, size, font and its glyphs [(x, char, width)]."""
    __slots__ = ('x', 'y', 'x1', 'size', 'font', 'glyphs')

    def __init__(self, x, y, x1, size, font, glyphs):
        self.x, self.y, self.x1, self.size, self.font, self.glyphs = x, y, x1, size, font, glyphs

    @property
    def text(self):
        return ''.join(g[1] for g in self.glyphs)


def page_runs(pdf, pn):
    pd = pdf.head(pn)
    res, par = pdf.sub(pd, rb'Resources'), pdf.ref(pd, rb'Parent')
    while not res and par:
        res, par = pdf.sub(pdf.head(par), rb'Resources'), pdf.ref(pdf.head(par), rb'Parent')
    cont = re.search(rb'/Contents\s*(\[.*?\]|\d+\s+\d+\s+R)', pd, re.S)
    data = b''
    if cont:
        for n in re.findall(rb'(\d+)\s+\d+\s+R', cont.group(1)):
            body = pdf.head(int(n)).strip()
            if body.startswith(b'['):                     # indirect array of streams
                for k in re.findall(rb'(\d+)\s+\d+\s+R', body):
                    data += pdf.stream(int(k)) + b'\n'
            else:
                data += pdf.stream(int(n)) + b'\n'
    out = []
    interpret(pdf, data, res, [1, 0, 0, 1, 0, 0], out, 0)
    return out


def interpret(pdf, data, res, ctm0, out, depth):
    fonts, xobj, fcache = pdf.sub(res, rb'Font'), pdf.sub(res, rb'XObject'), {}
    ctm, stack, args = ctm0[:], [], []
    tm = tlm = [1, 0, 0, 1, 0, 0]
    font, size, lead, tc, tw, th = None, 1.0, 0.0, 0.0, 0.0, 1.0
    for kind, v in tokens(data):
        if kind != 'o':
            args.append((kind, v))
            continue
        op, a = v, [x[1] for x in args]
        nums = [x for x in a if isinstance(x, float)]
        if op == 'q':
            stack.append((ctm[:], font, size, tc, tw, th, lead))
        elif op == 'Q':
            if stack:
                ctm, font, size, tc, tw, th, lead = stack.pop()
        elif op == 'cm' and len(nums) >= 6:
            ctm = mul(nums[-6:], ctm)
        elif op == 'BT':
            tm = tlm = [1, 0, 0, 1, 0, 0]
        elif op == 'Tf' and len(a) >= 2 and isinstance(a[-2], str):
            fn = a[-2]
            if fn not in fcache:
                r = re.search(rb'/' + re.escape(fn.encode('latin-1')) + rb'\s+(\d+)\s+\d+\s+R', fonts)
                fcache[fn] = Font(pdf, pdf.head(int(r.group(1)))) if r else None
            font, size = fcache[fn], float(a[-1])
        elif op == 'TL' and nums:
            lead = nums[-1]
        elif op == 'Tc' and nums:
            tc = nums[-1]
        elif op == 'Tw' and nums:
            tw = nums[-1]
        elif op == 'Tz' and nums:
            th = nums[-1] / 100
        elif op in ('Td', 'TD') and len(nums) >= 2:
            if op == 'TD':
                lead = -nums[-1]
            tlm = mul([1, 0, 0, 1, nums[-2], nums[-1]], tlm)
            tm = tlm
        elif op == 'Tm' and len(nums) >= 6:
            tlm = tm = nums[-6:]
        elif op == 'T*':
            tlm = mul([1, 0, 0, 1, 0, -lead], tlm)
            tm = tlm
        elif op in ('Tj', 'TJ', "'", '"'):
            if op in ("'", '"'):
                if op == '"' and len(nums) >= 2:
                    tw, tc = nums[0], nums[1]
                tlm = mul([1, 0, 0, 1, 0, -lead], tlm)
                tm = tlm
            elems = [x for x in args if x[0] in 'sf'] if op == 'TJ' else [x for x in args if x[0] == 's'][-1:]
            if font:
                m0 = mul(tm, ctm)
                scale = (m0[0] ** 2 + m0[1] ** 2) ** .5
                glyphs, dx = [], 0.0
                for k, x in elems:
                    if k == 'f':
                        dx -= x / 1000 * size * th
                        continue
                    for c in font.codes(x):
                        w = font.w.get(c, font.dw) / 1000 * size
                        glyphs.append((m0[4] + dx * scale, font.char(c), w * scale))
                        dx += (w + tc + (tw if c == 32 and not font.two else 0)) * th
                tm = mul([1, 0, 0, 1, dx, 0], tm)
                if glyphs:
                    out.append(Run(m0[4], m0[5], m0[4] + dx * scale, size * (abs(m0[3]) or abs(m0[1])),
                                   font, glyphs))
        elif op == 'Do' and a and isinstance(a[-1], str) and depth < 6:
            r = re.search(rb'/' + re.escape(a[-1].encode('latin-1')) + rb'\s+(\d+)\s+\d+\s+R', xobj)
            if r:
                n = int(r.group(1))
                xd = pdf.head(n)
                if re.search(rb'/Subtype\s*/Form', xd):
                    mm = re.search(rb'/Matrix\s*\[([^\]]*)\]', xd)
                    mat = [float(x) for x in mm.group(1).split()] if mm else [1, 0, 0, 1, 0, 0]
                    interpret(pdf, pdf.stream(n), pdf.sub(xd, rb'Resources') or res, mul(mat, ctm), out, depth + 1)
        args = []


# ---------------------------------------------------------------- page layout: boards and text segments

# The 1Echecs diagram font: a board row is '/' + 8 squares + '/'; an empty light square is a gap (kerning),
# ':' an empty dark square.  A piece is one letter, lower case = White, upper case = Black (R D T F C P,
# the white Queen is the pair 'de'); on a dark square the letter is preceded by two zero-width glyphs that
# draw the hatching (01 King, 23 Queen, 45 Rook, 67 Bishop, 89 Knight, () Pawn), so only glyphs with a
# width count.  Any other visible glyph is a fairy piece (rotated / neutral / special symbol), kept as {glyph}.
PIECE = {'r': 'K', 'd': 'Q', 'de': 'Q', 't': 'R', 'f': 'B', 'c': 'S', 'p': 'P'}
MARKS = ('õù', '÷û')                                  # square markers drawn over a square


HATCH = {'r': '01', 'd': '23', 'de': '23', 't': '45', 'f': '67', 'c': '89', 'p': '()'}


def decode_square(cl, overlay=''):
    """visible glyphs (+ zero-width overlay) -> (colour, piece) | ('?', '{glyph}') | None; marker flag."""
    marked = any(m in overlay for m in MARKS)
    for m in MARKS:
        overlay = overlay.replace(m, '')
    cl = cl.replace(':', '').replace(' ', '')
    if not cl:
        return None, marked
    if (cl in ('de', 'd') or (len(cl) == 1 and cl in 'RDTFCPrtfcp')) and overlay in ('', HATCH[cl.lower()]):
        return ('w' if cl.islower() else 'b', PIECE[cl.lower()]), marked
    if overlay and (cl in ('de', 'd') or cl in 'RDTFCPrtfcp') and len(overlay) <= 2:
        cl = overlay + cl                              # an unusual overlay changes an orthodox piece
    return ('?', '{%s}' % cl), marked


class Board:
    def __init__(self, x, top, sz):
        self.x, self.top, self.sz = x, top, sz
        self.bottom = top - 9 * sz
        self.x1 = x + 8 * sz
        self.squares = {}          # (file 0-7, rank 1-8) -> visible glyphs
        self.overlay = {}          # (file 0-7, rank 1-8) -> zero-width glyphs drawn over the square
        self.runs = []


def find_boards(runs):
    boards = []
    for r in runs:
        if r.font.chess and re.fullmatch(r'!?-{8}!?', r.text.strip()):
            dash = [g for g in r.glyphs if g[1] == '-']
            boards.append(Board(dash[0][0], r.y, r.size))
            boards[-1].runs.append(r)
    for r in runs:
        if not r.font.chess:
            continue
        for b in boards:
            if abs(r.size - b.sz) > .6 or not (b.x - b.sz < r.x < b.x1 + .5 * b.sz):
                continue
            k = (b.top - r.y) / b.sz
            if abs(k - round(k)) > .3 or not 1 <= round(k) <= 9:
                continue
            b.runs.append(r)
            if round(k) == 9:
                continue
            rank = 9 - round(k)
            for gx, ch, w in r.glyphs:
                col = int((gx - b.x) / b.sz + .05)
                if ch in '/$_' or not 0 <= col < 8:
                    continue
                if w < .05 * b.sz:                     # zero-width overlay: hatching or a square marker
                    b.overlay[(col, rank)] = b.overlay.get((col, rank), '') + ch
                else:
                    b.squares[(col, rank)] = b.squares.get((col, rank), '') + ch
            break
    return boards


def position_of(items):
    """[(colour w/b/?, piece, square)] -> (english position, fen or None, white, black, unknown)"""
    order = 'KQRBSP'
    side = {'w': [], 'b': [], '?': []}
    fen_board = {}
    for colour, piece, sq in items:
        side[colour].append((piece, sq))
        if colour != '?':
            p = piece.replace('S', 'N')
            fen_board[('abcdefgh'.index(sq[0]), int(sq[1]))] = p if colour == 'w' else p.lower()

    def fmt(lst):
        return ' '.join(p + s for p, s in sorted(lst, key=lambda t: (order.index(t[0]) if t[0] in order else 9,
                                                                   t[1][0], t[1][1])))
    pos = fmt(side['w']) + ' + ' + fmt(side['b'])
    if side['?']:
        pos += ' + ' + fmt(side['?'])
    fen = None
    if not side['?'] and sorted(v for v in fen_board.values() if v in 'Kk') == ['K', 'k']:
        rows = []
        for rank in range(8, 0, -1):
            row, empty = '', 0
            for col in range(8):
                p = fen_board.get((col, rank))
                if p:
                    row += (str(empty) if empty else '') + p
                    empty = 0
                else:
                    empty += 1
            rows.append(row + (str(empty) if empty else ''))
        fen = '/'.join(rows)
    return pos, fen, len(side['w']), len(side['b']), len(side['?'])


def board_position(b):
    items, marks = [], []
    for (col, rank) in set(b.squares) | set(b.overlay):
        dec, marked = decode_square(b.squares.get((col, rank), ''), b.overlay.get((col, rank), ''))
        sq = 'abcdefgh'[col] + str(rank)
        if marked:
            marks.append(sq)
        if dec:
            items.append((dec[0], dec[1], sq))
    return position_of(items) + (sorted(marks),)


FIG = '\x01%s\x02'


def figurines(text):
    """Chess-font text outside a board: split into piece tokens."""
    out = []
    for m in re.finditer(r'de|[RDTFCPrdtfcp]|[^RDTFCPrdtfcp]+', text):
        t = m.group(0).strip()
        if t:
            out.append(FIG % t)
    return ''.join(out)


class Seg:
    __slots__ = ('x', 'y', 'x1', 'size', 'bold', 'italic', 'text', 'page', 'used')

    def __repr__(self):
        return 'Seg(%.0f,%.0f,%r)' % (self.x, self.y, self.text)


def segments(runs, pageno):
    runs = sorted(runs, key=lambda r: -r.y)
    lines = []
    for r in runs:
        tol = .3 * max(r.size, 8)
        for ln in lines[-4:]:
            if abs(ln[0] - r.y) <= tol or (r.font.chess and 0 < ln[0] - r.y <= tol + 1):
                ln[1].append(r)
                break
        else:
            lines.append([r.y, [r]])
    segs = []
    for y, rs in lines:
        rs.sort(key=lambda r: r.x)
        cur = []
        for r in rs:
            if cur and r.x - max(c.x1 for c in cur) > 9:
                segs.append(make_seg(cur, pageno))
                cur = []
            cur.append(r)
        if cur:
            segs.append(make_seg(cur, pageno))
    return [s for s in segs if s.text.strip()]


def make_seg(rs, pageno):
    s = Seg()
    txt = [r for r in rs if not r.font.chess] or rs
    s.x, s.x1, s.page, s.used = rs[0].x, max(r.x1 for r in rs), pageno, False
    s.y = max(r.y for r in txt)
    s.size = max(r.size for r in txt)
    n = sum(len(r.glyphs) for r in txt) or 1
    s.bold = sum(len(r.glyphs) for r in txt if 'bold' in r.font.name.lower()) / n > .5
    s.italic = sum(len(r.glyphs) for r in txt if re.search(r'ital|-it\b|oblique', r.font.name.lower())) / n > .5
    s.text = ''.join(figurines(r.text) if r.font.chess else r.text for r in rs)
    s.text = re.sub(r'[ \t\xa0]+', ' ', s.text.replace('­', ''))
    return s


# ---------------------------------------------------------------- problems out of a PDF

FR_FIG = {'r': 'R', 'd': 'D', 'de': 'D', 't': 'T', 'f': 'F', 'c': 'C', 'p': 'P'}


def render(text, twin=False):
    """Segment text -> French text; figurines become French piece letters (with the colour, w/b, in twins),
    fairy glyphs stay as {glyph}."""
    def fig(m):
        g = m.group(1)
        if g.lower() in FR_FIG and (g in FR_FIG or g.lower() != 'de'):
            letter = FR_FIG[g.lower()]
            if twin:
                return ('w' if g.islower() else 'b') + FR2EN[letter]
            return letter
        return '{%s}' % g
    return re.sub('\x01(.*?)\x02', fig, text)


FILE_ACC = re.compile(r'(?<![à-ÿÀ-ß])[éç](?=[1-8]|[x×]|[a-hçé][1-8])')


def english(s):
    """French solution notation -> English (K Q R B S), '#' for mate, 'x' for captures, é/ç files -> e/c."""
    s = s.replace('‡', '#').replace('…', '...').replace('×', 'x').replace('®', '->').replace('→', '->')
    for _ in range(2):                                  # twice: 'Téé6', 'çç5'
        s = FILE_ACC.sub(lambda m: {'é': 'e', 'ç': 'c'}[m.group(0)], s)
    s = re.sub(r'(?<![A-Za-z])([RDTFC])(?=[a-h]?[1-8]?x?[a-h][1-8])', lambda m: FR2EN[m.group(1)], s)
    s = re.sub(r'=([DTFC])(?![a-z])', lambda m: '=' + FR2EN[m.group(1)], s)
    return s


COUNT = re.compile(r'\((\d+\s*\+\s*\d+(?:\s*\+\s*\d+\s*n?)?)\)')
LABEL = r'(?:(?:Ann(?:exe)?|Exemple|Ex)\.?\s*[A-Z]?\s?\d{1,3}[a-z]?)'
NUMBERED = re.compile(r'^(\d{1,5}[a-zA-Z]?|' + LABEL + r'|[A-Z]{1,3}\s?-?\d{1,4}[a-z]?|[IVXL]{1,5}|'
                      r'[a-z]{1,4}\d{1,3})\s*[-–]\s+(\S.*)$')
AWARD = re.compile(r"\b(prix|mention|recommand|commend|special|spécial|lob|preis|place|hon\.?|ho\b|°|"
                   r"1er|1st|2nd|3rd|\dth|prize)", re.I)
SOURCE = re.compile(r'ph[ée]nix|\b(19|20)\d\d\b|tourn|concours|memorial|mémorial|jt\b|tt\b|\bty\b|problem|'
                    r'magazine|revue|diagrammes|feenschach|mat plus|springaren|probleemblad|die schwalbe|'
                    r'variantim|strateg|wccc|wcct|olympi|jubil|section|version', re.I)
SIMPLE_TWIN = re.compile(r'[a-z]\) (=[a-z]\)|[-+]?[wb]?[KQRBSP][a-h][1-8]( ?(->|-|→) ?[a-h][1-8])?[ ,]*|'
                         r'[wb]?[KQRBSP][a-h][1-8] ?(<->|<>|↔) ?[wb]?[KQRBSP]?[a-h][1-8][ ,]*|'
                         r'(#|h#|s#|r#)\d+(,\d+)?[ ,]*|[a-h][1-8] ?(->|-|→) ?[a-h][1-8][ ,]*)+$')


def clean(t):
    return re.sub(r'\s+', ' ', t).strip()


def parse_header(lines, rec):
    authors, rest = [], []
    for i, ln in enumerate(lines):
        t = clean(render(ln.text))
        m = NUMBERED.match(t)
        if i == 0 and m:
            rec['number'] = m.group(1)
            authors.append(m.group(2))
        elif i == 0 and re.fullmatch(r'(n°\s*)?\d{1,5}[a-z]?|[A-Z]{1,3}-?\d{1,4}|' + LABEL, t):
            rec['number'] = t.replace('n°', '').strip()
        elif t.startswith('&') and rest:
            rest[-1] = (rest[-1][0] + ' ' + t, rest[-1][1])
        elif t.startswith('&') and (authors or i == 0):
            authors.append(t[1:].strip())
        elif not authors and not rest and ln.bold:
            authors.append(t)
        elif authors and ln.bold and not AWARD.search(t) and not SOURCE.search(t) and not rest:
            authors.append(t)                       # joint author on its own bold line
        else:
            rest.append((t, ln))
    if authors:
        rec['author'] = ' & '.join(re.sub(r'\s*[&,]\s*$', '', a) for a in authors)
    src, award, other = [], [], []
    for t, ln in rest:
        if AWARD.search(t) and len(t) < 60 and not re.search(r'd[ée]di|m[ée]moire|hommage', t, re.I):
            award.append(t)
        elif SOURCE.search(t) and not ln.italic and not re.search(r"d[ée]di|m[ée]moire|hommage|d'apr[èe]s|to ",
                                                                  t, re.I):
            src.append(t)
        else:
            other.append(t)
    if not authors and src == [] and other and not rec.get('number'):
        rec['author'] = other.pop(0)
    if src:
        rec['source'] = ', '.join(src)
    if award:
        rec['award'] = ', '.join(award)
    if other:
        rec['dedication'] = ' '.join(other)


def parse_stip(text, rec):
    t = clean(render(text))
    m = COUNT.search(t)
    if not m:
        return False
    rec['count'] = re.sub(r'\s', '', m.group(1))
    stip, tail = t[:m.start()].strip(), t[m.end():].strip()
    mm = re.search(r'\s(\d+\.\d+\.[\d.…]*|\d+ solutions?|\d+\s*sol\.)$', stip)
    if mm:
        rec['play'] = mm.group(1)
        stip = stip[:mm.start()].strip()
    mm = re.fullmatch(r'(.*?\d)(\*?v*\*?)', stip)
    if mm and mm.group(2):
        stip, rec['marks'] = mm.group(1), mm.group(2)
    rec['stip'] = stip.replace('‡', '#') or None
    if re.match(r'C[+-]', tail):
        rec['tested'] = tail[:2]
        tail = tail[2:].strip()
    return tail


def board_problems(boards, segs, pageinfo):
    """Attach the text around every board: header lines above it, stipulation line and twins/conditions below."""
    out = []
    for b in boards:
        rng = [s for s in segs if b.x - 18 <= s.x <= b.x1 + 6 and not s.used and s.y > 45]
        above = sorted((s for s in rng if s.y > b.top - 2), key=lambda s: s.y)
        head, prev = [], b.top
        for s in above:
            if s.y - prev > 22 or s.size >= 15 or len(head) >= 7 or COUNT.search(s.text):
                break
            if s.x1 > b.x1 + 60 and s.x < b.x + 20 and len(clean(s.text)) > 60:
                break                                  # a paragraph of running text
            head.append(s)
            prev = s.y
        head.reverse()
        below = sorted((s for s in rng if s.y <= b.bottom + 6), key=lambda s: -s.y)
        stipsegs = [s for s in below if s.y >= b.bottom - 9]
        rec = {}
        pos, fen, w, bl, fa, marks = board_position(b)
        rec['position'], rec['fen'] = pos, fen
        tail = False
        if stipsegs:
            y0 = stipsegs[0].y
            first = [s for s in stipsegs if abs(s.y - y0) < 3]
            tail = parse_stip(' '.join(s.text for s in first), rec)
            if tail is not False:
                for s in first:
                    s.used = True
        if tail is False:
            first = []
        extra = [tail] if tail else []
        prev = first[0].y if first else b.bottom
        for s in below:
            if s in first:
                continue
            if prev - s.y > 18 or (s.bold and NUMBERED.match(clean(s.text))) or s.size >= 15 or \
                    (s.x1 > b.x1 + 40 and len(clean(s.text)) > 45) or COUNT.search(s.text):
                break
            extra.append(s)
            prev = s.y
        if not head and not first:
            continue                                   # a board without any text: not a problem diagram
        for s in head:
            s.used = True
        parse_header(head, rec)
        twins, conds = [], []
        for e in extra:
            if isinstance(e, str):
                conds.append(e)
                continue
            e.used = True
            t = clean(render(e.text, twin=bool(re.match(r'[a-z]\)', clean(e.text)))))
            if re.match(r'[a-z]\)', t):
                twins.append(english(t))
            elif t:
                conds.append(t)
        if twins:
            rec['twins'] = twins
        if conds:
            rec['conditions'] = conds
        if marks:
            rec['marked_squares'] = marks
        rec['pieces'] = '%d+%d' % (w, bl) + ('+%d?' % fa if fa else '')
        rec['_page'] = pageinfo
        out.append(rec)
    return out


SOL_HEAD = re.compile(r'^(\d{3,5}[a-z]?)\s*[-–]?\s+([A-ZÀ-Ý]\S*\.?\s.*)$')


def solution_blocks(segs_by_page):
    """Numbered solution paragraphs ('10177 - Abdelaziz Onkoud' then the moves and the comment)."""
    sols, cur = {}, None
    for pageno, segs in segs_by_page:
        free = [s for s in segs if not s.used and 45 < s.y]
        mid = 297
        free.sort(key=lambda s: (0 if s.x < mid - 25 else 1, -s.y, s.x))
        for s in free:
            t = clean(render(s.text))
            m = SOL_HEAD.match(t)
            if s.size >= 15:
                cur = None
                continue
            if m and s.bold:
                cur = sols.setdefault(m.group(1), {'author': m.group(2), 'lines': [], 'page': pageno})
                if cur['lines']:                        # the number appears twice: keep the first block
                    cur = None
                continue
            if cur is not None:
                if not cur['lines'] and t.startswith('&'):
                    cur['author'] += ' ' + t              # joint author on the next line
                elif not re.fullmatch(r'(i?[èe]me|[èe]re|er|nde?|e)', t):   # stray superscripts
                    cur['lines'].append(t)
    return sols


def join_lines(lines):
    out = ''
    for ln in lines:
        if out.endswith('-') and not out.endswith(' -') and re.match(r'[a-zà-ÿ]', ln) and \
                not re.search(r'[a-h][1-8]-$', out):
            out = out[:-1] + ln
        else:
            out += ('\n' if out else '') + ln
    return out


def pdf_problems(path, url):
    try:
        pdf = PDF(open(path, 'rb').read())
    except Exception as e:
        print('unreadable', path, e, file=sys.stderr)
        return [], {}
    recs, segs_by_page, issue = [], [], None
    for i, pn in enumerate(pdf.pages()):
        try:
            runs = page_runs(pdf, pn)
        except Exception as e:
            print('page failed', path, i + 1, e, file=sys.stderr)
            continue
        boards = find_boards(runs)
        used = {id(r) for b in boards for r in b.runs}
        segs = segments([r for r in runs if id(r) not in used], i + 1)
        for s in segs:
            m = re.search(r'Ph[ée]nix\s+(\d{1,3}(?:-\d{1,3})?)\s*[-–]\s*([A-Za-zéûÉÛ-]+(?:\s*[-–]\s*[A-Za-zéûÉÛ]+)?\s+\d{4})',
                          s.text)
            if m and s.y < 60 and not issue:
                issue = 'Phénix %s (%s)' % (m.group(1), m.group(2))
        recs += board_problems(boards, segs, i + 1)
        segs_by_page.append((i + 1, segs))
    sols = solution_blocks(segs_by_page)
    for r in recs:
        r['page'] = '%s#page=%d' % (url, r.pop('_page'))
        if r.get('number') and issue and 'source' not in r and re.fullmatch(r'\d+', r['number']):
            r['source'] = issue
    return recs, {k: dict(v, page='%s#page=%d' % (url, v['page'])) for k, v in sols.items() if v['lines']}


# ---------------------------------------------------------------- HTML award pages

IMG = '\x03IMG %s\x03'


def page_lines(page):
    m = re.search(r'InstanceBeginEditable name="EditRegion1"\s*-->(.*?)(<!--\s*InstanceEndEditable|$)', page, re.S)
    t = m.group(1) if m else page
    t = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', t, flags=re.S | re.I)
    t = re.sub(r'<img\b[^>]*?src\s*=\s*["\']([^"\']+)["\'][^>]*>',
               lambda mm: '\x00' + IMG % mm.group(1) + '\x00' if DIAGRAM.search(mm.group(1)) else '', t,
               flags=re.S | re.I)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'<br\s*/?>|<p\b[^>]*>|</p>|</div>|<div\b[^>]*>|</td>|</tr>|</h\d>|<h\d[^>]*>|<li\b[^>]*>|<hr[^>]*>',
               '\x00', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', '', t))
    lines = [re.sub(r'[ \t\r\xa0]+', ' ', ln).strip() for ln in t.split('\x00')]
    return [ln for ln in lines if ln]


NAME_CAPS = re.compile(r"\b[A-ZÀ-ÝŠŽČĆ][A-ZÀ-ÝŠŽČĆ'\-]{2,}\b")
MOVE_LINE = re.compile(r'^([a-z]\)\s*)?(\d+\s*(\.|…)|\d+\.\.\.|\.\.\.|…)')
AWARD_INTRO = re.compile(r"^(.{0,45}?(?:prix|mention|recommand|commend|spécial|special|lob|ho\b)[^:]{0,40}?)\s*:\s*(.+)$",
                         re.I)
SEPARATOR = re.compile(r'^[-_=*]{5,}$')
PLAY_DESC = re.compile(r'^\(.*(coups?|solutions?|moves?|sol\.).*\)$', re.I)


def html_problems(page, url, rel, mirror, classify):
    lines = page_lines(page)
    title = re.search(r'<title>(.*?)</title>', page, re.S | re.I)
    imgs = [i for i, ln in enumerate(lines) if ln.startswith('\x03IMG')]
    out = []
    # the header of each diagram: the few short lines just before the picture, from the author line on
    heads = []
    for i in imgs:
        j, cand = i - 1, []
        while j >= 0 and len(cand) < 5 and not lines[j].startswith('\x03') and not SEPARATOR.match(lines[j]) \
                and len(lines[j]) <= 90:
            cand.insert(0, j)
            j -= 1
        start = i
        for k in cand:                          # the author line: surname(s) in capitals
            t = lines[k]
            if NAME_CAPS.search(t) and not AWARD.search(t) and not re.match(r'\d+\.\s|th[èe]me|section', t, re.I):
                start = k
                break
        heads.append(start)
    context = []
    for n, i in enumerate(imgs):
        # tourney context: the page heading and the latest section title before the header
        ctx = [ln for ln in lines[(imgs[n - 1] + 1 if n else 0):heads[n]]
               if re.match(r'(\d+\.\s*)?section|\d+\.\s+\S', ln, re.I) and len(ln) < 80]
        end = heads[n + 1] if n + 1 < len(imgs) else len(lines)
        rec = {}
        src = lines[i][5:-1]
        img_url = urllib.parse.urljoin(url, src)
        path = local_path(mirror, img_url)
        pos = None
        if os.path.exists(path):
            try:
                pos = classify(path)
            except Exception as e:
                print('image failed', path, e, file=sys.stderr)
        if pos:
            rec['position'], rec['fen'] = pos[0], pos[1]
            rec['pieces'] = pos[2]
        else:
            rec['position'], rec['fen'] = None, None
        body = lines[i + 1:end]
        k, stipdone = 0, False
        while k < len(body):
            t = body[k]
            m = re.fullmatch(r'\((\d+\s*\+\s*\d+(?:\s*\+\s*\d+\s*n?)?)\)\s*(C[+-])?', t)
            if m and 'count' not in rec:
                rec['count'] = re.sub(r'\s', '', m.group(1))
                if m.group(2):
                    rec['tested'] = m.group(2)
            elif re.fullmatch(r'C[+-]', t):
                rec['tested'] = t
            elif 'count' in rec and not stipdone and len(t) < 50 and not AWARD_INTRO.match(t):
                mm = re.search(r'\s(\d+\.\d+\.[\d.…]*|\d+ solutions?)$', t)
                if mm:
                    rec['play'] = mm.group(1)
                    t = t[:mm.start()]
                mm = re.fullmatch(r'(.*?\d)(\*?v*\*?)', t.strip())
                if mm and mm.group(2):
                    t, rec['marks'] = mm.group(1), mm.group(2)
                rec['stip'] = english(t.strip()).replace('‡', '#')
                stipdone = True
            elif stipdone and PLAY_DESC.match(t):
                pass
            elif stipdone and (AWARD_INTRO.match(t) or len(t) > 90 or MOVE_LINE.match(t)):
                break
            elif stipdone:
                if re.match(r'[a-z]\)\s', t):
                    rec.setdefault('twins', []).append(english(t))
                else:
                    rec.setdefault('conditions', []).append(t)
            elif 'count' not in rec and k > 3:
                break
            k += 1
        rest = body[k:]
        intro = None
        if rest and AWARD_INTRO.match(rest[0]):
            intro = AWARD_INTRO.match(rest[0])
            rest = rest[1:]
        comment, sol = [], []
        for t in rest:
            if SEPARATOR.match(t) or (sol and AWARD_INTRO.match(t) and re.search(r'\(.*\d.*\)\s*$', t)) or \
                    re.match(r'(\d+\.\s*)?section\b', t, re.I):
                break
            if not sol and not MOVE_LINE.match(t):
                comment.append(t)
            else:
                sol.append(t)
        hl = lines[heads[n]:i]
        authors, src_l, award_l, other = [], [], [], []
        for t in hl:
            if AWARD.search(t) and len(t) < 60:
                award_l.append(t)
            elif SOURCE.search(t) and not NAME_CAPS.search(t.replace('PHÉNIX', '').replace('PHENIX', '')):
                src_l.append(t)
            elif not authors or t.startswith('&'):
                authors.append(t.lstrip('& '))
            else:
                other.append(t)
        if authors:
            rec['author'] = ' & '.join(authors)
        if intro:
            full = re.sub(r'\s*\(([^()]*(\([^()]*\))?[^()]*)\)\s*$', '', intro.group(2)).strip()
            if full and NAME_CAPS.search(full):
                rec['author'] = full
            m = re.search(r'\(([^()]*\d[^()]*)\)\s*$', intro.group(2))
            if m:
                src_l = [m.group(1)]
            if not award_l:
                award_l = [intro.group(1)]
        if src_l:
            rec['source'] = ', '.join(src_l)
        if award_l:
            rec['award'] = ', '.join(award_l)
        if other:
            rec['dedication'] = ' '.join(other)
        heading = [lines[0]] if lines and not lines[0].startswith('\x03') and heads[0] > 0 else []
        tourney = ' - '.join(dict.fromkeys(heading + ctx[-1:]))
        if tourney:
            rec['tourney'] = tourney
        if sol:
            rec['solution_fr'] = '\n'.join(sol)
            rec['solution'] = english(rec['solution_fr'])
        if comment:
            rec['comment'] = '\n'.join(comment)
        rec['page'] = url
        rec['image'] = img_url
        out.append(rec)
    return out


# ---------------------------------------------------------------- diagram pictures (award pages)
# The HTML award pages show the diagrams only as pictures, all drawn with the same diagram font.  A small
# baseline-JPEG / PNG / GIF decoder (luminance only) turns them into grey pixels; the board frame is located,
# every square is shrunk to a 12x12 patch and compared with reference patches of the 26 orthodox square
# kinds (6 pieces x 2 colours x 2 square colours + 2 empty squares).  A square too far from every reference
# is reported as an unknown (fairy) piece.

ZIGZAG = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7,
          14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39,
          46, 53, 60, 61, 54, 47, 55, 62, 63]
_COS = [[(0.5 ** .5 if u == 0 else 1.0) * math.cos((2 * x + 1) * u * math.pi / 16) / 2
         for u in range(8)] for x in range(8)]


def _idct(blk):
    """8x8 inverse DCT (coefficients in natural order) -> 64 samples, level-shifted."""
    nz = [(i, v) for i, v in enumerate(blk) if v]
    if len(nz) == 1 and nz[0][0] == 0:
        return [min(255, max(0, round(nz[0][1] / 8 + 128)))] * 64
    tmp = [0.0] * 64
    rows = {}
    for i, v in nz:
        rows.setdefault(i >> 3, []).append((i & 7, v))
    for v_, lst in rows.items():                       # rows: horizontal frequencies u -> x
        for x in range(8):
            c = _COS[x]
            tmp[v_ * 8 + x] = sum(c[u] * val for u, val in lst)
    out = [0] * 64
    for x in range(8):
        col = [(v_, tmp[v_ * 8 + x]) for v_ in rows]
        for y in range(8):
            c = _COS[y]
            out[y * 8 + x] = min(255, max(0, round(sum(c[v_] * val for v_, val in col) + 128)))
    return out


def decode_jpeg(data):
    """Baseline (sequential Huffman) JPEG -> (width, height, grey rows) using the first component only."""
    qt, ht, comps, i, restart = {}, {}, [], 2, 0
    width = height = None
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            i += 1 if marker == 0xFF else 2
            continue
        ln = data[i + 2] << 8 | data[i + 3]
        seg = data[i + 4:i + 2 + ln]
        if marker == 0xDB:
            j = 0
            while j < len(seg):
                pq, tq = seg[j] >> 4, seg[j] & 15
                if pq:
                    vals = [seg[j + 1 + 2 * k] << 8 | seg[j + 2 + 2 * k] for k in range(64)]
                    j += 129
                else:
                    vals = list(seg[j + 1:j + 65])
                    j += 65
                q = [0] * 64
                for k in range(64):
                    q[ZIGZAG[k]] = vals[k]
                qt[tq] = q
        elif marker in (0xC0, 0xC1):
            height, width = seg[1] << 8 | seg[2], seg[3] << 8 | seg[4]
            for k in range(seg[5]):
                cid, hv, tq = seg[6 + 3 * k], seg[7 + 3 * k], seg[8 + 3 * k]
                comps.append({'id': cid, 'h': hv >> 4, 'v': hv & 15, 'tq': tq})
        elif marker in (0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            raise ValueError('unsupported JPEG (progressive/lossless/arithmetic)')
        elif marker == 0xC4:
            j = 0
            while j < len(seg):
                tc, th = seg[j] >> 4, seg[j] & 15
                counts = seg[j + 1:j + 17]
                syms = seg[j + 17:j + 17 + sum(counts)]
                code, k, table = 0, 0, {}
                for length in range(1, 17):
                    for _ in range(counts[length - 1]):
                        table[(length, code)] = syms[k]
                        code += 1
                        k += 1
                    code <<= 1
                ht[(tc, th)] = table
                j += 17 + sum(counts)
        elif marker == 0xDD:
            restart = seg[0] << 8 | seg[1]
        elif marker == 0xDA:
            ns = seg[0]
            scomp = []
            for k in range(ns):
                cid, t = seg[1 + 2 * k], seg[2 + 2 * k]
                c = next(c for c in comps if c['id'] == cid)
                scomp.append((c, t >> 4, t & 15))
            return _scan(data, i + 2 + ln, width, height, comps, scomp, qt, ht, restart)
        i += 2 + ln
    raise ValueError('no scan')


def _scan(data, pos, width, height, comps, scomp, qt, ht, restart):
    # entropy-coded segment -> one big bit string (FF00 unstuffed, RST markers noted as resync points)
    chunks, segs, j, start = [], [], pos, pos
    while j < len(data) - 1:
        if data[j] == 0xFF:
            nxt = data[j + 1]
            if nxt == 0:
                j += 2
                continue
            if 0xD0 <= nxt <= 0xD7:
                segs.append(data[start:j].replace(b'\xff\x00', b'\xff'))
                j += 2
                start = j
                continue
            break
        j += 1
    segs.append(data[start:j].replace(b'\xff\x00', b'\xff'))
    hmax, vmax = max(c['h'] for c in comps), max(c['v'] for c in comps)
    mcux, mcuy = (width + 8 * hmax - 1) // (8 * hmax), (height + 8 * vmax - 1) // (8 * vmax)
    y0 = comps[0]
    yw, yh = mcux * y0['h'] * 8, mcuy * y0['v'] * 8
    img = [bytearray(yw) for _ in range(yh)]
    tables = {}
    for c, td, ta in scomp:
        tables[c['id']] = (_lookup(ht[(0, td)]), _lookup(ht[(1, ta)]))
    seg_i, bits, bp = 0, None, 0

    def load(k):
        return ''.join(format(b, '08b') for b in segs[k]) if k < len(segs) else ''
    bits = load(0)
    pred = {c['id']: 0 for c, _, _ in scomp}
    total = mcux * mcuy
    for m in range(total):
        if restart and m and m % restart == 0:
            seg_i += 1
            bits, bp = load(seg_i), 0
            pred = {k: 0 for k in pred}
        mx, my = m % mcux, m // mcux
        for c, _, _ in scomp:
            dct, act = tables[c['id']]
            q = qt[c['tq']]
            for by in range(c['v']):
                for bx in range(c['h']):
                    s, bp = _huff(bits, bp, dct)
                    diff = 0
                    if s:
                        v = int(bits[bp:bp + s], 2)
                        bp += s
                        diff = v if v >= 1 << (s - 1) else v - (1 << s) + 1
                    pred[c['id']] += diff
                    blk = [0] * 64
                    blk[0] = pred[c['id']] * q[0]
                    k = 1
                    while k < 64:
                        rs, bp = _huff(bits, bp, act)
                        r, s = rs >> 4, rs & 15
                        if s == 0:
                            if r == 15:
                                k += 16
                                continue
                            break
                        k += r
                        v = int(bits[bp:bp + s], 2)
                        bp += s
                        if k < 64:
                            zz = ZIGZAG[k]
                            blk[zz] = (v if v >= 1 << (s - 1) else v - (1 << s) + 1) * q[zz]
                        k += 1
                    if c is y0:
                        px = _idct(blk)
                        ox, oy = (mx * c['h'] + bx) * 8, (my * c['v'] + by) * 8
                        for yy in range(8):
                            img[oy + yy][ox:ox + 8] = bytes(px[yy * 8:yy * 8 + 8])
    sx, sy = y0['h'] / hmax, y0['v'] / vmax        # luminance may be subsampled too (rare)
    if sx != 1 or sy != 1:
        img = [bytearray(img[int(y * sy)][int(x * sx)] for x in range(width)) for y in range(height)]
    return width, height, [bytes(r[:width]) for r in img[:height]]


def _lookup(table):
    return {(ln, code): sym for (ln, code), sym in table.items()}, max(ln for ln, _ in table)


def _huff(bits, bp, tab):
    table, maxlen = tab
    code = 0
    for ln in range(1, maxlen + 1):
        if bp >= len(bits):
            return 0, bp
        code = code << 1 | (bits[bp] == '1')
        bp += 1
        s = table.get((ln, code))
        if s is not None:
            return s, bp
    raise ValueError('bad huffman code')


def decode_png(data):
    import struct
    pos, idat, w = 8, b'', None
    plte = None
    while pos < len(data):
        ln, typ = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, depth, ctype, _, _, inter = struct.unpack('>IIBBBBB', body)
        elif typ == b'PLTE':
            plte = body
        elif typ == b'IDAT':
            idat += body
        pos += 12 + ln
    if inter:
        raise ValueError('interlaced PNG')
    chans = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    bpp = max(1, chans * depth // 8)
    stride = (w * chans * depth + 7) // 8
    raw = zlib.decompress(idat)
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        prev = line
    out = []
    for line in rows:
        if depth < 8:
            vals = [(line[i // (8 // depth)] >> (8 - depth - (i % (8 // depth)) * depth)) & ((1 << depth) - 1)
                    for i in range(w)]
        elif depth == 16:
            vals = [line[i * 2] for i in range(w * chans)]
        else:
            vals = list(line)
        if ctype == 3:
            g = bytes((plte[3 * v] * 299 + plte[3 * v + 1] * 587 + plte[3 * v + 2] * 114) // 1000 for v in vals)
        elif ctype == 0:
            g = bytes(v * 255 // ((1 << depth) - 1) for v in vals) if depth < 8 else bytes(vals)
        elif ctype == 4:
            g = bytes(vals[0::2])
        else:
            g = bytes((vals[i] * 299 + vals[i + 1] * 587 + vals[i + 2] * 114) // 1000 for i in range(0, len(vals), chans))
        out.append(g)
    return w, h, out


def decode_gif(data):
    w, h = data[6] | data[7] << 8, data[8] | data[9] << 8
    flags, pos = data[10], 13
    gct = None
    if flags & 0x80:
        n = 3 << ((flags & 7) + 1)
        gct = data[pos:pos + n]
        pos += n
    while data[pos] != 0x2C:
        if data[pos] == 0x21:
            pos += 2
            while data[pos]:
                pos += data[pos] + 1
            pos += 1
        else:
            raise ValueError('bad gif')
    iw, ih = data[pos + 5] | data[pos + 6] << 8, data[pos + 7] | data[pos + 8] << 8
    lflags = data[pos + 9]
    pos += 10
    pal = gct
    if lflags & 0x80:
        n = 3 << ((lflags & 7) + 1)
        pal = data[pos:pos + n]
        pos += n
    minsize = data[pos]
    pos += 1
    buf = bytearray()
    while data[pos]:
        buf += data[pos + 1:pos + 1 + data[pos]]
        pos += data[pos] + 1
    clear, end = 1 << minsize, (1 << minsize) + 1
    size, dic, out, prev, bitpos, val = minsize + 1, None, bytearray(), None, 0, int.from_bytes(buf, 'little')
    dic = [bytes([i]) for i in range(clear)] + [b'', b'']
    while bitpos + size <= len(buf) * 8:
        code = (val >> bitpos) & ((1 << size) - 1)
        bitpos += size
        if code == clear:
            size, dic, prev = minsize + 1, [bytes([i]) for i in range(clear)] + [b'', b''], None
            continue
        if code == end:
            break
        if code < len(dic):
            entry = dic[code]
            if prev is not None:
                dic.append(prev + entry[:1])
        elif prev is not None:
            entry = prev + prev[:1]
            dic.append(entry)
        else:
            break
        out += entry
        prev = entry
        if len(dic) == 1 << size and size < 12:
            size += 1
    grey = bytes((pal[3 * v] * 299 + pal[3 * v + 1] * 587 + pal[3 * v + 2] * 114) // 1000 for v in out)
    if lflags & 0x40:                                  # interlaced
        order = list(range(0, ih, 8)) + list(range(4, ih, 8)) + list(range(2, ih, 4)) + list(range(1, ih, 2))
        rows = [None] * ih
        for k, y in enumerate(order):
            rows[y] = grey[k * iw:(k + 1) * iw]
    else:
        rows = [grey[k * iw:(k + 1) * iw] for k in range(ih)]
    return iw, ih, [r if r and len(r) == iw else bytes(iw) for r in rows]


def decode_image(path):
    data = open(path, 'rb').read()
    if data[:2] == b'\xff\xd8':
        return decode_jpeg(data)
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return decode_png(data)
    if data[:4] == b'GIF8':
        return decode_gif(data)
    raise ValueError('unknown image format')


GRID = 12


def board_frame(w, h, rows):
    """Inner box of the board: between the first and the last dark frame line in both directions."""
    def lines(profile, n):
        dark = [i for i, v in enumerate(profile) if v < 90]
        if not dark:
            return 0, n - 1
        first = [dark[0]]
        for d in dark[1:]:
            if d == first[-1] + 1:
                first.append(d)
            else:
                break
        last = [dark[-1]]
        for d in reversed(dark[:-1]):
            if d == last[-1] - 1:
                last.append(d)
            else:
                break
        return first[-1] + 1, min(last) - 1
    y_lo, y_hi = int(h * .3), int(h * .7)
    x_lo, x_hi = int(w * .3), int(w * .7)
    colp = [sum(rows[y][x] for y in range(y_lo, y_hi)) / (y_hi - y_lo) for x in range(w)]
    rowp = [sum(rows[y][x_lo:x_hi]) / (x_hi - x_lo) for y in range(h)]
    # frame lines run across the whole picture; restrict to the lines near the picture edges
    x0, x1 = lines(colp, w)
    y0, y1 = lines(rowp, h)
    return x0, y0, x1, y1


def square_patches(path):
    w, h, rows = decode_image(path)
    x0, y0, x1, y1 = board_frame(w, h, rows)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    if bw < 80 or bh < 80 or abs(bw - bh) > bw * .06:
        raise ValueError('no board frame found (%dx%d)' % (bw, bh))
    sx, sy = bw / 8, bh / 8
    patches = {}
    for rank in range(8):
        for f in range(8):
            px, py = x0 + f * sx, y0 + rank * sy
            cell = []
            for gy in range(GRID):
                ya, yb = int(py + gy * sy / GRID), int(py + (gy + 1) * sy / GRID)
                for gx in range(GRID):
                    xa, xb = int(px + gx * sx / GRID), int(px + (gx + 1) * sx / GRID)
                    tot = n = 0
                    for yy in range(ya, max(yb, ya + 1)):
                        r = rows[yy]
                        for xx in range(xa, max(xb, xa + 1)):
                            v = r[xx]
                            tot += 1.0 if v < 60 else (170 - v) / 110 if v < 170 else 0.0
                            n += 1
                    cell.append(tot / n)
            patches[(f, 8 - rank)] = cell
    return patches


def patch_code(cell):
    return ''.join(str(min(9, int(v * 10))) for v in cell)


def code_patch(code):
    return [(int(c) + .5) / 10 for c in code]


def classify_patch(cell, refs, limit=.085):
    ink = sum(cell) / len(cell)
    if ink < .02:
        return None, 0.0
    best, bd = None, 9.0
    for label, ref in refs:
        d = sum(abs(a - b) for a, b in zip(cell, ref)) / len(cell)
        if d < bd:
            best, bd = label, d
    return (best if bd <= limit else '?'), bd


# Reference patches (12x12 ink levels 0-9, row by row) of the award-page diagram font; upper case = White.
REFS = {
    'K': ['000000000000000005610000000005610000003505513500021041041030030003500030030003500030003015620310000620015000000555555000000533334000000000000000'],
    'Q': ['000000000000000002300000002323504300011713506030033543543340005613044330003200001500003013320500000620015000000555555000000533334000000000000000'],
    'R': ['000000000000003324324500003042042500001755556200000533334000000500003000000500003000000500003000001666666100003000000500007666666630000000000000'],
    'B': ['000000000000000002300000000003500000000031050000000315613000000505613000000030011000000056670000000043341000005553255510033333333340000000000000'],
    'S': ['000000000000000101000000000545320000000511013000002330001300003000100120011001500030032123300030013513000030000011000030000043333350000000000000'],
    'P': ['000000000000000002300000000003120000000003500000000054361000000003310000000030030000000030030000000012120000000051051000000633335000000000000000'],
    'k': ['000000000000000005610000000005610000003505713500026666856640039994579960038996599950004866667510000899998000000755556000000589995000000000000000'],
    'q': ['000000000000000003500000002924608300011716906030055586956380008699997830006999999900004986679600000879987000000955558000000589995000000000000000'],
    'r': ['000000000000004626626600006979979900001555555200000566665000000599996000000599996000000599996000001533334100003999999500008666666830000000000000'],
    'b': ['000000000000000003500000000005800000000059980000000394385000000594386000000089991000000043350000000059971000005558955510047665566670000000000000'],
    's': ['000000000000000101000000000568520000000799953000002869997300007999899520019999999730057894999930014516999960000019999960000069999970000000000000'],
    'p': ['000000000000000003500000000008920000000005700000000069981000000007910000000059980000000069990000000018930000000059961000000899998000000000000000'],
}


# ---------------------------------------------------------------- parse

NOTE = ('Problems extracted from the site of the French problem magazine Phenix (phenix-echecs.fr): the '
        'downloadable PDFs (originals "inedits" with their solutions, a few complete issues, thematic tourney '
        'awards and announcements), whose diagrams are set in the 1Echecs chess font and so read as text, and the '
        'HTML award pages ("jugements"), whose diagrams are pictures read by template matching. Positions, '
        'stipulations, twins and solutions are converted to English notation (K Q R B S P, e/c files for the '
        'French e-acute/c-cedilla); solution_fr keeps the original. Fairy pieces the reader cannot name are '
        'written {glyph} (the 1Echecs glyph) or {?} (unknown picture) in a third, colourless group of the '
        'position, and such positions have no FEN.')

CONTEXT = [('errata', 'errata: corrected version'), ('demolition', 'demolition contest (published to be cooked)'),
           ('concours_solutions', 'solving contest'), ('annonce_', 'tourney announcement (example)'),
           ('messigny', 'Messigny meeting')]


def classify_image(path):
    refs = [(lab, code_patch(c)) for lab, codes in REFS.items() for c in codes]
    items = []
    for (f, r), cell in square_patches(path).items():
        lab, _ = classify_patch(cell, refs)
        if lab is None:
            continue
        sq = 'abcdefgh'[f] + str(r)
        items.append(('?', '{?}', sq) if lab == '?' else ('w' if lab.isupper() else 'b', lab.upper(), sq))
    pos, fen, w, b, unk = position_of(items)
    return pos, fen, '%d+%d' % (w, b) + ('+%d?' % unk if unk else '')


def surname_key(author):
    return [re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', a.strip().split()[-1].lower())
                   .encode('ascii', 'ignore').decode()) for a in re.split(r'&|,| et ', author) if a.strip()]


def same_author(a, b):
    return bool(set(surname_key(a)) & set(surname_key(b)))


def finish(rec):
    """Final clean-up of one record: proof-game stipulations, counts check, orthodoxy."""
    conds = rec.get('conditions', [])
    stip = rec.get('stip') or ''
    if re.fullmatch(r'partie', stip, re.I):
        for c in conds[:2]:
            if re.match(r'justificative', c, re.I):
                rec['stip'] = stip + ' ' + c
                conds.remove(c)
                break
    elif stip and conds and not re.search(r'[\d#=+]', stip) and re.match(r'[a-zé]', conds[0]):
        rec['stip'] = stip + ' ' + conds.pop(0)      # 'Résoudre' / 'la position', 'Plus courte' / 'résolution ?'
    if rec.get('position') and not re.search(r'[A-Z{]', rec['position']):
        rec['position'] = None                         # empty board (construction task)
    m = re.match(r'partie justificative en (\d+)[,.](\d)', rec.get('stip') or '', re.I)
    if m:
        rec['stip'] = 'PG %s.%s' % m.groups() if m.group(2) != '0' else 'PG %s' % m.group(1)
    for c in list(conds):
        if re.fullmatch(r'\d+ solutions?|(\d+\.){2,}\d*\.*', c):
            rec['play'] = c
            conds.remove(c)
    if conds:
        rec['conditions'] = conds
    else:
        rec.pop('conditions', None)
    pieces = rec.pop('pieces', None)
    if pieces and rec.get('count') and '?' not in pieces and 'n' not in rec['count'] and \
            pieces != rec['count'] and rec.get('position'):
        rec['warning'] = 'diagram shows %s pieces, caption says %s' % (pieces, rec['count'])
    twins = rec.get('twins', [])
    rec['orthodox'] = bool(rec.get('fen')) and not conds and all(SIMPLE_TWIN.match(t) for t in twins) and \
        'warning' not in rec
    order = ['number', 'position', 'fen', 'stip', 'play', 'marks', 'count', 'tested', 'author', 'source', 'award',
             'tourney', 'dedication', 'context', 'twins', 'conditions', 'solution', 'solution_fr', 'solution_note', 'comment', 'orthodox',
             'marked_squares', 'warning', 'page', 'image']
    return {k: rec[k] for k in order if k in rec and (rec[k] not in (None, '', []) or k == 'fen')}


def parse(mirror):
    recs, sols = [], {}
    files = []
    for root, _, fns in os.walk(mirror):
        for fn in fns:
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, mirror).replace(os.sep, '/')
            # originals (issues, "inédits") first: their source line is the most precise
            rank = 0 if 'telechargement' in rel and 'la_revue' in rel else 1 if fn.lower().endswith('.pdf') else 2
            files.append((rank, rel, path))
    npdf = nhtml = 0
    for rank, rel, path in sorted(files):
        url = BASE + '/' + urllib.parse.quote(rel)
        if rel.lower().endswith('.pdf'):
            npdf += 1
            r, s = pdf_problems(path, url)
            for k, v in s.items():
                sols.setdefault((url, k), v)
                if re.fullmatch(r'\d{3,5}', k):
                    sols.setdefault(k, v)
            ctx = next((v for k, v in CONTEXT if k in rel.lower()), None)
            recs += [dict(x, _doc=url, **({'context': ctx} if ctx else {})) for x in r]
        elif re.search(r'\.(php|html?)$', rel, re.I):
            raw = open(path, 'rb').read()
            try:
                page = raw.decode('utf-8')
            except UnicodeDecodeError:
                page = raw.decode('cp1252', 'replace')
            if not re.search(r'<img\b[^>]*diagramm?es?/', page, re.I):
                continue
            nhtml += 1
            recs += html_problems(page, url, rel, mirror, classify_image)
    nsol = 0
    for r in recs:
        doc = r.pop('_doc', None)
        num = r.get('number')
        s = sols.get((doc, num)) or (sols.get(num) if num and re.fullmatch(r'\d{3,5}', num) else None)
        note = None
        if s and r.get('author') and s['author'] and not same_author(r['author'], s['author']):
            # the solution pages sometimes number the problems differently: look for the author nearby
            s, near = None, []
            if re.fullmatch(r'\d{3,5}', num):
                for d in range(1, 4):
                    for k in (str(int(num) - d), str(int(num) + d)):
                        c = sols.get((doc, k))
                        if c and same_author(r['author'], c['author']):
                            near.append(c)
                    if near:
                        break
            if len(near) == 1:
                s, note = near[0], 'solution found under another number (the source numbers them differently)'
        if s and 'solution' not in r:
            if note:
                r['solution_note'] = note
            r['solution_fr'] = join_lines(s['lines'])
            r['solution'] = english(r['solution_fr'])
            nsol += 1
            a = r.get('author', '')
            if s['author'] and (not a or (re.search(r'\b[A-Z]\.', a) and surname_key(a) == surname_key(s['author']))):
                r['author'] = s['author']
    recs = [finish(r) for r in recs if r.get('stip') or r.get('count') or r.get('number')]
    # the same problem appears as an original, in its award, on the award web page...
    uniq, index, by_fen = [], {}, {}
    for r in recs:
        key = (r.get('position') or r.get('image'), r.get('stip'), str(r.get('twins')), str(r.get('conditions')))
        fkey = (r.get('fen'), r.get('stip')) if r.get('fen') else None
        other = index.get(key) or (by_fen.get(fkey) if fkey else None)
        if other is not None:
            for k, v in r.items():
                if k not in other and k not in ('orthodox', 'context', 'warning'):
                    other[k] = v
            continue
        index[key] = r
        if fkey:
            by_fen.setdefault(fkey, r)
        uniq.append(r)
    for r in uniq:
        r['orthodox'] = r.pop('orthodox')             # keep the field order stable after merges
        for k in ('page', 'image'):
            if k in r:
                r[k] = r.pop(k)
    print('%d PDFs, %d HTML award pages, %d diagrams, %d solutions attached' % (npdf, nhtml, len(recs), nsol),
          file=sys.stderr)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'parse'])
    ap.add_argument('mirror')
    ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'phenix.json'))
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.mirror)
        return
    uniq = parse(a.mirror)
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
    orth = sum(1 for r in uniq if r['orthodox'])
    print(f'{len(uniq)} unique problems, {sum(1 for r in uniq if r.get("fen"))} with FEN, {orth} orthodox, '
          f'{sum(1 for r in uniq if r.get("solution"))} with solution -> {out}', file=sys.stderr)


if __name__ == '__main__':
    main()
