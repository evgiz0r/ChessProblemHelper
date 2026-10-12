# Blind judging experiment 12: WCCT 11, section A (#2), all entries (scored)

Source: wfcc.ch (WCCT 11 section A entries book + report with scores, downloaded 12 Oct 2026). An extractor agent built
86 FENs (keys verified; 80 scored, 6 excluded by the tourney); scores, ranks, countries sealed in /tmp/claude-0/sealed/wcct11a_key.json.
Eight blind `judge` agents (11 entries each) got FEN, the entry's published solution and the set theme:

> Theme: In a try (or tries) and the key a white unit (including a
> pawn) vacates a square which is then occupied in the variation play or in the refutation by at
> least two black units. The white thematic unit may be the same or there may be different
> white units in try (tries) and key. White’s mates may result from the occupation itself or
> from some other self-weakening by Black.

## Frozen ranking (committed before unsealing)
Merged by score; ties by each judge's own order. Groups were judged by different agents, so the scales differ a little.
```
K02 K17 K61 K70 K81 K01 K20 K25 K37 K54 K33 K56 K77 K85 K06 K14 K63 K69 K39 K18 K45 K27 K36 K80 K32 K35 K65 K72 K29 K59 K74 K76 K09 K38 K48 K53 K79 K04 K13 K82 K28 K34 K62 K67 K49 K03 K21 K55 K84 K07 K24 K42 K58 K11 K30 K64 K68 K73 K75 K22 K52 K05 K19 K40 K46 K31 K44 K51 K66 K08 K71 K41 K78 K83 K12 K86 K15 K23 K10 K26 K43 K50 K16 K57 K47 K60
```

## Scores by group (judge's order)
```
g0 K02 9|K01 8.5|K06 8|K09 6.5|K04 6|K03 5|K07 5|K11 5|K05 4.5|K08 4|K10 3
g1 K17 9|K20 8.5|K14 8|K18 7.5|K13 6|K21 5|K22 4.5|K19 4|K12 3|K15 3|K16 2.5
g2 K25 8|K33 8|K27 7|K32 7|K29 7|K28 6|K24 5|K30 5|K31 4|K23 3|K26 3
g3 K37 8|K39 7.5|K36 7|K35 7|K38 6.5|K34 6|K42 5|K40 4|K44 4|K41 3.5|K43 3
g4 K54 8|K45 7|K48 6|K53 6|K49 5|K55 5|K52 4.5|K46 4|K51 4|K50 2.5|K47 2
g5 K61 9|K56 8|K63 8|K65 7|K59 7|K62 6|K58 5|K64 5|K66 4|K57 2|K60 2
g6 K70 9|K77 8|K69 8|K72 7|K74 7|K76 7|K67 6|K68 5|K73 5|K75 5|K71 4
g7 K81 9|K85 8|K80 7|K79 6|K82 6|K84 5|K78 3|K83 3|K86 3
```

## Judges' notes (condensed)
- g0: K02 9 (d5 vacated, three occupiers refute three tries, white correction 4 phases; heavy 9+14); K01 8.5 (Zagoruiko 3x2,
  reciprocal change Sc5?/key, flight-giving key); K06 8 (theme on two squares, reciprocal change Qxc5/Qd5); K03/K07 5
  (bishop-vacates tasks, five/four occupiers, static); K11 5 (cycle of refutations but double threat everywhere).
- g1: K17 9 (Zagoruiko 4x2 on Se4/Be4, eight mates, 16 units); K20 8.5 (three occupiers of e4 refute three tries, changes);
  K14 8 (Zagoruiko 3x2); K18 7.5 (theme doubled through promotions, pseudo Le Grand).
- g2: K25 8 (knight wheel, B/R/P on d5 each refute a try, cycle, Laitinen, Umnov; flight in diagram); K33 8 (Grimshaw on vacated
  c4 in three phases, Zagoruiko 3x2); K27 7 (four occupiers of e6, static); K29 7 (six phases, capturing key).
- g3: K37 8 (Qd5/Sd5/Bd5 refute three knight tries, partial changes); K39 7.5 (four occupiers of e3, static); K36 7 (four
  checking battery tries each refuted by a different interposition on c5: task; checking capturing key); K35 7.
- g4: K54 8 (d5 triad, cycle of refutations, 8 of 9 mates differ, no double threat); K45 7 (same triad, 4x3 Zagoruiko, double
  threat in every phase); K48 6 (4x2 Zagoruiko, capturing key); K53 6 (white knight correction 3x2).
- g5: K61 9 (white correction, four occupiers of d5 refute random/corrections, Sd5 mated four ways); K56 8 (Grimshaw on vacated
  c3 + white correction + Mäkihovi, duals in one try); K63 8 (Zagoruiko 4x2 + cycle of defences/refutations); K65 7 (same scheme).
- g6: K70 9 (rook vacates b3: Sc5/Qd1/Rb7 refute three tries, Sb3 and Qb3 each mated three ways); K77 8 (four occupiers of e4,
  each try cuts a white line, static task); K69 8 (bishop white correction, three occupiers on d4).
- g7: K81 9; K85 8; K80 7 (see g7.md in the run directory).
