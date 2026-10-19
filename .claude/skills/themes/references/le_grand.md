# Le Grand

Try 1.T? threatens 2.A# and after a defence d 2.B# mates; the key 1.K! threatens 2.B# and after the same d 2.A#
mates. The solver reports it under Patterns ("Le Grand: d [try T vs key K]"); claim it only when it does. Pseudo
Le Grand: the two mates swap between threat and variation, but after different defences.

## Engines read from the archive (knowledge/studies.md 1, 2, 12; psis-7323fac2ab)
1. **Flight, cross-geometry** (E. Bourd psis-e2307f56cb, Z. Labai psis-bdd8420216). King X, flight Y. Mate square
   M1 touches X and is two squares from Y on a line; M2 touches Y and is two from X. Queen mates on M1/M2. The try
   makes both mates distant ones (its unit takes the one square the distant mate leaves); the key makes both contact
   ones (its unit protects M1 and M2 at once: a bishop on the diagonal through both, a knight forking both).
2. **Battery discharges that both hit the flight** (E. Bourd, Problemesis 2005, psis-7323fac2ab): Bb3/Sc4 v Kd5,
   flight e4; Sd2 and Sd6 both attack e4, so either discharge mates on e4 by the knight's own check. Which one is
   the threat is decided by the guards of the far squares: 1.Rdd3? (2.Sd2#) Ke4 2.Sd6#, 1.Qc8! (2.Sd6#) Ke4 2.Sd2#.
3. **Black plug at the crossing of two Black lines, capture keys** (Sredba 2003-05 1st HM, psis-f819ecb779): each key
   removes one line piece; the plug shields the other's mating square, and a random plug move unshields it.
   No flight needed; the captures are thematic because which line goes decides the threat.

## The flight problem
Le Grand by flight needs the flight in both phases. The constitution makes an unprovided diagram flight fatal
(the gate: 'king escape in diagram', major when a flight has no set mate); a provided one is minor. So either:
- the flight has a set mate, ideally a third mate C (set C, try B, key A: Le Grand plus a change), or
- one White unit guards the flight and both the try and the key are its moves (flight-giving try and key), or
- the defence is a Black piece move, not a king move (engine 3).

## Search
`python -m chesscomp.compose.legrand JOB OUT` (env CORE, SEED, BUDGET_S, DEFK, FLIGHT, SAME, NPAIR) hill-climbs with a
python-chess scorer (a few ms a position; evolve with PATTERN='Le Grand' managed one a second and found nothing in
40 job-minutes). A HIT has the swap, a unique key, a refuted try and no unprovided flight; solve it with the solver and
the gate before believing it.
