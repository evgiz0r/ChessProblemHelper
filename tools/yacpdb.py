"""Pull problems from YACPDB (www.yacpdb.org) through its query-language gateway and store them compactly.

YACPDB answers `gateway/ql?q=<query>&p=<page>` with 100 full entries per page, ordered by id; a page takes
about 4-5 s to serve, so the crawl is sequential and pauses between pages. Raw pages are kept in a mirror
directory, so an interrupted crawl resumes where it stopped. `build` turns the pages into gzipped JSON-lines
shards (one problem per line) in the same record shape as the other collections: position in English
algebraic, fen, stip, author, source, award, keywords, solution, orthodox, plus the YACPDB id and url.

usage:
    python tools/yacpdb.py crawl MIRROR_DIR [-q 'Stip("#2")']        # fetch every result page
    python tools/yacpdb.py build MIRROR_DIR [-o knowledge/yacpdb] [--name twomovers] [--shard 40000]
    python tools/yacpdb.py query 'Stip("#2") AND Keyword("Le Grand")' [-p 1]   # one page, printed as JSON

Query syntax: https://www.yacpdb.org/#static/help  (e.g. Author("Bourd, Evgeni"), Keyword("Zagoruiko"),
Stip("h#2"), combined with AND, OR, NOT).
"""
import argparse, gzip, json, os, re, sys, time, urllib.parse, urllib.request

GATE = 'https://www.yacpdb.org/gateway/ql'
UA = 'ChessProblemHelper/1.0 (chess problem research; github.com/evgiz0r/ChessProblemHelper)'
ORTHO = re.compile(r'[KQRBSP][a-h][1-8]')


def fetch(query, page, tries=5):
    url = GATE + '?' + urllib.parse.urlencode({'q': query, 'p': page})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            if not d.get('success'):
                raise RuntimeError(str(d.get('error'))[-300:])
            return d['result']
        except Exception as e:
            print(f'page {page}: {e}; retry {i + 1}', file=sys.stderr)
            time.sleep(10 * 2 ** i)
    raise RuntimeError(f'page {page} failed {tries} times')


# ---------------------------------------------------------------- crawl

def crawl(mirror, query, delay=1.0):
    os.makedirs(mirror, exist_ok=True)
    with open(os.path.join(mirror, 'query.txt'), 'w') as f:
        f.write(query + '\n')
    page, pages = 1, None
    while pages is None or page <= pages:
        dest = os.path.join(mirror, f'p{page:05d}.json')
        if os.path.exists(dest):
            if pages is None:
                pages = -(-json.load(open(dest))['count'] // 100)
            page += 1
            continue
        res = fetch(query, page)
        pages = -(-int(res['count']) // 100)
        tmp = dest + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'count': int(res['count']), 'entries': res['entries']}, f, ensure_ascii=False)
        os.replace(tmp, dest)
        if page % 50 == 0 or page == pages:
            print(f'{page}/{pages}', file=sys.stderr)
        page += 1
        time.sleep(delay)


# ---------------------------------------------------------------- build

def fen_of(white, black):
    board = {}
    for pieces, colour in ((white, str.upper), (black, str.lower)):
        for p in pieces:
            if not ORTHO.fullmatch(p) or p[1:] in board:
                return None
            board[p[1:]] = colour(p[0].replace('S', 'N'))
    if sorted(v for v in board.values() if v in 'Kk') != ['K', 'k']:
        return None
    rows = []
    for rank in '87654321':
        row, empty = '', 0
        for f in 'abcdefgh':
            v = board.get(f + rank)
            if v:
                row += (str(empty) if empty else '') + v
                empty = 0
            else:
                empty += 1
        rows.append(row + (str(empty) if empty else ''))
    return '/'.join(rows)


def date_str(d):
    return '-'.join(f'{d[k]:02d}' if k != 'year' else str(d[k]) for k in ('year', 'month', 'day') if k in d)


def source_str(s):
    if not s:
        return None
    bits = [s.get('name', '')]
    if 'issue' in s:
        bits.append(f"#{s['issue']}")
    if 'problemid' in s:
        bits.append(f"no. {s['problemid']}")
    if 'date' in s:
        bits.append(date_str(s['date']))
    return ', '.join(str(b) for b in bits if b)


def award_str(a):
    if not a:
        return None
    t = a.get('tourney', {}).get('name')
    return ' '.join(str(x) for x in (a.get('distinction'), t and f'({t})') if x) or None


