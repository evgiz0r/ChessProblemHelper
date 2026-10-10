"""Show a position to E. Bourd: the one way every session prints a diagram (E. Bourd, 10 Oct 2026).

    python tools/show.py <name> "<FEN>"

Writes a square board to docs/blog/cards/<name>.png and prints what to do with it:
- in a Claude Code chat: send that PNG with SendUserFile (display "render"); a markdown image link opens a
  new tab on his computer, a wide card is cropped on his phone;
- in a GitHub issue or a blog post: the raw.githubusercontent link on main (commit and push the PNG first);
- always: the FEN as text and the link to the Composing Bench, where he can set it up and solve it.
"""
import json, os, subprocess, sys

BENCH = 'https://claude.ai/code/artifact/acc24a96-d9f6-4076-98a9-7915ed586916'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) != 3:
    sys.exit(__doc__)
name, fen = sys.argv[1], sys.argv[2].split()[0]
rel = f'docs/blog/cards/{name}.png'
subprocess.run([sys.executable, os.path.join(ROOT, 'tools/card_png.py'), os.path.join(ROOT, rel), '--board'],
               input=json.dumps({'fen': fen, 'lines': []}), text=True, check=True)
print(f'''chat:   SendUserFile {{"files": ["{rel}"], "display": "render"}}
github: ![{name}](https://raw.githubusercontent.com/evgiz0r/ChessProblemHelper/main/{rel})
text:   FEN `{fen}` - open it on the bench: {BENCH}''')
