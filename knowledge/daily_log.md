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

## 2026-10-07, No. 2: Black correction (bishop)
- Result: 3R4/8/6K1/4P3/3bk3/N1p3Q1/8/8 (5+3), 1.Sc4! B~ Qg4#, Bxe5 Qe3#, Be3 Qxe3#. Gate: PASS with warnings
  (same refutation of the two tries; dual-avoidance reasons differ), all named in the post. Mentor issue #2 had
  no answer yet; nothing to act on.
- Minutes: setup and reading 10, mentor 2, study 5, kit change (evolve CORR mode) 15, search and hand work 40,
  gate/judge/post 15. The container restarted once mid-run; work in the tree survived.
- What wasted time: `pkill -f compose.evolve` kills the shell that runs it (its own command line matches), so
  two batches of searches never started; launch them from a script file and stop them by PID. Twenty minutes of
  blank-core searches (king + piece + queen) found correction sets but no key. Hand boxing gave mates in one.
- What was missing: a way to say "mates on different squares" in the score (both corrections here mate on e3).
- Next run: theme "Changed mates". Seed evolve with a hand sketch from the start; for corrections try
  `CORR` with a second-correction mate on another square (a score term for distinct mating squares).

## 2026-10-08, No. 3: Changed mates
- Result: 2R5/3n1p2/1B6/1K1kP1Q1/1P4B1/4rP2/8/8 (8+4). Set 1...Sxe5 2.Rd8#, 1...Rxe5 2.Qd2#; 1.Qe7! (2.Qd6#)
  Sxe5 2.Qc5#, Rxe5 2.Qxd7#. Gate: PASS with warnings (same refutation of two unprinted tries; dual-avoidance
  reasons differ), both named in the post. Mentor issues #2 and #3 were already acted on and closed.
- Minutes: setup and reading 5, mentor 1, study 3, kit change (KEYROLE in evolve) 8, searches and hand work 15,
  post and records 15. About 30 solves, 8 search jobs.
- What wasted time: four bare-core evolve runs (15 minutes) again found nothing; the reference's seeded core worked at
  once. The search's hits all carried a unit that served only the set mate (Rg8); the critique counts a unit with
  duplicated guards as taking part in a mate, so it does not flag the knight/rook that exists only for the set play.
- What was missing: a critique tag for a "set-only unit" (not needed for soundness, every solution guard duplicated);
  waiting on the mentor's answer (question 1) before making it a flaw or a fatal flaw.
- Next run: theme from `next-theme`. Always seed evolve with a theme core from the reference; never start bare.
  For changed mates, try a try phase with a third pair on the same two captures (TRYCHANGE=1 with the No. 3 core).

## 2026-10-09, No. 4: Flight-giving key (study post)
- Result: no sound original within the composing budget, so the skill's fallback: a study post of J. M. Rice,
  Jubilé A. Casa-70, The Problemist 2002-03, 6th Prize (R7/4N3/4p3/1k1nR3/3B3Q/1PP5/8/5K2, 1.Bc5!, an unpinning
  and flight-giving interference), with full credit. Gate: FAIL by design (anticipation of itself: it is an archive
  problem); no other fatal flaw. Mentor issue #4 had no answer yet; nothing to act on.
- Setup: the local `main` had diverged from origin (54 commits of an old history). Pull --ff-only refused; the run worked
  on a branch from origin/main and pushed HEAD:main. The routine prompt now says so.
- Minutes: setup and reading 15, mentor 1, study 5, kit change (critique) 10, composing about 110 (18 search jobs,
  about 60 hand solves), post and records 20.
- What wasted time: bare-core evolve again (15 minutes, four jobs); one seeded core was illegal (a knight checking the
  king) and died at once; `pkill -f` once more matched the shell that ran it (exit 144). Postsearch produces post-key
  positions with the flight mated in minutes, but they carry few defences (its score has no term for them) and
  keyfind found no key for any of them.
- What was missing: a search mode that scores the DIAGRAM for the theme directly (no flight before, a quiet unique key,
  the given flight mated, at least two other distinct mates). A scratch version (scratchpad, not committed) found the
  best idea of the day (1.Bd4 self-interference) within 15 minutes of being seeded. Worth adding to evolve as FLIGHT=1.
- Next run: theme from `next-theme`. For a flight-giving key, decide the flight's mate first (the mating move must cover
  the vacated square), then a threat, then the box. The Bd4 matrix (2R5/8/5K2/1N1kp3/R7/2B1p1P1/4P3/8) needs only a
  cure for its complete block: a threat or one tempo move left unanswered in the set.

## Proposals
- Merge the unmerged YACPDB crawl (branch claude/clever-knuth-kdog9b: 217,505 twomovers, plus 22,700 from
  selivanov.world) into the anticipation check of the gate; today it checks Problemesis only (7,912).
- A detector for Grimshaw and Novotny in `chesscomp/analysis.py`, so those themes can be claimed only when
  the solver sees them (today only a Grimshaw on the key phase is reported).
- evolve: a score term for distinct mating squares among the thematic mates (CORR and DEFS modes).
- A theme reference for Grimshaw, Novotny, Le Grand and Rudenko (none yet).
- evolve: FLIGHT=1, a score for a flight-giving key in the diagram (no flight before, given flight mated, two more
  distinct mates); the scratch scorer of 9 October is the model.
- critique: a 'set-only unit' tag (not needed for soundness, every guard in the solution mates duplicated), once the
  mentor says how much it weighs (No. 3, question 1).

## Data note (7 October 2026)
Problemesis records psis-0c3747b09e (Caillaud, Microweb 2000) and psis-cb0ecb6471 (Poisson, Lacny-50) do not
solve to their published solutions: the source pages carry diagram errors (in Caillaud's, Ta8 checks Ka6).
28 of 102 Lacny/reciprocal #2 records fail the same check; a cleaning pass should flag records whose unique
key differs from the published one before they are used as study material.
