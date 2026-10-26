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


def test_theme_references_exist_and_their_example_is_sound():
    """Every theme reference named in blog/themes.json is a file; a reference .md that names a #2 FEN in its
    'Reference:' line gives that position's key (daily No. 6: the Grimshaw reference)."""
    import re, chess
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    for t in json.load(open(blog.THEMES))['themes']:
        ref = t.get('reference')
        if not ref:
            continue
        first = ref.split()[0].rstrip(';')
        assert os.path.exists(os.path.join(ROOT, first)), (t['id'], first)
    text = open(os.path.join(ROOT, '.claude/skills/themes/references/grimshaw.md')).read()
    fen = re.search(r'Reference:.*?([1-8KQRBNPkqrbnp/]{15,})', text).group(1)
    res = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_tries=False, include_set=False, time_limit=60)
    assert res['keys'] == ['Rf3'], res['keys']


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
    # E. Bourd on daily No. 1: a unit that only plays the thematic try; 11 Oct: a drawback, not fatal
    assert 'try-only unit' in _rules('6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1')
    for rule in ('out-of-play key', 'superfluous piece'):
        assert rule in blog.FATAL
    assert 'try-only unit' not in blog.FATAL


def test_try_only_unit_even_when_its_tries_carry_changes():
    # c7 pawn: no part in the solution, only promotion tries (with a changed mate) - reported (a drawback)
    assert 'try-only unit' in _rules('4K3/2Pp3B/4k3/8/3Q4/8/8/8')


def test_plug_that_also_plays_a_try_is_not_try_only():
    # E. Bourd's Kc5 bishop-rook battery (18 Oct 2026): wPd7 cuts Be8 from c6 (no solution without it) and also
    # plays 1.d8=Q?; it is not a unit "only for a try". Nor a cook-stopper: the solution needs it, so it is part of the
    # problem (E. Bourd, 26 Oct 2026, on Kisis's Sc1: "what cook exactly are they stopping")
    from chesscomp import Problem
    from chesscomp.critique import critique
    f = critique(Problem.from_fen('K3b3/3P4/2B2R2/B1k1NP2/1nP3n1/b1P3pq/5R2/6Q1 w - - 0 1', '#2'))['findings']
    d7 = {x['rule'] for x in f if x['msg'].startswith('wPd7')}
    assert d7 == {'solution guard'}                  # wPf5 stays a real cook-stopper: it stops 1.Bd5


def test_white_correction_with_king_tries_in_the_threat_pool():
    # E. Bourd (18 Oct 2026): 1.B~? Qg2+!, 1.Bd5!? Sxf6!, 1.Be4!? Sxe5!, 1.Bf3?! Sxe5!, 1.Bb7!; 1.Kb7?/Ka7? Sd5! also carry
    # the threat and must not turn the random stage into 'same refutation'
    from chesscomp import Problem
    from chesscomp.critique import critique
    fs = critique(Problem.from_fen('K3b3/3P4/2B2R2/B1k1NP2/1nP3n1/b1P3pq/5R1P/6Q1 w - - 0 1', '#2'))['findings']
    wc = [f for f in fs if f['rule'] == 'white correction']
    assert len(wc) == 1 and 'Qg2+' in wc[0]['msg']
    assert not any(f['rule'] == 'same refutation' and f['severity'] == 'major' for f in fs)


def test_single_phase_needs_tries_or_changes():
    # E. Bourd (18 Oct 2026): "anything that is a single phase without tries or changes is not pass for publication
    # unless the single phase is very complicated or pretty"
    from chesscomp import Problem
    from chesscomp.critique import critique
    rules = lambda fen: {f['rule'] for f in critique(Problem.from_fen(fen + ' w - - 0 1', '#2'))['findings']}
    assert 'single phase' in rules('1K6/1B6/8/p1N2Qnp/1b1k4/3P1bN1/1PPn1P2/7q')            # 1.Be4!, no tries
    assert 'single phase' not in rules('2b1KB2/3p4/4N1N1/1P1kPBp1/1P4R1/1P1pp3/pbrr4/q1R5')  # Dombrovskis tries
    assert 'single phase' not in rules('8/6Q1/6N1/8/1p2k3/3nNpK1/2rP1P2/1B2n3')            # try pair, a change


def test_random_tries_are_not_a_second_phase():
    # E. Bourd (18 Oct 2026): "i meant no thematic tries or changes. random tries dont count" - 1.Bd3! has three bishop
    # tries, all refuted by 1...Ra3!, which is no defence after the key
    from chesscomp import Problem
    from chesscomp.critique import critique
    fs = critique(Problem.from_fen('2N5/3p1K1p/Q7/3nkB2/rbPn3N/6P1/1B6/8 w - - 0 1', '#2'))['findings']
    assert any(f['rule'] == 'single phase' for f in fs)
