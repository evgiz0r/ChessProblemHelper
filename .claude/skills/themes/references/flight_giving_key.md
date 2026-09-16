# Flight-giving key with two flights

Reference problem: `claude-two-flight-knight-sacrifice`, 2R2B1b/8/4P1bN/2Nkp3/p4p2/2Q5/3K4/8 #2 (7+6),
session 25, on a scheme by E. Bourd (bK d5, bP e5, wS c5: "Se4 will give two flights").

1.Se4! (2.Qc4#) 1...Kxe6 2.Qc6#, 1...Kxe4 2.Qd3#. Tries 1.Sd7? / 1.Sa6? (same flights, same mates) 1...Bd3!

## What has to be true

1. **Each flight needs a mate that is not the threat.** After the flight the threat must fail on its
   own: Qc4 fails after Kxe6 because d7 is uncovered, after Kxe4 because f3 is uncovered. Cover d7 or f3
   and the flight just "allows the threat".
2. **Two mates from one queen differ by their x-rays.** Against Ke4, Qc4 (rank) x-rays f4 and needs e3,
   f3, f5; Qd3 (diagonal) x-rays f5 and needs f4 and protection. So cover f4 (bPf4 occupies it) and leave
   f3 open. A rook on the third rank or a knight on e1 covers f3 and merges the two.
3. **The key's departure and arrival must both work.** Departure: unmask the c-file (Qc4 threat, Qc6
   mate, Rc8's protection of c4 that makes Qc4 a mate only after the key). Arrival: close the g6-d3
   diagonal so ...Bd3 no longer refutes. Every other knight move unmasks the file too; only e4 closes
   the line, which is what makes Sd7?/Sa6? tries and Se4 the key.
4. **A king flight can be a self-interference.** After 1...Kxe4 the king stands on its own bishop's
   line to d3, and Qd3 mates. The same line, closed by the knight, is the reason the threat works.
5. **The other arrival squares of the key piece.** Se6 also covered d4, so Qc6 became a second threat and
   Kxe6 ran into the same Qc6#. No refutation exists for that; the square was occupied by a white pawn
   that the knight protected and the key abandons - the cook-stopper is the second flight.

## Cooks met and their one-unit remedies

| Cook | Cause | Remedy |
|---|---|---|
| Qb3+ Kd4 Qd3# / Rd8# | c4 empty, d3 protected, c5 protected by the rook | bPa4 (axb3) |
| Rd1+/Rd2+/Rd3+ Bd3 Qxd3# | any f-file rook reaches the d-file with check | no rook; Sh6 covers f5 and f7 |
| Rf6 (2.Rd6#) | the f-file rook again | same |
| Sg8/Sg4 (2.Sf6#) with a knight on h6 | f6 unguarded | bBh8 guards f6 and protects e5 |
| Sd7 (2.Qxe5#) | e5 unprotected | bBh8 |
| Sg4 (2.Se3#) | e3 unguarded | bPf4 (also occupies f4, so no g3 pawn) |
| Se6 (2.Qc6#/Qc4#) | e6 covers d4; Kxe6 meets the same mate as the main line | wPe6, captured by the flight |

## Shape of the abstract search that failed

bK e4 with a bishop or queen on the a7-g1 diagonal guarding d4 and e3, key leaving the diagonal, up to
three added units around it: about 10M positions, no hit. The mates after the two flights need the
vacated square covered by the mating move itself (rank or diagonal x-ray) and that fixes the queen's
mating squares before any unit is placed; the search cannot discover that, a scheme with the key move
named gives it for free.