def solution_text(s):
    """YACPDB solutions are indented by depth with runs of spaces; keep one space per level-step."""
    lines = []
    for l in s.split('\n'):
        stripped = l.lstrip(' ')
        if stripped:
            lines.append(' ' * min((len(l) - len(stripped) + 3) // 4, 6) + stripped.rstrip())
        elif lines and lines[-1]:
            lines.append('')
    return '\n'.join(lines).strip('\n')


def record(e):
    alg = e.get('algebraic', {})
    white, black = alg.get('white', []), alg.get('black', [])
    extra = {k: v for k, v in alg.items() if k not in ('white', 'black')}   # neutral pieces etc.
    fen = None if extra else fen_of(white, black)
    rec = {'id': e['id'], 'url': f"https://www.yacpdb.org/#{e['id']}",
           'position': ' '.join(white) + ' + ' + ' '.join(black), 'fen': fen,
           'stip': e.get('stipulation'), 'count': f'{len(white)}+{len(black)}',
           'author': ' & '.join(map(str, e.get('authors', []))) or None,
           'source': source_str(e.get('source')), 'award': award_str(e.get('award'))}
    if extra:
        rec['other_pieces'] = extra
    for k in ('keywords', 'twins', 'options', 'comments'):
        if e.get(k):
            rec[k] = e[k]
    if e.get('solution'):
        rec['solution'] = solution_text(e['solution'])
    rec['orthodox'] = bool(fen) and not e.get('options') and not e.get('twins')
    return {k: v for k, v in rec.items() if v is not None}


def build(mirror, out, name, shard):
    recs, seen, expected = [], set(), None
    for fn in sorted(os.listdir(mirror)):
        if re.fullmatch(r'p\d{5}\.json', fn):
            page = json.load(open(os.path.join(mirror, fn), encoding='utf-8'))
            expected = page['count']
            for e in page['entries']:
                if e['id'] not in seen:          # pages can overlap if the database grew mid-crawl
                    seen.add(e['id'])
                    recs.append(record(e))
    recs.sort(key=lambda r: r['id'])
    os.makedirs(out, exist_ok=True)
    for old in os.listdir(out):
        if re.fullmatch(re.escape(name) + r'-\d+\.jsonl\.gz', old):
            os.remove(os.path.join(out, old))
    files = []
    for i in range(0, len(recs), shard):
        fn = f'{name}-{i // shard + 1:02d}.jsonl.gz'
        with gzip.open(os.path.join(out, fn), 'wt', encoding='utf-8', compresslevel=9) as f:
            for r in recs[i:i + shard]:
                f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
        files.append({'file': fn, 'first_id': recs[i]['id'], 'last_id': recs[min(i + shard, len(recs)) - 1]['id'],
                      'count': len(recs[i:i + shard])})
    query = open(os.path.join(mirror, 'query.txt')).read().strip()
    index_path = os.path.join(out, 'index.json')
    index = json.load(open(index_path)) if os.path.exists(index_path) else {}
    index.setdefault('source', 'https://www.yacpdb.org/')
    index['note'] = ('Problems pulled from YACPDB through its query gateway (tools/yacpdb.py). Each shard is '
                     'gzipped JSON lines, one problem per line, sorted by YACPDB id.')
    index.setdefault('collections', {})[name] = {
        'query': query, 'fetched': time.strftime('%Y-%m-%d'), 'count': len(recs), 'reported_count': expected,
        'orthodox': sum(r['orthodox'] for r in recs), 'shards': files}
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f'{len(recs)} problems ({expected} reported), {index["collections"][name]["orthodox"]} orthodox, '
          f'{len(files)} shards -> {out}', file=sys.stderr)


def load(out='knowledge/yacpdb', name='twomovers'):
    """Iterate over the records of a built collection."""
    index = json.load(open(os.path.join(out, 'index.json')))
    for s in index['collections'][name]['shards']:
        with gzip.open(os.path.join(out, s['file']), 'rt', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['crawl', 'build', 'query'])
    ap.add_argument('arg', help='mirror directory (crawl, build) or query (query)')
    ap.add_argument('-q', '--query', default='Stip("#2")')
    ap.add_argument('-p', '--page', type=int, default=1)
    ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'yacpdb'))
    ap.add_argument('--name', default='twomovers')
    ap.add_argument('--shard', type=int, default=40000)
    a = ap.parse_args()
    if a.cmd == 'crawl':
        crawl(a.arg, a.query)
    elif a.cmd == 'build':
        build(a.arg, a.out, a.name, a.shard)
    else:
        res = fetch(a.arg, a.page)
        json.dump({'count': res['count'], 'problems': [record(e) for e in res['entries']]}, sys.stdout,
                  ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
