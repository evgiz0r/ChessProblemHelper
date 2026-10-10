"""Send a position to the bench: print a link that opens the Composing Bench with this diagram loaded.

    python tools/bench_link.py "<FEN>" [--stip "#2"] [--from "Daily No. 5"]

The bench reads ?fen=<FEN>&stip=<stip>&from=<label> on load (docs/bench/index.html, boot).
Put the link under every problem shown in chat, in a blog post or a mentor issue.
"""
import argparse
from urllib.parse import urlencode

BENCH = 'https://evgiz0r.github.io/ChessProblemHelper/bench/'


def bench_url(fen, stip='#2', source=''):
    q = {'fen': fen.split()[0], 'stip': stip}
    if source:
        q['from'] = source
    return BENCH + '?' + urlencode(q, safe='/')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('fen')
    ap.add_argument('--stip', default='#2')
    ap.add_argument('--from', dest='source', default='')
    a = ap.parse_args()
    print(bench_url(a.fen, a.stip, a.source))
