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
