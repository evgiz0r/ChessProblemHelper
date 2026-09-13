"""Knowledge base: the composer's vocabulary and judgement, stored as data the tools (and an AI) can load.

    from chesscomp import knowledge as kb
    kb.theme('bristol')                 -> definition, detector, source
    kb.find('the queen follows the bishop on the diagonal')  -> candidate themes
    kb.record_lesson('Grimshaw', 'prefer the interference square next to the king', source='E. Bourd s2')
"""
from __future__ import annotations
import json, os, re, datetime

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'knowledge')


def _load(name, default):
    p = os.path.join(DIR, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


def themes() -> dict:
    return _load('themes.json', {})


def principles() -> list:
    return _load('principles.json', [])


def lessons() -> list:
    p = os.path.join(DIR, 'lessons.jsonl')
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def theme(name: str) -> dict | None:
    t = themes()
    for k, v in t.items():
        if k.lower() == name.lower():
            return {'name': k, **v, 'lessons': [l for l in lessons() if l.get('topic', '').lower() == k.lower()]}
    return None


_SYN = {'follow': ['Bristol'], 'clearance': ['Bristol'], 'cross': ['Grimshaw'], 'crossing': ['Grimshaw'],
        'interfere': ['Grimshaw', 'White interference try'], 'reciprocal': ['Reciprocal change'],
        'swap': ['Reciprocal change', 'Threat reversal'], 'three phases': ['Zagoruiko'], 'cycle': ['Zagoruiko'],
        'self-block': ['Self-block'], 'selfblock': ['Self-block'], 'change': ['Changed mates'],
        'threat becomes': ['Le Grand', 'Pseudo Le Grand'], 'bishop choice': ['Pickabish']}


def find(text: str) -> list:
    """Map a composer's free-text description to candidate themes (keyword + definition overlap)."""
    text_l = text.lower()
    scores = {}
    for k, v in themes().items():
        s = 3 if k.lower() in text_l else 0
        words = set(re.findall(r'[a-z]{4,}', v['definition'].lower()))
        s += len(words & set(re.findall(r'[a-z]{4,}', text_l))) * 0.5
        scores[k] = s
    for w, ts in _SYN.items():
        if w in text_l:
            for t in ts:
                scores[t] = scores.get(t, 0) + 2
    return [k for k, s in sorted(scores.items(), key=lambda x: -x[1]) if s >= 1.5][:5]


def record_lesson(topic: str, text: str, source: str = 'E. Bourd', kind: str = 'principle', example: str | None = None):
    """Persist something learned. Appends to knowledge/lessons.jsonl (never overwrites)."""
    rec = {'date': datetime.date.today().isoformat(), 'topic': topic, 'kind': kind, 'text': text, 'source': source}
    if example:
        rec['example'] = example
    with open(os.path.join(DIR, 'lessons.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return rec


def add_theme(name: str, definition: str, source: str, detector: str | None = None, **extra):
    t = themes()
    t[name] = {'definition': definition, 'detector': detector, 'source': source, **extra}
    json.dump(t, open(os.path.join(DIR, 'themes.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return t[name]
