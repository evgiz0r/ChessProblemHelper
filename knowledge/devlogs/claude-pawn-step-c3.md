# Development log: claude-pawn-step-c3 (session of 11 Oct 2026)

Task (E. Bourd): "compose a simple problem, the key is a white pawn single step", then review the process.
Final: `4N2K/6n1/8/4kP1R/2Q5/8/2P2n2/1B6` (7+3). 1.c3! (2.Qd4#) Se6 2.fxe6#, Sxf5 2.Rxf5#, Se4 2.Qxe4#.
Wall clock: about 25 minutes from the request to the gate; solver and searches under 2 minutes of it.

| # | Stage | Position | Card | Change | Solver verdict | Decision |
|---|-------|----------|------|--------|----------------|----------|
| 0 | Idea on paper | - | - | Pawn single step needs a reason: open a line, give a flight, or guard a square. Chose: bBb1 behind wPc2, king e5; 1.c3 opens b1-h7 (e4, f5) and guards d4. Planned threat 2.Qe4#; planned try 1.c4? (double step guards d5 instead of d4) | - | build it |
| 1 | Kernel 1 | `4N3/8/8/4kP2/2Q3P1/8/2P5/1B5K` | pawnstep-k1 | box: Se8 (d6, f6), Pf5 (e6), Pg4 (protects f5), Qc4 (d4, e4, f4, d5, e6) | no solution: every White move stalemates or frees a square | Black needs a unit whose moves defend |
| 2 | Kernel 2 | `4N3/8/8/4kP2/2Q3P1/8/2P2n2/1B5K` | - | + bSf2 (Sd3 cuts b1-e4, Se4 blocks, Sxg4 unguards f5) | illegal: Sf2 checks Kh1 | move the king |
| 3 | Kernel 2b | `4N2K/8/8/4kP2/2Q3P1/8/2P2n2/1B6` | pawnstep-k2 | Kh1 -> h8 | **sound**, 1.c3! unique. Threat is Qd4# (not Qe4#: Sf2 guards e4); 1...Se4 2.Qxe4# uses the opened diagonal. Thin: one defence | kernel found; the plan's threat was wrong, the solver's is better (pawn c3 guards d4 = threat, opened line = mate after Se4) |
| 4 | Defenders | kernel_search 1 Black + 1 White, key c2c3 fixed | - | 39k positions, 74 hits, 44 s | best: A bBb4+wRc8 (Bc5 Rxc5, Bxc3 Rc5, Se4 Qxe4); B bSc7+wRf6 (Se6 Rxe6, Sb5 Re6, Se4); C bSg7+wRh5 (Se6 fxe6, Sxf5 Rxf5, Se4 Qxe4); many with wPd3 (rejected: d3 blocks the bishop, the key opens nothing) | A and B mate on one square twice; C has three different mates and a battery Rh5/Pf5 -> take C |
| 5 | Candidate C | `4N2K/6n1/8/4kP1R/2Q3P1/8/2P2n2/1B6` | pawnstep-c | + bSg7, wRh5 | sound; critique: wPg4 is set-play only (big flaw); random duals after Sxg4 | remove g4: Rh5 already protects f5 in the diagram, Bb1 after the key |
| 6 | Final | `4N2K/6n1/8/4kP1R/2Q5/8/2P2n2/1B6` | pawnstep-c3 | - Pg4 | sound, 7+3, three different mates; Sxf5 Rxf5# is new after the key (the opened diagonal protects f5) | gate PASS, trim: nothing removable |

## Dead ends and lost ideas
- The double-step try 1.c4? never existed: the queen stands on c4 (seen only at judging time; the idea at
  step 0 did not survive the queen's post chosen at step 1).
- Plan's threat Qe4# -> real threat Qd4#. The hand plan was wrong in a useful way.

## Open questions for the mentor
- Random moves of Sf2 (Sg4, Sh3, Sh1, Sd1) unguard e4 and allow Qe4# as well as Qd4#: acceptable?
- Is the key's double job (guard d4 + open b1-e4 for two mates) enough content for a simple problem?
- Worth hunting the 1.c4? try (queen off c4, e.g. on the 4th rank behind c4 so the double step closes her road)?
