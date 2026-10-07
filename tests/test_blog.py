"""The daily blog: the site builds from the posts, and the publishing gate refuses what must never appear."""
import os, sys, subprocess, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import blog


def test_build_writes_every_post():
    blog.build()
    posts = blog.load_posts()
    assert posts, 'no posts'
    for p in posts:
        assert os.path.exists(os.path.join(blog.OUT, p['slug'] + '.html'))
        for key in ('date', 'title', 'theme', 'fen', 'stip', 'author', 'source', 'solution', 'comment'):
            assert key in p, (p['slug'], key)
    assert os.path.exists(os.path.join(blog.OUT, 'index.html'))
    assert os.path.exists(os.path.join(blog.OUT, 'feed.xml'))


def test_posts_name_a_known_theme():
    themes = {t['id'] for t in json.load(open(blog.THEMES))['themes']}
    for p in blog.load_posts():
        assert p['theme'] in themes, p['slug']


def _gate(fen):
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'blog.py'), 'check', fen], capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout


def test_gate_refuses_a_cook():
    code, out = _gate('5b2/8/p4N2/P4n2/K1kBpN1p/1Np4q/8/3Q4')   # 1.Be3 and 1.Qh5 both solve
    assert code == 1 and 'cook' in out


def test_gate_refuses_an_anticipation():
    code, out = _gate('3n1KB1/3p1n2/2p1k3/8/5P1B/2PQ4/8/8')     # Slesarenko & Gvozdjak 1999
    assert code == 1 and 'anticipation' in out


def test_gate_passes_a_sound_original():
    code, out = _gate('3R4/4b3/K7/1Np2n2/2kPp2p/B1p4q/2P5/3Q4')  # E. Bourd, session 28
    assert code == 0, out


def _rules(fen):
    from chesscomp import Problem
    from chesscomp.critique import critique
    return {f['rule'] for f in critique(Problem.from_fen(fen + ' w - - 0 1', '#2'))['findings']}


def test_mentor_fatal_rules_7_october():
    # E. Bourd on daily No. 2: a key by a knight out of play is fatal
    assert 'out-of-play key' in _rules('3R4/8/6K1/4P3/3bk3/N1p3Q1/8/8')
    # E. Bourd on daily No. 1: a unit that only plays the thematic try is fatal
    assert 'try-only unit' in _rules('6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1')
    for rule in ('out-of-play key', 'try-only unit', 'superfluous piece'):
        assert rule in blog.FATAL


def test_try_only_unit_even_when_its_tries_carry_changes():
    # c7 pawn: no part in the solution, only promotion tries (with a changed mate) - still fatal
    assert 'try-only unit' in _rules('4K3/2Pp3B/4k3/8/3Q4/8/8/8')
