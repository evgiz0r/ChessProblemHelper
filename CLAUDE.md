# ChessProblemHelper

Chess problem solver/analyser (`chesscomp/`) built with composer Evgeni Bourd. See README.md for the
toolkit; `knowledge/session_log.md` records past composing sessions.

## Setup

`pip install --use-pep517 -r requirements.txt` (plain `pip install` fails to build chess>=1.11 here).
The SessionStart hook in `.claude/hooks/session-start.sh` does this automatically in web sessions.

## Problem database

`knowledge/problemesis.json`: 7,912 problems crawled from the Problemesis web magazine
(christian.poisson.free.fr, 1998–2006), 5,334 of them orthodox with a FEN. Each record has a stable `id`
(`psis-…`), `position` (French notation as printed), `fen`, `stip`, `count`, `author`, `source` (magazine,
year, award), optional `number`, `twins`, `conditions` (fairy), `play` (e.g. `2.1.1.1`), `solution`
(English notation, `#`, `x`; theme names follow the moves), `solution_fr`, `orthodox`, `pages`.

Query and iterate with `chesscomp/db.py`:

```bash
python -m chesscomp.db stats
python -m chesscomp.db list --stip '#2' --orthodox --author bourd --limit 10
python -m chesscomp.db list --text Grimshaw --stip 'h#*'
python -m chesscomp.db show psis-7323fac2ab
python -m chesscomp.db run check --stip '#2' --orthodox --no-twins --jobs 4      # solver vs published key
python -m chesscomp.db run mymodule:myfunc --stip 'h#2' --name my-run           # any rec -> dict function
```

```python
from chesscomp import db
for rec in db.select(stip='#2', orthodox=True, text='Zagoruiko'):
    p = db.to_problem(rec)            # chesscomp.Problem (None for twins/fairy/unsupported stipulations)
```

Batch runs append one JSON line per record to `knowledge/runs/<name>.jsonl` and skip ids already there,
so a long run can be interrupted and resumed. Containers are ephemeral: commit and push run files you want
to keep. `check` statuses: ok, mismatch, cooked, unsound, timeout, unsupported, no_published, error.

To add or refresh a collection: `python tools/problemesis.py crawl DIR` then `parse DIR`
(the parser is deterministic; ids are a hash of position + stipulation + twins + conditions).
New collections are registered in `db.COLLECTIONS`.
