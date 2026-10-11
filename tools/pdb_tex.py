"""Import a PDB (pdb.dieschwalbe.de) LaTeX export into a knowledge/ collection.

    python tools/pdb_tex.py download.tex knowledge/pdb_bourd.json [--skip-known]

PDB's "download as LaTeX" writes one \\begin{diagram} block per problem (schwalbe.sty): German piece letters
(D T L S = Q R B N), long algebraic moves (Th4-h6), German award words, the FEN in a '%\\fen{}' comment
('*N' before a piece marks a fairy piece, e.g. '*3r' a rook-lion). Records follow the problemesis schema
(id, fen, stip, count, author, source, twins, conditions, solution, orthodox) plus pdb_id, themes, comment.
Solutions are converted to the db's notation: short algebraic, English letters except S for the knight.
--skip-known leaves out positions already in the database (same FEN board part)."""
import json, re, sys

PIECE = {'D': 'Q', 'T': 'R', 'L': 'B', 'S': 'S', 'K': 'K'}
GENRES = {'2#': '#', '3#': '#', 'n#': '#', 'h#': 'h#', 's#': 's#', 'r#': 'r#'}
AWARD = [('ehrende Erwähnung', 'HM'), ('Lob', 'Comm.'), ('Preis', 'Prize'), ('Platz', 'place'),
         ('spez.', 'Special'), ('Informalturnier', 'informal tourney'), ('Thematurnier', 'theme tourney'),
         ('Schnellkompositionsturnier', 'quick composing tourney'), ('Sektion', 'section')]


def field(block, key):
    m = re.search(r'\\' + key + r'\{(.*?)\}\s*(?:%.*)?\n', block, re.S)
    return m.group(1).strip() if m else ''


def tex(s):
    return (s.replace('\\newline', '\n').replace('\\#', '#').replace('\\dots', '...').replace('\\any', '~')
             .replace('\\&', '&').replace('\\', ''))


def move_text(s):
    """German long algebraic -> db notation (short algebraic, S for knight)."""
    s = tex(s).replace('droht', 'threat').replace('dann', 'then')
    s = re.sub(r'\b(T|L)L(?=[a-h~])', lambda m: {'T': 'RL', 'L': 'BL'}[m.group(1)], s)   # lions
    s = re.sub(r'(?<![A-Za-z])([DTLSK])(?=[a-h][1-8]|x|~)', lambda m: PIECE[m.group(1)], s)
    s = re.sub(r'=([DTLS])', lambda m: '=' + PIECE[m.group(1)], s)
    s = re.sub(r'#,([DTLS])#', lambda m: '#,' + PIECE[m.group(1)] + '#', s)
    s = re.sub(r'(?<![A-Za-z])([KQRBS]{1,2})[a-h][1-8]-(?=[a-h][1-8])', r'\1', s)       # Rh4-h6 -> Rh6
    s = re.sub(r'(?<![A-Za-z])([KQRBS]{1,2})[a-h][1-8](?=x)', r'\1', s)                 # Rf2xd2 -> Rxd2
    s = re.sub(r'(?<![A-Za-z\d])([a-h])[1-8]x', r'\1x', s)                               # c7xd6 -> cxd6
    s = re.sub(r'(?<![A-Za-z\d])[a-h][1-8]-([a-h][1-8])', r'\1', s)                      # f6-f7 -> f7
    s = re.sub(r'(\d)\. \.\.\.\s*', r'\1...', s)
    s = re.sub(r'(\d)\. (?=\S)', r'\1.', s)
    s = re.sub(r'[ \t]+', ' ', s)
    return '\n'.join(l.strip() for l in s.split('\n') if l.strip())


