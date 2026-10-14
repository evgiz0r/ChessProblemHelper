# Ablation 1: solver only against the full repository (13 Oct 2026)

Question (E. Bourd): how much better does this repository compose than a session starting from scratch?
Same task to two headless sessions (same model, 18 minutes, 70 tool calls, 20-minute watchdog):
"compose an original #2 showing a Grimshaw, as good as you can". A first run was void (headless default model
was a smaller one; arm B stopped after 2 minutes).

| arm | tools | turns | result |
|---|---|---|---|
| A | solver + plain report only (no critique, knowledge, skills) | 71 | 2br4/5B2/8/4k1P1/1B1N4/1Q2PPK1/8/8, 1.Qd3! sound but triple threat (gate FAIL); Grimshaw on d7 in the set play only |
| B | the whole repository | 32 | nothing sound; best 2b1r3/8/8/8/1P1k1P1R/1P2p1N1/4P3/K3B2Q, try 1.Rh6? (2.Rd6#) Re6 Sf5#, Be6 Qe4#, but 1...Re5!, cooks 1.Qc6, 1.Kb2 |

Reading: the repository raised the ambition (a Grimshaw on the threat line in the solution) and the self-judgement
(B knew it had nothing; A called a fatal triple threat "serious"), not the output in 18 minutes. B spent its time
reading and on three 270 s postsearch runs; A made 63 quick hand solves. B never called anatomy.
Gap found: `report --critique` does not flag a double threat; only `tools/blog.py check` does.
One theme, one run each: not a measurement yet. Next: 45-60 minutes per arm, two or three themes.

# Ablation 2: "2 black bishops unpin a black knight" (theme by E. Bourd, 13-14 Oct 2026)

Two sessions per arm, 50 minutes each (55-minute watchdog), 200 tool calls, four in parallel on 4 cores. The critique
now flags the double threat. A blind `judge` agent scored them in shuffled order (P1-P4):

| blind | arm | FEN | gate | judge |
|---|---|---|---|---|
| P3 | B1 repo | 3N4/3b1R2/1n1p4/QN1nk1K1/R2bp3/4p3/8/6B1 | PASS | 1st, 6/10: unmasking key 1.Sc3! (Qa5 pins Sd5), Bb5 Rf5#, Bc5 Rxe4# (unpin + line opening), tries Sc7/Sa7/Sa3 all fail to Bc5 |
| P1 | B2 repo | 4b1R1/4b3/7N/3nk3/R3N1B1/2P2K2/8/2B5 | PASS | 2nd, 4/10: 1.Ra5! pins, Bb5 Sf7#, Bc5 Rg5#, set mates, no tries |
| P2 | A1 solver | 4b3/6nK/8/5n1k/8/4b1Q1/R5N1/8 | FAIL (out-of-play key) | 3rd, 3.5/10: richest play, 4+5, three unpins, Bg5 Qf3# self-block; key Ra2-a5 obvious |
| P4 | A2 solver | 8/7K/7B/4bB2/1R2n2k/2n1N1N1/5R1P/5b2 | PASS | 4th, 2/10: pin already set, 1.Kg6 unrelated to the theme, a plug (stopped at 39 min) |

Reading: the repository arms placed 1st and 2nd. B1's extra layer (unmasking key, tries) came from the tools
(`unmask_search`, `trypair`, `freethreat`); both B arms called `anatomy` (5 and 7 times) once CLAUDE.md asked it.
The solver-only arm found the richest raw play (A1) but did not know the house rule that sank its key; the judge
applies our rules, so part of the gap is the rules themselves. All four found the same basic scheme (the unpin is the
reason of the defence, the mate exploits the bishop's lost guard); none used the freed knight. n=2 per arm.
