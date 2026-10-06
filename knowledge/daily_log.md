# Daily problem log

One entry per daily run, newest last: theme, result, time per stage, what wasted time, what was missing,
what the next run should try. "Proposals" collects improvements too big for one run; the mentor decides.

## 2026-10-06, No. 1 (seed): Dombrovskis paradox
- Result: published the one-variation Dombrovskis composed on 29 September (6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1).
  Gate: PASS with warnings (thin play, try-only knight, tempo pawn), all named in the post.
- Built this day: the blog generator and gate (`tools/blog.py`), the theme rotation (`blog/themes.json`),
  the daily-problem skill, this log. The gate caught Slesarenko & Gvozdjak 1999 as an anticipation in a test.
- Next run: theme "Black correction" (least recently used). The adjacent-knight rules in
  `.claude/skills/themes/references/black_correction.md` are the place to start.

## Proposals
- A detector for Grimshaw and Novotny in `chesscomp/analysis.py`, so those themes can be claimed only when
  the solver sees them (today only a Grimshaw on the key phase is reported).
- A theme reference for Grimshaw, Novotny, Le Grand and Rudenko (none yet).