def san_first_moves(sol, fen, genre):
    """White's first moves ('1. Sb1-c3!') as SAN from the diagram, so a needed disambiguation (Sbc3) survives."""
    if not fen or '*' in fen or genre not in ('2#', '3#', 'n#', 's#'):
        return sol
    import chess
    board = chess.Board(fen + ' w - - 0 1')

    def one(m):
        frm, to, promo = m.group(2), m.group(3), m.group(4)
        mv = chess.Move(chess.parse_square(frm), chess.parse_square(to),
                        chess.Piece.from_symbol(PIECE[promo[1]].replace('S', 'N')).piece_type if promo else None)
        if mv not in board.legal_moves:
            return m.group(0)
        return m.group(1) + board.san(mv).rstrip('+#').replace('N', 'S')
    return re.sub(r'(1\. )[DTLSK]?([a-h][1-8])[-x]([a-h][1-8])(=[DTLS])?', one, sol)


def award(s):
    s = tex(s)
    for de, en in AWARD:
        s = s.replace(de, en)
    return s


def parse(text):
    out = []
    for b in re.findall(r'\\begin\{diagram\}(.*?)\\end\{diagram\}', text, re.S):
        pid = re.search(r'PDB-ID: (\S+)', b).group(1)
        genre = re.search(r'Genre: (.*)', b).group(1).strip()
        m = re.search(r'%\\fen\{(.*?)\}', b)
        fen = m.group(1) if m else None
        lines = tex(field(b, 'stip')).split('\n')
        stip, rest = lines[0].strip(), [l.strip() for l in lines[1:] if l.strip()]
        twins = [l.replace(' nach ', ' -> ') for l in rest if re.match(r'[a-z]\)', l)]
        extra = [l for l in rest if l not in twins]
        fairy = genre not in GENRES or bool(fen and '*' in fen)
        w = re.search(r'\\pieces\{(.*?)\}', b)
        count = ''
        if w:
            wp, bp = (re.findall(r'\b' + c + r'[A-Z]+((?:[a-h][1-8])+)', w.group(1)) for c in 'ws')
            count = f'{sum(len(x) // 2 for x in wp)}+{sum(len(x) // 2 for x in bp)}'
        src = ' '.join(x for x in (tex(field(b, 'source')), field(b, 'sourcenr'), field(b, 'year')) if x)
        aw = award(field(b, 'award'))
        rep = re.search(r'Reprints:\s*\n%\s*(.*)', b)
        rec = {'id': 'pdb-' + pid, 'pdb_id': pid, 'fen': fen, 'stip': stip, 'count': count,
               'author': '; '.join(' '.join(reversed(a.split(', '))) for a in tex(field(b, 'author')).split('; ')),
               'source': src + ('\n' + aw if aw else ''), 'twins': twins or None,
               'conditions': extra if fairy and extra else None, 'stip_note': None if fairy else (extra or None),
               'solution': move_text(san_first_moves(field(b, 'solution'), fen, genre)), 'themes': tex(field(b, 'themes')) or None,
               'comment': tex(field(b, 'comment')) or None, 'reprint': rep.group(1).strip() if rep else None,
               'genre': genre, 'orthodox': not fairy}
        out.append({k: v for k, v in rec.items() if v is not None})
    return out


def main(argv):
    src, dst = argv[0], argv[1]
    recs = parse(open(src, encoding='utf-8').read())
    head = open(src, encoding='utf-8').read(400)
    skipped = []
    if '--skip-known' in argv:
        sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
        from chesscomp import db
        known = {}
        own = [c for c, f in db.COLLECTIONS.items() if f == __import__('os').path.basename(dst)]
        for r in db.records():
            if r.get('fen') and r['collection'] not in own:
                known.setdefault(r['fen'].split()[0], r['id'])
        skipped = [{'pdb_id': r['pdb_id'], 'same_as': known[r['fen']]} for r in recs if r.get('fen') in known]
        recs = [r for r in recs if r.get('fen') not in known]
    q = re.search(r'Query: (.*)', head)
    json.dump({'source': 'https://pdb.dieschwalbe.de', 'query': q.group(1).strip() if q else None,
               'note': 'PDB LaTeX export converted by tools/pdb_tex.py; skipped = records already in the database.',
               'count': len(recs), 'skipped': skipped, 'problems': recs},
              open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(recs)} records -> {dst}; {len(skipped)} skipped as known')


if __name__ == '__main__':
    main(sys.argv[1:])
