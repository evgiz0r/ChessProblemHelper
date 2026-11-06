<!-- Verbatim copy of chesslab/BACKLOG.md as of 9 Oct 2026 14:54 UTC (evgiz0r/Personaldashboard, branch ccr-859f3d72-q4pgb7), rebuilt from that session's transcript. Summary: ../board_views_2026-10-09.md -->

# Backlog

Ranked by expected value. Each item: the evidence, the change, and how we'd know it worked.
When you start an item, mark it `[in progress]`. When it's done, move the result to FINDINGS.md
and delete the item, or mark it `[rejected]` with the reason.

1. **Search is the bottleneck, not perception.** Evidence: perception was ~100% when subjects
   deliberated, but mate-in-2 without a hint was 1–4 of 6 (FINDINGS §2). Change: a `lab.py explore FEN MOVE`
   *delta view* that lists what changes after a move (lines opened or closed, new attacks, loose pieces,
   king flights gained or lost), plus a view or tool that walks forcing moves. Measure: mate2 suite,
   **unhinted**, current best view vs. delta view, dev then holdout.

2. **The mate2 bench is too easy and too uniform.** Evidence: when told a mate exists, 11–12 of 12 (FINDINGS §3).
   All keys were checks, so "try the checks" solves them. Change: probe variants that don't say a mate
   exists, and a generator filter for **quiet keys** (no check or capture; needs search over more
   candidates, or composed or seeded positions). Measure: the spread between views should widen.

3. **Composition bench.** Evidence: 5 composers, 3 sound first try (annotated, lines, free), 2 cooked
   (grid, named relations), both by missed White forcing moves; one verifier-feedback round fixed both
   (FINDINGS §4). This was n=1 per method. Change: a `compose` command that writes composer prompts per method and
   collects and verifies results. Measure: first-try soundness, repair rounds and threat duals, over 4+ per method.

4. **The bench can't compare views fairly yet.** Evidence: FINDINGS 2026-10-09 lab run. New views scored
   perfectly only on probes they leak; `discovered_checks` was empty in all 12 positions; `mate2` in glance was
   always "none". Change: (a) probes no view leaks, for example *consequence* probes ("after move X, which enemy
   pieces become loose or which lines open", "is capture X still good after the best recapture") and positions
   balanced so each probe is non-empty in about half of them (extend `make_set` balancing beyond one probe);
   (b) drop `mate2` from glance prompts, or score it only in deliberate mode. Measure: probes where views differ
   by more than 1 item, and no view at a free 100%.

5. **Slow ground truth.** Generating a geometry or mate2 set took ~40s per set (pure-Python mate-in-2 search).
   Change: checks-first move ordering, early exits, a reusable transposition cache; optionally Stockfish if
   it can be installed. Measure: wall time of `bench make mate2 12 3` while giving identical keys.

6. **Classifier cut-offs on long deliberate prompts.** 3 of 4 cut-offs happened with the ~20k-character
   lines/relations prompts. Change: default `--split` for long views; record the cut-off rate per view/mode
   in results. Find which content triggers it.

7. **"Glance" mode isn't thought-free.** Subjects still used 55–75k tokens. Change: record token usage
   and duration per subject (the transcripts or task notifications carry it) and log it with
   results as a cost metric. Explore a tighter glance proxy.

8. **Mate-in-3 and other genres** (selfmate, helpmate) in `verify.py`, so composition can go beyond mate in 2.

9. **Enforce `LEAKS` with a test** (more urgent now: the 2026-10-09 lab run found an unlisted leak, annotated→pins, by hand) that renders each view on bench positions and checks whether a probe's
   gold answer appears verbatim in the view text.
