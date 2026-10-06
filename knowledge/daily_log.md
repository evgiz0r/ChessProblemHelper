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

- How the run starts (found by four test runs): a routine created by a session cannot attach a repository,
  so a routine session can clone the public repository but cannot push, use the issues API, or run pytest
  (not installed). A session created with the repository as its source and `main` as its outcome branch
  can do all of it. So the nightly routine (02:57 Asia/Jerusalem) wakes the setup session, which starts the
  daily session that way with `blog/routine_prompt.md` as its prompt.

## Proposals
- Merge the unmerged YACPDB crawl (branch claude/clever-knuth-kdog9b: 217,505 twomovers, plus 22,700 from
  selivanov.world) into the anticipation check of the gate; today it checks Problemesis only (7,912).
- A detector for Grimshaw and Novotny in `chesscomp/analysis.py`, so those themes can be claimed only when
  the solver sees them (today only a Grimshaw on the key phase is reported).
- A theme reference for Grimshaw, Novotny, Le Grand and Rudenko (none yet).
