import io, json, contextlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import blog


def test_next_theme_skips_paused_themes():
    # E. Bourd, 20 Oct 2026: dailies take practiced themes; Le Grand, Zagoruiko, reciprocal change are paused
    themes = json.load(open(blog.THEMES, encoding='utf-8'))['themes']
    paused = {t['id'] for t in themes if t.get('paused')}
    assert {'le-grand', 'zagoruiko', 'reciprocal-change'} <= paused
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        blog.next_theme()
    assert json.loads(out.getvalue())['id'] not in paused
