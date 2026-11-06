<!-- Verbatim copy of chesslab/FINDINGS.md as of 9 Oct 2026 14:54 UTC (evgiz0r/Personaldashboard, branch ccr-859f3d72-q4pgb7), rebuilt from that session's transcript. Summary: ../board_views_2026-10-09.md -->

# Findings

Blind subjects are subagents of the same model. Each gets one prompt file and no tools,
and is scored against python-chess. Sample sizes are small. Treat differences of 1–2 items as noise.

## 2026-10-09: first session (scripts predate lab.py; position sets differ from bench/keys)

### §1 Perception with deliberation: format barely matters
16 random positions × 5 views, 6 probes each. Mean F1: FEN 0.976, grid 0.988, grid+list 0.990,
lines 0.979, relations 0.993. All 11 misses were **omissions** (missed checks or mates), never hallucinations.
The prediction "FEN hurts" was **wrong**: with room to deliberate, subjects rebuild the board from any format.

### §2 Harder geometry, glance vs. deliberate
12 positions with 22+ pieces. Probes: pins, x-ray lines, discovered checks, profitable captures, mate in 2 (6 positions had one).

| perception mean | FEN | grid+list | lines | relations |
|---|---|---|---|---|
| glance | 0.95 | 0.97 | 0.97 | 1.00 |
| deliberate | 1.00 | 1.00 | (cut off) | 1.00 |

Mate in 2 found, deliberate: FEN 1/6, grid+list 4/6, relations 2/6. In glance mode, 0/6 everywhere.
FEN glance misses were long-range: an h-file capture, a long-diagonal x-ray, one phantom x-ray.
**Deliberation erases perception errors. Search is the bottleneck.**
Caveats: glance subjects still used 55–75k tokens. 3 deliberate runs were cut off by a safety classifier
(lines ×2, relations ×1), counted as missing.

### §3 Can a view carry search? (mate 2, subjects told a mate exists)
12 mate-in-2 positions. Solved: grid+list 11, relations 12, kingzone 11, tree1 (1-ply replies) 12.
- **Knowing a mate exists** raised the solve rate from ~2/6 to ~12/12. Confound: different positions. All keys were checks.
- tree1 cut the time per batch about 4x (~50s vs. 90–245s) at equal accuracy.
- The only error was the same missed defence twice (M08: 1.Qf3+? e4!, a pawn interposing on the check line).
  The views that listed replies or full relations avoided it.

### §4 Composition: mate in 2 with a double-check threat, 5 visualization methods, n=1 each
| method | first try | after 1 verifier-feedback round |
|---|---|---|
| annotated pieces | sound (unique threat; interpositions beaten only by the double check) | |
| lines | sound (some duals) | |
| free choice | sound (4-piece miniature, threat duals) | |
| grid | cooked by 1.Nxb8 | sound |
| named relations | cooked by 1.Nd7+/1.Ng6+ | sound, no duals at all |

- Both failures were **missed White forcing moves** (a capture; knight checks), not misread geometry.
- One round of exact verifier output fixed both. **A verifier in the loop matters more than the view.**
- Hint (n=1): methods that force listing every line of sight (annotated, lines) were sound first try.
  The methods that failed (grid, named relations) only show the relations you choose to look at.
- All verified problems are in `bench/problems/library.json`.

### Process notes
- python-chess's wheel doesn't build on this image; `lab/boot.py` vendors the sdist.
- Subjects must be audited: every run so far was clean (one Read, then the answer).

## 2026-10-09: first run through lab.py (geometry-s2, glance, n=12, all subjects clean)

| probe | grid_list | relations | annotated | salient |
|---|---|---|---|---|
| pins | 0.92 | 0.92 | 1.00 (leak) | 1.00 (leak) |
| xray_lines | 0.96 | 0.98 | 1.00 (leak) | 1.00 (leak) |
| profitable_captures | 0.83 | 1.00 (leak) | 1.00 (leak) | 1.00 |
| discovered_checks | 1.00 | 1.00 | 1.00 | 1.00 |
| mate2 | 0/6 | 0/6 | 0/6 | 0/6 |

- **Not evidence that the new views are better.** Their perfect scores are on probes they give away.
  The `LEAKS` table had missed that `annotated` reveals pins (an x-ray through an enemy piece to the king); fixed.
- **The bench failed to discriminate.** `discovered_checks` was empty in all 12 positions, and `mate2` in glance mode
  was answered "none" by everyone. Both are uninformative as built (see BACKLOG).
- **Signal:** in G07 and G11 the mating key was a capture. Every subject listed it as a profitable capture, but
  none saw it as mate in 2. They saw the move and missed its consequence, the same search gap as §2–§3.
- On the probes no view leaks, grid_list misses were long-range (h2 pin along the h-file, two x-rays through g7/h7) plus
  two missed captures. That's the same pattern as the 2026-10-09 FEN misses, but n is small.
