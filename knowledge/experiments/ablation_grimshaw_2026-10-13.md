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
