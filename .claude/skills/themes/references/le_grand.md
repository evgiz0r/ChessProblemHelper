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
4. **Jonsson's line switch** (Springaren 1998, 3rd Prize, psis-4d1711af7b, daily No. 14 study): 3N4/n7/1kBP4/8/Qp6/8/n1R5/R1b4K.
   One black knight a2 stands on Ra1's file; 1...Sc3 opens it (Ra1 then protects a5 and a6) and closes Rc2's file (c5,
   c6 lose their guard). 1.Sb7? (2.Qa5#) Sc3 2.Qa6#, 1.Bb7! (2.Qa6#) Sc3 2.Qa5#: in each phase the unit that left
   c6/d8 decides which of c5/c6 the closed file still matters for. Try 1.Bb5? Sc3! (Dombrovskis). No flight at all.

## The flight problem
Le Grand by flight needs the flight in both phases. The constitution makes an unprovided diagram flight fatal
(the gate: 'king escape in diagram', major when a flight has no set mate); a provided one is minor. So either:
- the flight has a set mate, ideally a third mate C (set C, try B, key A: Le Grand plus a change), or
- one White unit guards the flight and both the try and the key are its moves (flight-giving try and key), or
- the defence is a Black piece move, not a king move (engine 3).

## What failed on 19 Oct 2026 (daily No. 14)
- The cross-geometry by hand with a hinge: Ke4, flight d5, Qa6 mating on c4 (distant from e4) or d3 (contact), and a
  black bishop g1 that interposes on d4 against both distant checks (Qc4+ on the rank, Qd3+ v Kd5 on the file). A White
  unit landing on e3 cuts the hinge, so 1.Be3? (2.Qc4#) Kd5 2.Qd3#, and 1.Be2? (2.Qd3#) Kd5 2.Qc4#: a Le Grand between
  two tries (7K/8/Q1N2R2/4p3/4kp2/8/6N1/2BB2b1), but no key. The hinge refutes both: 1...Bxe3! takes the interferer and
  still reaches d4, and 1...Bd4! self-blocks in advance and closes the d-file, which carried the guard of the flight.
  Rule: a black line piece used as an interposer can always occupy the interposition square in advance; if that square
  lies on a guard line of the threat mate, the hinge refutes it. And an interferer on the hinge's line can be captured
  from the hinge's own square, after which it still interposes. Check both before building around a hinge.
- A flight engine always has one square that only the try (or the key) supplies, and that square is a diagram flight
  unless a set mate provides it. Decide which before placing guards.

## Search
`python -m chesscomp.compose.legrand JOB OUT` (env CORE, SEED, BUDGET_S, DEFK, FLIGHT, SAME, NPAIR) hill-climbs with a
python-chess scorer (a few ms a position; evolve with PATTERN='Le Grand' managed one a second and found nothing in
40 job-minutes). The climb itself drifted away from good seeds in every run (16 job-runs of 12-20 minutes, no HIT).
What worked is the exhaustive layer around a hand kernel: `python -m chesscomp.compose.legrand pairs KERNEL b|bb|bw`
(every one or two added units, about 100 s for a black+white pair). A HIT has the swap, a unique key, a refuted try
and no unprovided flight; solve it with the solver and the gate before believing it.
