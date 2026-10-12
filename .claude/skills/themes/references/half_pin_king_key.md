# Half-pin, pawn half-battery, White-king key

Half-pin (yacpdb 2753 and the session-2 settings): a mate that captures the pinned unit, or merely needs
the half-pinner as a guard, does not use the pin. Only defences by the half-pinned units are thematic.
Order: a clean dual-avoidance scheme first, then tries. Content is measured per PIECE: each half-pinned
unit should provoke its own mate.
Pawn half-battery: impossible on a diagonal (the rear pawn guards a square on the pin line); on a file
the pawns cannot advance so the defences are captures of units essential to the threat; on a rank they
can advance and the mate may capture the advanced pawn.
White-king key: the king stands on a White line and blocks it; every king move opens it, so the choice
of destination is free; tries are destinations that close another White line. Evgeni's order: lines and
possible king moves, then simple mates, then extend so the defences themselves open White lines
(b5BQ/8/4pK1B/1N6/1p2P3/1P1krpN). A third interfering line earns a try only if its square is not guarded
by another unit already. Searches for it failed (150k positions): with little Black material every try
dies to a king flight.

## Black half-pin in a #2 (daily No. 7, 12 Oct 2026)
Mechanism: a White line piece, two Black units, the Black king on one line. Each unit's defence leaves the
other pinned, and the mate is one the pinned unit would otherwise stop (capture the mating piece, interpose,
or land on its square). List, for each unit, the squares it covers and the lines it could block: those are the
mating squares and check lines the OTHER unit's defences make available.
Reference: Barnes, StrateGems 2002, 1st Prize (psis-25e8021eff) 7b/8/1K1p2Q1/3N4/1Nknr2R/P6R/2rp4/B7, Rh4
half-pins Re4 and Sd4: 1.Qf7! (2.Se3#) Re6 2.Qc7# (Sd4 pinned), Se6 2.Qf1# (Re4 pinned).
Detector: the solver's Patterns list prints `Half-pin: <defence> [key]` for each defence whose mate uses the
pin of the other unit (`motives.detect_half_pin`); claim the theme only when it does. Evolve can aim at it
with `PATTERN=Half-pin DEFS= NPAT=3`.
Archive: `python -m chesscomp.db list --stip '#2' --orthodox --text half-pin` (13 records, 7-14 White units).
