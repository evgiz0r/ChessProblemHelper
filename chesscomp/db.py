"""Problem database: query and iterate over the problem collections in knowledge/.

    from chesscomp import db
    db.stats()                                          -> counts by collection / stipulation
    for rec in db.select(stip='#2', orthodox=True, author='caillaud', text='Grimshaw'): ...
    rec = db.get('psis-0220065664')
    p = db.to_problem(rec)                              -> chesscomp.Problem, or None if unsupported
    db.published_keys(rec)                              -> ['Qxb4'] (album notation, from the solution text)
    db.run('check', stip='#2', limit=200, jobs=4)       -> resumable batch run, see below

Batch runs apply a task to every selected record and append one JSON line per record to
knowledge/runs/<name>.jsonl. A rerun skips ids already in that file, so a run can be stopped and resumed,
and its results travel with the repository (commit the file). A task is a function rec -> dict, given by
name (see TASKS) or as 'module:function'.

CLI:
    python -m chesscomp.db stats
    python -m chesscomp.db list --stip '#2' --author caillaud --limit 10
    python -m chesscomp.db show psis-0220065664
    python -m chesscomp.db run check --stip '#2' --orthodox --limit 500 --jobs 4 [--name check-2]
"""
from __future__ import annotations
import argparse, importlib, json, os, re, sys
from functools import lru_cache

from .knowledge import DIR

COLLECTIONS = {'problemesis': 'problemesis.json'}
RUNS = os.path.join(DIR, 'runs')


# ---------------------------------------------------------------- loading and querying

@lru_cache(maxsize=None)
def load(collection: str = 'problemesis') -> tuple:
    with open(os.path.join(DIR, COLLECTIONS[collection]), encoding='utf-8') as f:
        return tuple(json.load(f)['problems'])


def records(collection: str | None = None):
    for c in ([collection] if collection else COLLECTIONS):
        for r in load(c):
            yield {'collection': c, **r}


def norm_stip(s: str | None) -> str | None:
    """'h#2,5' -> 'h#2.5' ; anything else unchanged."""
    return re.sub(r'(\d),5\b', r'\1.5', s.strip()) if s else s


def select(stip: str | None = None, orthodox: bool | None = None, author: str | None = None,
           source: str | None = None, text: str | None = None, twins: bool | None = None,
           solved: bool | None = None, collection: str | None = None, where=None, limit: int | None = None):
    """Filter records. String filters are case-insensitive substrings, except stip (exact, after
    normalising '2,5' to '2.5'; a trailing '*' matches any, e.g. 'h#*' or 's#*'). `text` searches the
    solution (theme names are listed there). `where` is an extra predicate rec -> bool."""
    n = 0
    want = norm_stip(stip)
    for r in records(collection):
        s = norm_stip(r.get('stip'))
        if want and not (s == want or want.endswith('*') and (s or '').startswith(want[:-1])):
            continue
        if orthodox is not None and bool(r.get('orthodox')) != orthodox:
            continue
        if twins is not None and bool(r.get('twins')) != twins:
            continue
        if solved is not None and bool(r.get('solution')) != solved:
            continue
        if author and author.lower() not in (r.get('author') or '').lower():
            continue
        if source and source.lower() not in (r.get('source') or '').lower():
            continue
        if text and text.lower() not in (r.get('solution') or '').lower():
            continue
        if where and not where(r):
            continue
        yield r
        n += 1
        if limit and n >= limit:
            return


def get(id: str) -> dict | None:
    return next((r for r in records() if r['id'] == id), None)


def stats() -> dict:
    from collections import Counter
    out = {}
    for c in COLLECTIONS:
        rs = load(c)
        out[c] = {'problems': len(rs), 'orthodox': sum(1 for r in rs if r.get('orthodox')),
                  'with_solution': sum(1 for r in rs if r.get('solution')),
                  'orthodox_by_stip': dict(Counter(norm_stip(r['stip']) for r in rs if r.get('orthodox')).most_common(15))}
    return out


# ---------------------------------------------------------------- bridging to the solver

def to_problem(rec: dict):
    """A chesscomp Problem for an orthodox, untwinned record with a supported stipulation, else None."""
    from .core import Problem, Stipulation
    if not rec.get('fen') or not rec.get('orthodox') or rec.get('twins'):
        return None
    st = norm_stip(rec.get('stip'))
    try:
        Stipulation.parse(st)
    except ValueError:
        return None
    return Problem.from_fen(rec['fen'], st, id=rec['id'], author=rec.get('author'), source=rec.get('source'))


def _clean(move: str) -> str:
    return re.sub(r'[+#!?]+$', '', move).replace('N', 'S').replace('O-O', '0-0')


def published_keys(rec: dict) -> list[str]:
    """Key move(s) of a direct/self problem as printed: '1.Qxb4!' (not tries '1.X?' nor refutations '1...X!')."""
    return [_clean(m) for m in re.findall(r'(?<![.\d])1\.(?!\.)([^\s!?\[\]]+)!(?![?!])', rec.get('solution') or '')]


def published_help_lines(rec: dict) -> list[str]:
    """Solution lines of a helpmate as printed ('1.Se2 Rxe3 2.Sxe3 Rh4#')."""
    return [l.strip() for l in (rec.get('solution') or '').split('\n') if re.match(r'\s*1\.', l)]


# ---------------------------------------------------------------- tasks

