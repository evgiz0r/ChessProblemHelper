---
name: stop-cooks
description: Remedy table for cooks, duals, double threats and holes reported by the solver on a #2 - one unit per fix, the way a composer does it. Use the moment a solve reports a second key, a dual or a hole.
---

# Stop a cook or a dual

Rule one: give Black a resource that lives only in the cook's line; do not weaken White (that breaks
the mates). Rule two: if the resource also refutes the intended key, INVERT - the intended key becomes
the try and the other move the key (1.Sc7? Sc4!, 1.Qh5! in 3rN2b/7b/8/n1Q5/1R1Pk1P1/4P3/4K3/8).

| What the solve says | Why it works | Remedy |
|---|---|---|
| Second key, same threat, same piece (Qf3 and Qxe2) | the piece reaches the threat from two squares | a Black capture on the unwanted square (Bh1: 1.Qf3? Bxf3!) - it becomes a try |
| Mate in one by a check | the king is boxed and the checker is protected | leave the hole the intended mate fills, or box with units that cannot reach a protected adjacent square |
| Discovered check cook (1.d5+) | pinner on the rank + White pawn on the pin square + queen nearby | a Black unit that blocks the discovered line (a knight to c4) |
| Queen in a corner cooks along a long line | three lines from one square | block each line with a unit that has another job (the White king on the rank, a knight that also mates, a Black knight that also interposes) |
| Dual after a side defence (1...Sf2 2.Qxf2/Qe3) | two mates share the weakened square | a Black pawn guarding the dual square (g3) |
| Thematic dual by a protector along a parallel line (Qd5#/Rxe7#) | the protector's second line is open | move the protector back so its second line is closed (Rd7 -> d8) |
| Promotion cook (1.fxe8=S) | the pawn was only a blocker | remove the pawn, block with a piece that cannot promote |
| Double threat (Qe3#/Sd6#) | the key square also covers a square the front piece protects | make the second square Black-guarded, or unreachable from the key square |
| Hole after a king move | the box misses a square only the mate covers | cover it in the diagram with a unit that cannot check |
| Waiting-move cook in a set+solution block | every Black move has a set mate | leave one Black tempo move unprovided (the key's threat then answers it) |
| Bishop self-block duals on a knight's mating squares | both knight mates stay legal | change the pinned piece's colour (a light bishop cannot reach d6/f6), or occupy the squares with immobile Black units the knight captures |

Always: one change, one solve, then re-read the whole report; a fix that stops one cook often opens
another line. Test removals in pairs before declaring a unit superfluous.
