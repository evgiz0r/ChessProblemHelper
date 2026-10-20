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

## 2026-10-10, No. 5: Self-blocks (simpler form)
- Result: 3r1r2/4p3/5pR1/3PkNBp/2R4P/5B1Q/4n2K/8 (9+7), 1.Sg7! (2.Qe6#) Rd6 2.Qf5#, Sd4 2.Qg3#, Sf4 2.Bxf4#, Kd6 2.Qe6#;
  tries 1.Sh6?/Se3?/Sxe7? Rxd5!, 1.Sd6? Rxd6!. Gate: PASS with warnings (attacked key piece, same refutation, dual-avoidance
  reasons, cook-stopper Ph4), all named in the post. Only Rd6 is a functional self-block; the post says so and asks the mentor.
  Mentor issues #4 and #5 had no answers yet; nothing to act on.
- Setup: local `main` had diverged again (the stale 54-commit history); worked on `daily-run` from origin/main, pushed HEAD:main.
- Minutes: setup and reading 5, mentor 1, study 5, kit change (SELFBLOCK mode) 10, searches and hand work 55, post and records 15.
  About 120 solves, 20 search jobs (8 evolve, 6 postsearch, brute force, one-unit searches).
- What wasted time: bare-core evolve once more (checking keys only); a brute force of complete blocks (all with White mates in one);
  `pkill -f` / `pgrep -f ... | xargs kill` twice killed my own shell (exit 144), because the pattern was in the command line.
  Kill by PID from `ps -eo pid,comm,args | awk '$2 ~ /^python/ && /name/'`.
- What was missing: a one-unit add/remove search around a nearly sound diagram that keeps a named key and named mates (written in
  the scratchpad as one.py; it found the key 1.Sg7 by removing a knight). Worth adding to the kit as `compose.oneunit`.
- Next run: theme from `next-theme` (Grimshaw has no reference: write one first). For self-blocks proper, start from a block or
  a battery and use SELFBLOCK=3 on a seeded sketch; the guard-of-the-threat-square idea gives self-block-shaped moves, not self-blocks.

## 2026-10-11, No. 6: Grimshaw
- Result: 3Q1bb1/2N3r1/1N3Rpp/1pP1k3/3p4/3P4/5K2/8 (7+8), 1.Rf3! (2.Qf6#) Re7 2.Qd6#, Be7 2.Sd7#, Rf7 2.Qd5#; try 1.Qxf8? Re7!
  Gate: PASS with warnings (king refutes the unprinted try 1.Rf4?, duals after six non-defences, 'bPh6 not needed', which is
  false: without h6 the key threatens 2.Qg5# too), all named in the post. The set play already holds the Grimshaw with the
  same mates. No open mentor issues (2-6 all closed and acted on).
- Setup: the local `main` had diverged again (the stale 54-commit history); worked on `daily-run` from origin/main, pushed HEAD:main.
  The playwright Python package was missing (installed requirements before switching branches): `pip install playwright`.
- Minutes: setup and reading 5, mentor 1, study 3, evolve 5 (wasted), hand and postsearch work 20, post, reference and records 15.
  About 35 solves, 14 searches (7 evolve, 3 postsearch, 3 keyfind, 1 trim).
- What wasted time: three evolve seeds were illegal (a white piece already gave check) and died in 0 s; check every seed with
  python-chess before launching. Bare evolve again gave checking keys only. The first threat (check down the e-file through
  the crossing) could never work: interposition after a check is no defence.
- What helped: a 10-line post-key printer (post_spec in SAN) for one solve per change; postsearch READY=1 found the g8-bishop
  cure for the square beyond the crossing in five minutes; giving the key rook a single free square.
- Next run: theme from `next-theme`. For a Grimshaw again, aim for a changed mate between set and solution (the mentor may
  answer question 1). Fix the critique's 'black piece role' so it counts the threats (see Proposals).

## 2026-10-12, No. 7: Half-pin
- Result: b2N4/Q3K3/8/3kpp2/4n1p1/1P3r2/3P4/2R4B (7+7), 1.Qa6! (2.Qc4#) Sd6/Sxd2 2.Qd3#, Rc3 2.Qd6#, Kd4 2.Qc4#
  (flight-giving key). Gate: PASS with warnings (random-move duals, dual-avoidance reasons differ), both named in the post.
  The solver reports Half-pin on all three defences. Mentor issue #7 (No. 6) has no answer yet; nothing to act on.
- Setup: the local `main` had diverged again (the stale 54-commit history); worked on `daily-run` from origin/main.
  origin/main carried merge-conflict markers in knowledge/lessons.jsonl (from a08ad2b); removed, both sides kept.
- Minutes (container clock): setup and reading 5, mentor 1, study and kit change 10, evolve 10 (wasted), postsearch 6,
  hand work and keyfind 10, judging and post 15. About 30 solves, 16 searches (8 evolve, 4 postsearch, keyfind, trim, 2 matecheck).
- What wasted time: bare and lightly seeded evolve (eight jobs) again gave checking keys only; postsearch converged on
  one mate for all named defences; a `pgrep -f` wait loop that matched its own shell (killed by hand).
- What helped: the split by reasoning on each unit's lines (see lessons); a post-key printer (threats + every Black move's
  mates in SAN) between solves; keyfind for the flight-giving key; trim after every cure (it found a redundant Sf7).
- Next run: theme from `next-theme`. For a half-pin again, aim for two mates per unit (four variations); the knight's
  two defences here share a mate. Try `PATTERN=Half-pin DEFS= NPAT=3` evolve seeded with a post-key sketch, not a bare core.

## 2026-10-13, No. 8: Self-pin
- Result: B7/2N5/2Pp4/1P2p1B1/RK1nk2N/1PR5/2P5/1Q1n4 (12+5), 1.Rg3! (2.Rg4#) Sxc6+ 2.Ka3#, Sxc2+ 2.Ka5#, Se6/Se2 2.c3#,
  Se3 2.Rxe3#, Sf2 2.Re3#; try 1.Qxd1? Sxc2+!. Self-pin by capture with check against a royal battery; the pinned knight's
  remaining control selects the king's square. Gate: PASS with warnings (attacked key piece, same refutation d5 of two tries,
  random-move duals, Pc6 'cook-stopper' which is the captured pin blocker, 17 units), all named in the post. The thematic pair
  is already set (flaw, asked). Mentor issues #7 and #8 had no answers; nothing to act on.
- Setup: `main` fast-forwarded cleanly this time (no diverged history).
- Minutes (container clock 23:58-01:35): setup and reading 5, mentor 1, detector (kit change) 15, composing 65, judging,
  post and records 15. About 60 solves, 38 search jobs (12 evolve, 14 postsearch, 12 freethreat), 3 keyfind, 1 trim.
- What wasted time: two loaded knight batteries (checking keys only, 14 evolve jobs in total gave nothing); four postsearch
  jobs with the same RNG converged to one zugzwang; two `until pgrep -f` wait loops matched their own shells again (use a
  file test: `until grep -q evaluated OUT`); a seed with Qh1 checking the king (validate seeds with python-chess first);
  an evolve core with two light bishops (count the bishops' colours before launching).
- What helped: reasoning about what a capture gives White (only the vacated square, or a check) before searching; freethreat
  with exact mate ids once the selectors were placed by hand; postsearch READY=1 to cut White's other solutions; keyfind.
- Next run: theme from `next-theme`. For a theme whose defence is a capture, first write down what the capture gives White.
  The royal-battery selection (a pinned checker keeping the king off one square) could carry changed mates: a key by the
  white king that forms the battery would leave the set captures with other mates.

## 2026-10-14, No. 9: Underpromotion key
- Result: B2B4/2r1P3/2nppp2/N3k3/2P3Q1/8/8/2K5 (7+6), 1.e8=S! (2.Bxf6#) Rf7/Re7 2.Sxc6#, Sxd8/Se7 2.Qe4#; tries 1.e8=Q?
  (2.Qexe6#) and 1.e8=R? (2.Rxe6#) f5!, 1.e8=B? Rc8!/f5!. The first underpromotion key in the kit with a threat and
  a mobile Black. Gate: PASS with warnings (attacked key piece, same refutation, random-move duals, unprovided Rc8/f5),
  all named in the post. An independent judge subagent called it light (static key: both mates set). Mentor issues
  #7, #8, #9 had no answers; nothing to act on.
- Setup: `main` fast-forwarded cleanly.
- Minutes (container clock 23:58-00:45): setup and reading 5, kit change (evolve KEY mode) 5, evolve 15 (mostly
  wasted), hand reasoning and postsearch 10, judging, post and records 10. About 30 solves, 13 search jobs.
- What wasted time: three of four first seeds had a white unit checking the black king (validate seeds before launch,
  again); KEY-mode evolve at about one evaluation a second; a scoring bug that rated a try with many keys like a key.
- What helped: asking what only the promoted piece does from e8 (guard d6/f6/c7/g7), then postsearch on the post-key
  with the knight already on e8.
- Next run: theme from `next-theme`. To lift No. 9: changed mates (the key could make the black rook's 7th-rank moves
  matter) or one refutation per wrong promotion. A seed validator in evolve (refuse an illegal SEED with a message).

## 2026-10-15, No. 10: White correction (study post)
- Result: no sound original; study post on Loustau, Phénix 1999 2nd Prize (psis-22fa9079c1),
  4R3/3N4/1BNb1R1r/1K1k1p2/1p4q1/3P4/4r3/6Q1, 1.B~? Qxg1!, 1.Bc5? Bc7!, 1.Bd4? Bc5!, 1.Be3!, with today's two
  near-misses as diagrams (bishop d3 on the d-file: one correction and a diagram flight; knight e4 next to the king:
  cooked by knight checks). Mentor issues #7-#10 had no answers; nothing to act on.
- Setup: `main` fast-forwarded cleanly (60 commits behind, no divergence).
- Minutes (container clock 23:58-02:30): setup and reading 10, mentor 1, study 10, kit change (WCORR score, seed check,
  test) 20, evolve 40 (24 jobs), hand work 50, post and records 20. About 80 solves.
- What wasted time: four of eight first seeds had a mate in one (the new seed check reported them, at least); evolve
  never found a second correction in 16 seeded jobs; three hand geometries started without the error table; the
  `ps | awk /compose.evolve/ | xargs kill` pipe in front of pytest killed its own shell, so the tests did not run.
- What helped: a 30-line try table in python-chess (threat, refutations and mates for every move of one unit, under a
  second) for one change per solve; the knight-colour fact (a knight next to the king never checks by moving).
- Next run: theme from `next-theme`. For a white correction again, write the error table first (arrival square ->
  defence stopped, mate spoiled), on a bishop or rook line with a second White line crossing it, then WCORR evolve.

## 2026-10-16, No. 11: Bristol clearance
- Result: 4N3/4N3/Bn6/P1k5/6P1/2P3Pp/6RQ/6K1 (10+3), 1.Rd2! (2.Qf2#) Sc4 2.Rd5#, Sd5 2.Rxd5#; try 1.Rb2? Sd5! (1...Sc4
  2.Rb5#): Bristol in key and try, changed mate after 1...Sc4, the rook's file selects the mates. Gate: PASS with warnings
  (attacked key piece from h3, random knight duals Qf2/Rd5, Rxd5 captures the defender, cook-stoppers Pg3/Pg4), all named
  in the post. Light. Mentor issues #7-#11 had no answers; nothing to act on.
- Setup: the local `main` had diverged again (114 vs 65 commits); worked on `daily-run` from origin/main.
- Minutes (container clock 23:58-00:40): setup and reading 5, kit change (BRISTOL mode + tests) 10, evolve 25 (16 jobs,
  run alongside hand work), hand work with a try table 20, judging, post and records 10. About 45 solves.
- What wasted time: bare evolve seeds and seeds with a free queen (only queen keys); a pin-cut sketch where the rook on
  d2 just took over the d-file pin; a first-rank version refused by the gate (out-of-play key) after it was sound.
- What helped: boxing the queen before any search; a scratch try table (every move of one unit: threat, refutations,
  non-threat mates) for one change per solve; reading the rook's stops as files.
- Next run: theme from `next-theme`. For a Bristol again, aim for every stop of the clearing piece a try with its own
  refutation, and a box whose units also mate. The try table is worth a kit tool (see Proposals).

## 2026-10-17, No. 12: Corner key
- Result: 8/8/K2p4/8/N2k1P1p/1P3B1R/2P4R/3Nb3 (9+4), 1.Bh1! (2.Rd3#) Bg3 2.Rd2#; tries 1.Bg2? Bg3! (g2 shuts Rh2) and
  1.Bc6? d5! (cut behind d5): a line selection into the corner, every other square of the diagonal with its own error.
  Gate: PASS with warnings (static key, king-refuted 1.Bd5?/Be4?, random duals after Bf2/Bd2, thin play), all named in the
  post. Light. Mentor issues #7-#12 had no answers; nothing to act on.
- Setup: the local `main` had diverged again (origin/main was force-updated); worked on `daily-run` from origin/main.
- Minutes (container clock 23:58-01:15): setup and reading 5, kit change (TRIES mode + test) 5, searches 50 (evolve 12 jobs,
  a scratch random fill 5 jobs, a scratch hill climb 10 jobs, alongside hand work), hand composing 15, post, trytable
  tool and records 25. About 60 solves.
- What wasted time: blind searches around bare cores (no key without a diagram flight; a corner queen takes the edge
  file's flights); a scratch hill climb without a promoted-force check (three rooks, two light bishops) and with capture
  keys onto an occupied corner; a `pkill -f` that killed its own waiting shell again.
- What helped: reading the archive's corner keys first (Pachl, Chepizhny, Ahues: line selections); boxing the king
  before placing the line pieces; the try table after every one-unit change (knight f1 -> bishop e1 made the try pure).
- Next run: theme from `next-theme`. For a line selection, write the error table per square first and give each error a
  different black unit; to lift No. 12, a second variation in the key phase (1...Bf2 cannot defend 2.Rd3#, so the
  c3#/Rd2# dual avoidance needs another threat).

## 2026-10-18, No. 13: Novotny
- Result: 8/1p1Nb3/1Nr3R1/8/4k1P1/4P3/4PPK1/B7 (9+4), 1.Rd6! (2.Rd4#) Bxd6 2.Sf6#, Rxd6 2.Sc5#, Rc4 2.Re6#, Bf6 2.Sxf6#;
  set Bd6 2.Sf6#, Rd6 2.Sc5#, R~ 2.Re6#: the set Grimshaw on d6 becomes a single-threat Novotny on d6, mates transferred.
  Gate: PASS with warnings (attacked key piece, random-move duals, 1...Bf6 2.Sxf6# recaptures), all named in the post.
  Stretch theme: the full (double-threat) form is fatal for the gate, so the single-threat form was published and the
  mentor asked about the gate. Mentor issues #7-#13 had no answers; nothing to act on.
- Setup: the local `main` had diverged again (origin/main force-updated); worked on `daily-run` from origin/main.
- Minutes (container clock, which ran slow): about 60 of work. Setup and reading 5, study 10, searches 15 (8 freethreat,
  4 postsearch), keyfind and hand cleaning 15, post, tool, reference and records 15. About 40 solves.
- What wasted time: the first freethreat runs (White bishop on the crossing, threat free): the threat never needed the
  crossing unit, so the captures did not defend. `pkill -f compose.freethreat` killed its own shell again, losing a
  script written in the same command.
- What helped: writing the separation condition down before placing anything (each mating square guarded by both black
  pieces), a 40-line enumeration of it (now chesscomp.compose.novotny_geometry), then postsearch with the threat and the
  mating knight fixed (KMP=d7), keyfind, and the anatomy after every change (it showed Kg2 needed in no mate).
- Next run: theme from `next-theme`. For a Novotny again, if the mentor allows a thematic double threat, try the English
  Novotny on the same geometry (the crossing unit's two threats are the two knight mates); otherwise look for changed mates
  through Shire's departure lines, which differ between the set and the solution.

## 2026-10-19, No. 14: Le Grand (study post)
- Result: no sound original; study post on Jonsson, Springaren 1998 3rd Prize (psis-4d1711af7b), 3N4/n7/1kBP4/8/Qp6/8/n1R5/R1b4K,
  1.Sb7? (2.Qa5#) Sc3 2.Qa6# but Sxc6!, 1.Bb5? Sc3!, 1.Bb7! (2.Qa6#) Sc3 2.Qa5#: Le Grand by a line switch, no flight.
  Near-misses shown as diagrams: the hinge kernel 7K/8/Q1N2R2/4p3/4kp2/8/6N1/2BB2b1 (Le Grand between 1.Be3? Bxe3! and
  1.Be2? Bd4!, no key) and the first kernel (duals after Kd5, check cooks). Gate on the study: only the anticipation (it is
  the archive problem). Mentor issues #7-#14 had no answers; nothing to act on.
- Setup: the local `main` had diverged again (origin/main force-updated); worked on `daily-run` from origin/main.
- Minutes (container clock, which runs slow): about 45. Setup and reading 5, evolve 10 (4 jobs, nothing), legrand tool and
  test 10, legrand climbs 15 (16 runs, nothing), hand kernels with try tables and the pairs layer 15, post and records 10.
- What wasted time: two bugs in the new climb (mates compared with their departure square, so Qh5-f5 and Qf1-f5 counted as
  two threats; `if not seed.king(WHITE)` read a king on a1 as missing and added a second one, so three jobs looped without
  a line of output); then the climb itself, which drifted off every seed. Monitors waiting on `pgrep -f compose.evolve`
  matched their own command line and never ended.
- What helped: reading the archive's light Le Grands by mechanism (flight cross-geometry, battery, plug, line switch);
  writing the guard table of the queen's two mates (which squares each covers v each king square) before placing units;
  the exhaustive pairs layer (now `legrand pairs`).
- Next run: theme from `next-theme`. For Le Grand again, start from Jonsson's line switch (a black unit that opens one
  White line and closes another, no flight) in a new geometry, and enumerate the last layer with `legrand pairs`.

## 2026-10-20, No. 15: Zagoruiko (study post)
- Result: no sound original; study post on Foster, The Problemist 2003-II 3rd Prize (psis-f8c659a19d),
  7Q/2N5/1B1pp1K1/3Ppp2/3pkP2/5R2/4B3/8, tries 1.Qe8? (exf4 Qxe6#, d3 Qa4#) and 1.Qh4? (Qxf4#, Re3#), key 1.Sb5! (Qxd4#,
  Sc3#): a strict 3x2 Zagoruiko, the third phase by the knight key. Near-misses shown: the pawn shell
  4Q3/8/3ppp2/4k3/3pPp2/5B2/1B6/K7 (two clean queen phases, sixteen keys) and the search's inversion (cooked). Gate on the
  study: only the anticipation. Mentor issues #7-#15 had no answers; nothing to act on.
- Minutes (container clock, slow): about 120 of work. Setup and reading 10, study 10, searches 45 (28 jobs: posts 4, zag 24),
  MODE=zag and tests 20, hand shell with a queen-square table 20, post and records 15.
- What wasted time: posts-mode searches whose score let the same mate repeat in every phase; zag searches from bare cores
  (flat -100 score below one full phase, no gradient: fixed); two seeds with a second White king; a complete-block shell
  where every waiting move keeps the set mates.
- What helped: a scratch table of every queen square with the mates after each defence (qtable.py): it showed at once that
  the shell has two clean posts only. Then the archive: both light pawn-shell Zagoruikos take the third phase from a knight key.
- Next run: theme from `next-theme`. For a Zagoruiko again, choose the third phase's piece first (a key unit that becomes the
  mating piece), the queen far away, a threat if possible; run MODE=zag KP=any around a hand kernel, never a bare core.

## Proposals
- Merge the unmerged YACPDB crawl (branch claude/clever-knuth-kdog9b: 217,505 twomovers, plus 22,700 from
  selivanov.world) into the anticipation check of the gate; today it checks Problemesis only (7,912).
- A detector for Novotny (and a set-play Grimshaw) in `chesscomp/analysis.py` (half-pin done 12 Oct, direct self-pin 13 Oct), so those themes can be claimed only when
  the solver sees them (today only a Grimshaw and a half-pin on the key phase are reported).
- evolve: a score term for distinct mating squares among the thematic mates (CORR and DEFS modes).
- trychange MODE=zag: score two-move cooks (captures of shell pawns as threats) before the solver sees a hit.
- A theme reference for Rudenko (none yet; Grimshaw done 11 Oct, Novotny 18 Oct, Le Grand 19 Oct).
- legrand: replace the hill climb (it drifts off good seeds) by a beam over kernels, or drop it for the pairs layer.
- critique 'black piece role' (and the gate warning) calls a unit 'not needed' when the variations survive its removal, but
  ignores a new threat: bPh6 in daily No. 6 stops 2.Qg5# as a second threat. Compare the threat set too before saying 'not needed'.
- A fast pre-filter for evolve: python-chess alone (mate-in-one tables, early exit at the second refutation) ran about
  ten times faster than the solver in daily No. 12's scratch hill.py; score with it, confirm hits with the solver.
- evolve: FLIGHT=1, a score for a flight-giving key in the diagram (no flight before, given flight mated, two more
  distinct mates); the scratch scorer of 9 October is the model.
- compose.oneunit: every single-unit addition or removal around a diagram, kept when one named key and the named mates
  survive (the scratch one.py of 10 October found 1.Sg7 in daily No. 5).
- critique: a 'set-only unit' tag (not needed for soundness, every guard in the solution mates duplicated), once the
  mentor says how much it weighs (No. 3, question 1).

## Data note (7 October 2026)
Problemesis records psis-0c3747b09e (Caillaud, Microweb 2000) and psis-cb0ecb6471 (Poisson, Lacny-50) do not
solve to their published solutions: the source pages carry diagram errors (in Caillaud's, Ta8 checks Ka6).
28 of 102 Lacny/reciprocal #2 records fail the same check; a cleaning pass should flag records whose unique
key differs from the published one before they are used as study material.
