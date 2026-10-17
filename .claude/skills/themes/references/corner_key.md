# Corner key (Bristol clearance)

Setting: claude-bristol-corner (Q1K5/1B6/8/8/5p1p/R1n5/4NN1k/8): 1.Bh1! (2.Qg2#) Sd5/Se4 2.Rh3#,
h3 2.Sg4#, f3 2.Qb8#. Kernel Q7/KB6/6N1/8/8/8/7k/8 shows the whole logic in 5 units: the bishop must
vacate every square the queen passes and keep protecting g2 from the line's end (1.Ba6? Kg1!).
Every interposition on the cleared diagonal also cuts the queen's protection of the corner square, so
mates after interpositions must protect h1 themselves (a knight on f2), x-ray it (a rook on the h-file)
or be the pawn line-opening the interposer cannot undo.
A corner queen has three long lines: block each with a unit that already has a job.
Rejected first version: three white knights (promoted piece). The rook on a3 did both of the third
knight's jobs.

## Line selection into the corner (daily No. 12, 17 Oct 2026)
The archive's rich corner keys are line selections, not Bristols: the piece must leave its square and keep its line,
and every other square of the line has its own error, refuted by its own defence (Pachl, Schach-Echo 1989-90,
psis-0eeec2b852, 1.Bh8! after 1.Bg3? Bb5!, 1.Bh2? Rb5!, 1.Bf6? Sc5!, 1.Bg7? Se5!; Chepizhny, diagrammes 2000,
psis-e4848d1a74, 1.Ba1!; Ahues, Die Schwalbe 1998, psis-4fd8d2cf88, 1.Qa8!: each queen post cut by the knight d4).
Write the error table first: for each square of the line, the White line it shuts, the black cut it allows behind
it (the corner is the far end, so only the squares beyond the cut fail), the capture it allows.
Setting: claude-daily12-corner-selection, 8/8/K2p4/8/N2k1P1p/1P3B1R/2P4R/3Nb3, 1.Bh1! (2.Rd3#) Bg3 2.Rd2#;
1.Bg2? Bg3! (g2 shuts Rh2), 1.Bc6? d5! (cut behind d5); 1.Bd5?/Be4? hang to the king. Light: one variation, set.
For one refutation per try the defender needs one way to do it: a knight f1 interposed on g3 and e3 (two
refutations of 1.Bg2?), a bishop e1 only on g3.
A queen in the corner guards the edge file from far away: every sound queen-to-h1 search hit took a flight (h2/h3).
Search: `chesscomp.compose.evolve` with KEY=<corner move> TRIES=2; by hand, `chesscomp.compose.trytable FEN <square>`.
