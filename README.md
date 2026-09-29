# Chess Problem Helper

Tools for solving, analysing and composing orthodox chess problems, built alongside a composer
(Evgeni Bourd, IM for chess compositions) so that the analysis speaks in composing terms rather than
engine terms: set play, tries and their refutations, the key, changed and reciprocal mates, dual
avoidance and its motive, and a critique that names the flaws a judge would name.

## Two ways to use it

**In the browser** — `docs/index.html` is a self-contained page (GitHub Pages ready). Set up a position
on the board or paste a FEN, pick a stipulation, and solve. Handles `#2` and `h#2`.

**In Python** — the full toolkit, including `#3`, `s#n`, deeper analysis, the critique and the composing
searches:

```bash
pip install -r requirements.txt
python -m chesscomp.report --fen "b3r3/2pQ2p1/4n1P1/1R6/4k1P1/2K1P2R/8/4n3" "#2" --critique
python -m chesscomp.report --white "Kg1 Qd1 Sf3 e2" --black "Ke8 Rh8 f7" "#2" --json
```

```python
from chesscomp import Problem, analyse, format_report
p = Problem.from_fen("b5BQ/8/4pK1B/1N6/1p2P3/1P1krpN1/1R6/8", "#2")
print(format_report(analyse(p)))
```

## Layout

```
chesscomp/            core model, solver, analysis, motives, critique, knowledge API, CLI
chesscomp/compose/    composing searches: key candidates, post-key schemes, motif map,
                      pin geometry, self-pin and king-key searches
knowledge/            problems, themes, principles, lessons, session log, motif map,
                      and problem collections crawled from the web (see below)
tools/                crawlers/parsers for those collections
docs/                 the browser version (index.html, analysis.js, problems.json)
tests/                validation against a yacpdb export of published problems
```

## Problem collections

| File | Source | Problems | Tool |
|---|---|---|---|
| `knowledge/yacpdb/` | [YACPDB](https://www.yacpdb.org/), every `#2` (gzipped JSON lines, 6 shards) | 217,505 (187,633 orthodox) | `tools/yacpdb.py` |
| `knowledge/phenix.json` | [Phénix](https://www.phenix-echecs.fr/) magazine PDFs and award pages | 6,233 (3,612 orthodox) | `tools/phenix.py` |
| `knowledge/selivanov.json` | [selivanov.world](https://selivanov.world/) (Уральский проблемист) award and magazine PDFs | 17,632 | `tools/selivanov.py` |
| `knowledge/kotesovec.json` | [V. Kotěšovec](http://www.kotesovec.cz/) articles and PDF books | 1,217 (230 orthodox) | `tools/kotesovec.py` |

Records share one shape: `position` (English algebraic, `white + black`), `fen` (orthodox 8x8 only), `stip`,
`count`, `author`, `source`, `award`, `twins`/`conditions`, `solution`, `orthodox`, and a link back to the
source. `tools/yacpdb.py query 'Keyword("Le Grand") AND Stip("#2")'` runs any YACPDB query live.
Not crawled: the Schwalbe PDB (robots.txt disallows it) and Meson (moved to bstephen.me.uk, not reachable
from the build environment).

```python
import sys; sys.path.insert(0, 'tools')
from yacpdb import load
twomovers = list(load('knowledge/yacpdb', 'twomovers'))
```

## What the analysis reports

* **Phases** — set play (with unprovided moves), tries with refutations, the key; moves that merely allow
  the threat are grouped away.
* **Relations** — changed, transferred and reciprocal continuations between any two phases.
* **Motives** — why each defence defends and why each mate works: self-block, black interference, unguard,
  line opening, unpin, cross-check, self-pin.
* **Dual avoidance** — for each thematic variation, why each sibling mate fails, classified (the defender
  retaining its line, a line the defence opened, another unit, a king flight), with a verdict on whether
  the reasons are unified.
* **Named themes** — Bristol, Grimshaw, half-pin, Le Grand, Zagoruiko, threat reversal, Dombrovskis,
  switchback, unpinning key, White interference tries, anticipatory line closing, self-pinning king tries.
* **Critique** — key quality, king escapes in the diagram, tries refuted by king moves, shared refutations,
  duals, thin play, participation of every White unit, and whether a unit that mates in no variation is a
  cook-stopper, a set-play filler or genuinely superfluous.

## Validation

`tests/validate_yacpdb.py` runs the solver against a database export of published problems. On 459 problems
by one composer: every published key found across 120 `#2`, 34 `s#2` and 29 `#3`, and every solution found
across 37 `h#2`. Theme recognition against the database's own keywords: changed mates 38/38, reciprocal
18/18, Zagoruiko 8/8, threat reversal 7/7, Le Grand 18/18.

`knowledge/problems.json` holds every position from the composing sessions with its generated solution, so
it doubles as a regression suite: re-solve them and compare against the stored keys.

## Status

Working: `#n`, `s#n`, `h#n` analysis; the critique; the knowledge base; composing searches that verify and
filter. Not working yet: generating a good problem unaided — every unguided search in the log failed, and
what succeeded came from a composer's structural idea plus the tools doing verification and hole-closing.
`knowledge/session_log.md` records both, including the failures and why they failed.