def task_check(rec: dict, time_limit: float = 60) -> dict:
    """Solve the problem and compare with the published solution."""
    from .analysis import analyse
    p = to_problem(rec)
    if p is None:
        return {'status': 'unsupported'}
    res = analyse(p, include_tries=False, include_set=False, time_limit=time_limit)
    out = {'seconds': res.get('seconds')}
    if res.get('timeout'):
        return {**out, 'status': 'timeout'}
    if p.stip.kind == 'help':
        sols = [s['line'] for s in res.get('solutions', [])]
        pub = published_help_lines(rec)
        first = lambda l: _clean(l.split()[0].split('.')[-1])
        match = sorted(map(first, pub)) == sorted(map(first, sols)) if pub else None
        return {**out, 'status': 'ok' if match else ('no_published' if match is None else 'mismatch'),
                'solver': sols, 'published': pub}
    keys = [_clean(k) for k in res.get('keys', [])]
    pub = published_keys(rec)
    if not pub:
        status = 'no_published'
    elif not keys:
        status = 'unsound'                       # no key found
    elif len(keys) > 1:
        status = 'cooked' if set(pub) & set(keys) else 'mismatch'
    else:
        status = 'ok' if keys[0] in pub else 'mismatch'
    return {**out, 'status': status, 'solver': keys, 'published': pub}


def task_analyse(rec: dict, time_limit: float = 120) -> dict:
    """Full chesscomp analysis (phases, relations, motives), JSON-serialisable."""
    from .analysis import analyse
    p = to_problem(rec)
    if p is None:
        return {'status': 'unsupported'}
    res = analyse(p, time_limit=time_limit)
    return {'status': 'timeout' if res.get('timeout') else 'ok', 'analysis': res}


TASKS = {'check': task_check, 'analyse': task_analyse}


def _resolve(task):
    if callable(task):
        return task
    if task in TASKS:
        return TASKS[task]
    mod, fn = task.split(':')
    return getattr(importlib.import_module(mod), fn)


def _apply(args):
    task, rec = args
    try:
        return {'id': rec['id'], **_resolve(task)(rec)}
    except Exception as e:                       # one bad record must not stop a long run
        return {'id': rec['id'], 'status': 'error', 'error': repr(e)}


def run_path(name: str) -> str:
    return os.path.join(RUNS, name + '.jsonl')


def results(name: str) -> dict:
    """{id: result} of a batch run (last line wins)."""
    p = run_path(name)
    if not os.path.exists(p):
        return {}
    out = {}
    for line in open(p, encoding='utf-8'):
        if line.strip():
            r = json.loads(line)
            out[r['id']] = r
    return out


def run(task, name: str | None = None, jobs: int = 1, progress: bool = True, **filters) -> dict:
    """Apply `task` to every selected record not yet in knowledge/runs/<name>.jsonl. Returns status counts."""
    from collections import Counter
    name = name or (task if isinstance(task, str) else task.__name__).replace(':', '.')
    done = set(results(name))
    todo = [r for r in select(**filters) if r['id'] not in done]
    os.makedirs(RUNS, exist_ok=True)
    counts = Counter()
    task_ref = task if isinstance(task, str) else f'{task.__module__}:{task.__name__}'
    with open(run_path(name), 'a', encoding='utf-8') as f:
        if jobs > 1:
            from multiprocessing import Pool
            pool = Pool(jobs)
            it = pool.imap_unordered(_apply, [(task_ref, r) for r in todo])
        else:
            pool, it = None, map(_apply, [(task_ref, r) for r in todo])
        try:
            for i, res in enumerate(it, 1):
                f.write(json.dumps(res, ensure_ascii=False) + '\n')
                f.flush()
                counts[res.get('status')] += 1
                if progress and (i % 25 == 0 or i == len(todo)):
                    print(f'{i}/{len(todo)} {dict(counts)}', file=sys.stderr)
        finally:
            if pool:
                pool.terminate()
    if progress:
        print(f'{len(done)} already done, {len(todo)} run -> {run_path(name)}', file=sys.stderr)
    return dict(counts)


# ---------------------------------------------------------------- CLI

def _filters(a):
    return dict(stip=a.stip, orthodox=True if a.orthodox else None, author=a.author, source=a.source,
                text=a.text, twins=False if a.no_twins else None, limit=a.limit)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python -m chesscomp.db')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('stats')
    sh = sub.add_parser('show')
    sh.add_argument('id')
    for name in ('list', 'run'):
        p = sub.add_parser(name)
        if name == 'run':
            p.add_argument('task', help=f"{', '.join(TASKS)} or module:function")
            p.add_argument('--name', help='run name (file knowledge/runs/<name>.jsonl); default: the task name')
            p.add_argument('--jobs', type=int, default=1)
        p.add_argument('--stip')
        p.add_argument('--orthodox', action='store_true')
        p.add_argument('--no-twins', action='store_true')
        p.add_argument('--author')
        p.add_argument('--source')
        p.add_argument('--text', help='substring of the solution text (themes are named there)')
        p.add_argument('--limit', type=int)
    a = ap.parse_args(argv)
    if a.cmd == 'stats':
        print(json.dumps(stats(), indent=1, ensure_ascii=False))
    elif a.cmd == 'show':
        print(json.dumps(get(a.id), indent=1, ensure_ascii=False))
    elif a.cmd == 'list':
        for r in select(**_filters(a)):
            print(f"{r['id']}  {norm_stip(r['stip']) or '?':8} {r.get('count') or '':6} {r.get('author') or ''} "
                  f"| {(r.get('source') or '').replace(chr(10), ' / ')} | {r.get('fen') or r['position']}")
    elif a.cmd == 'run':
        print(json.dumps(run(a.task, name=a.name, jobs=a.jobs, **_filters(a))))


if __name__ == '__main__':
    main()
