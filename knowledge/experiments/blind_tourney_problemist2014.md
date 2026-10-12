# Blind judging experiment 6: The Problemist #2 informal tourney (field from yacpdb)

E. Bourd, 12 Oct 2026: "any other better higher quality tournaments? like strong JT, or problemist/variantim/die-schwalbe/WCCI".
Reachable: yacpdb.org (query interface), selivanov.world. PDB needs a login; wfcc.ch, schwalbe.org, theproblemist.org and
variantim.org are blocked by this environment's network policy.

Field: yacpdb query `Stip("^#2$") AND Source("The Problemist") AND PublishedAfter("2014-01-01") AND NOT
PublishedAfter("2015-01-01")`, without twins/options; one entry with a fairy piece dropped. 63 problems. The date filter
let in 2015 problems dated by year only (35 from 2014, 28 from 2015), so the comparison is made per year against each
award. yacpdb is probably incomplete for unplaced problems. Shuffled (seed 2014) into T01-T63; sealed data
/tmp/claude-0/sealed/yac/. Eight blind `judge` agents (FEN only), then the 8 problems flagged for multiple threats were
judged again with the authors' theme keywords (English Novotny, Fleck, Brogi...), as a real judge reads the author's
solution. Placing about a third (21).

## Field
```
T01: 8/8/1pN2q2/2Pk1Pp1/BP2R3/3PKNp1/8/7Q
T02: 1KB2N2/5pp1/8/2P1kp2/2P1NR1P/2P1B2P/2b3Pb/n3R3
T03: 8/2Q5/8/3K4/8/pP2BBp1/PpPbPpP1/1RNkNR2
T04: 8/5p1r/2K2BB1/p1N4R/2k4P/PR1pP1p1/3r4/1n6
T05: 5K2/R3np2/r1p1Bkp1/4p1R1/1pQ3pP/2n1Nb2/1B2p3/8
T06: B2N2b1/2n5/2R5/1p1k1p2/8/PK3Pb1/1BPP4/Q7
T07: 6K1/b7/P5R1/k1p5/1R6/P1Qb4/3N4/3q4
T08: 1R3N2/3Nk1pq/2p2p2/K1p3p1/2B1p1P1/6Q1/8/8
T09: 1bQ5/3Np2K/5N2/1R1rnkp1/qB4p1/1B4P1/b7/4R3
T10: K7/2pQ3p/R4nkP/3p3p/3P1B2/1B2p3/3r2b1/6R1
T11: N5n1/n1pB2P1/7R/2qkBp2/3pNQ2/1Ppp3b/7K/8
T12: 8/5p1K/2p1b2p/b3B3/1NB4N/nR1pkP2/rR1p2Qp/1q3n1r
T13: 8/3p2K1/4k2N/b1Q2p2/1pP2P2/7n/2r1r1b1/1B6
T14: 1K6/5pp1/2NR1pN1/R6n/1p2k1p1/4P1rr/6bb/B4Q1B
T15: R1B5/1N6/1B1Ppp2/R2qkPp1/2p1P2P/5P2/bb1Q2P1/4K3
T16: 8/7p/BK1N1p1q/2Pp2bR/1ppkN3/1R2pp2/1Pp4B/4Qr2
T17: 5R2/1q3N2/6n1/3bB1P1/r5p1/1Q1B1kP1/4RP2/b6K
T18: K5Q1/8/pP2R3/qk1B4/b3R3/1Pp5/8/8
T19: 4r2b/p1p2pn1/2K1p1p1/1n3P1r/R2pk2P/2pNNbPB/2P2Q2/8
T20: Q5b1/6Bk/5K2/3R2p1/1pp2p2/1r6/1pq2p2/1B6
T21: 8/8/4pQnK/1pP5/1B1pBP2/RNP1kP2/7R/4n2N
T22: 1Q3KB1/4p1N1/1p3p1r/q1p2p2/Rppkp3/3P3b/1PP1R3/3N4
T23: 1n2Q3/2Bq2Nr/2p1p2b/8/rR1PkN2/pR4np/K1P5/1B6
T24: 8/1P1K4/1R1np3/1p1Bkp1N/3p1R2/bQ3p2/1n1Nb3/B7
T25: 8/n1p5/K1Pp4/p2P2p1/kN3pR1/pR6/PpN1B3/1n6
T26: 8/1bPN1K2/R1p2PP1/1P1k2N1/nQ4pR/1P4p1/1rp4q/BB6
T27: 8/7R/6p1/7p/2K5/1B5k/8/6Q1
T28: 3Q4/3p4/8/8/3n2p1/3K4/3B4/3k4
T29: B7/1q3Q1b/r1R5/nN6/1N2kB1r/4pp1p/8/1K6
T30: 3N4/3P1p2/kB2pR2/p7/p1KPp3/P1PpP3/1R6/5B2
T31: 2bRQn1B/4p2n/2Np1P1p/4Nkb1/6R1/1B1p1P1K/8/8
T32: 8/1p6/pB1Kp3/2p2b2/2Nk1N2/1n1P3r/1P3P2/4R3
T33: 8/8/6Q1/KbNBp3/6P1/p3pP1r/pp2k3/rn1R1R2
T34: 3R4/8/4Nb2/3np2R/Bp2k3/3pNr2/1K1BP3/8
T35: 8/1K6/5pN1/4P2p/5nkP/1Q2R1Pp/4N3/1B5n
T36: 8/3n3p/2p1Q1p1/4p3/R1n1k3/1Nrr1pK1/2N2B2/1B6
T37: 8/Q2B1R2/1rpkpn2/3p4/N4P1K/4r2p/1B6/8
T38: 2n2K2/3p1P2/p1pN3R/4k1B1/1RB2NP1/1P6/8/bb1Q2n1
T39: 2k5/2Pp1B2/1K3R2/8/4b3/8/8/8
T40: 1qB1R1K1/7n/1p1p4/b2k1N2/1pRrN3/3P4/3Q2n1/8
T41: Kb6/p3r2B/R1N3q1/p7/3p1N2/1p6/1Pk1P3/R1B2Q1b
T42: 8/qp1r3b/3N3R/1P1kP1N1/p2ppP2/8/1b4Q1/1KR2BB1
T43: 3B2nK/8/pp3p2/N4R2/NkP3PQ/p4n2/1b1p4/1R1B4
T44: b2R1Q2/2p3B1/4R3/1rNqN2K/1ppkp3/5P2/3P4/8
T45: 1Q6/3N2R1/r1k3p1/3p4/5P1P/7R/2r1p1N1/3bK2B
T46: 4Q3/1b2b2K/2np3B/1R1P1N2/p2NkPp1/3r4/3PPn2/1B6
T47: 4r3/1R3bR1/Q1pPkN2/1p3NP1/5PP1/3p4/K3p3/8
T48: 8/4r3/3b4/2p1kpP1/3NB3/1PR3NP/1B2K2Q/4R3
T49: 5Q2/8/2K2N2/8/3p4/3k4/1R1P4/3R4
T50: 1r6/2b2p1q/n1N5/1Q1B1r2/p1KPP1P1/p1P1P1pP/k4NR1/B6R
T51: 5N2/3N3n/3BPpR1/2pp1k2/1p3ppP/P2K3p/3Q1P1r/1Bb3n1
T52: 2nN1B2/p1pR4/2Rqprp1/1p6/3k2P1/PB1Pp1Q1/2K1P3/8
T53: 6BB/KPP3rN/2P4b/4kpnb/4pR1n/8/3Q4/8
T54: 1B2B3/5b2/5p2/1Q3P1r/R1pP2k1/5NN1/K5P1/8
T55: B5r1/3pPR2/1b2pKp1/p3N3/Rq3krP/3P4/2Q3n1/5N2
T56: 8/8/2B2n2/p2p3r/Nk3q1R/4N1B1/PP6/R3K3
T57: n3N1rQ/4Bpbr/2PPk3/Rb1R2P1/3p4/K4B2/8/8
T58: 2Bn4/6B1/3P4/n3Np2/4k3/b2R2P1/4K3/8
T59: 8/1b6/2B2N2/p2p3p/R7/R1Kp1k1n/1PPPNn2/5Q2
T60: 5B2/1Rrb4/n7/4pp2/1p1krpN1/1B6/3K4/1N1R3Q
T61: n4b2/2p2pp1/2PPkP2/1N5N/2P1K1P1/3R1R2/4P3/3r1r2
T62: 8/1N2p3/2P1Pn2/B1R2K2/2pkB1QR/1Pp1p3/3n2Np/6b1
T63: 4r2R/b3R2b/4q3/8/2N3P1/p1N2PP1/Q3P1K1/1n2k3
```

## Judges' reports (condensed)
T01 1: double threat battery, static (check keywords).
T02 1.5: thin, superfluous pawns.
T03 3: queen sac, two mirrored battery mates, pawn cage.
T04 6.5 HM: rook tries Rf5?/Re5?/Rd5? each a white self-interference refuted by the defence whose mate it cuts, key Rg5!; mixed defences, escape key.
T05 7 Prize: three black interpositions on d5 each opening a white line, bishop tries Bd7?/Bf5?/Bxg4? each refuted by its matching d5 defence (3x3 self-interference); 20 units, capture try.
T06 6 Comm: Kb4! into two cross-checks, doubled reversal of white moves (Qa2?/Kb4!; Qh1?/f4?), changed mate; plugs, second pair bolted on.
T07 4.5: Qb3! sac allowing check, one change, 7+5.
T08 2.5: Sdxf6! capture key.
Order: 05 > 04 > 06 > 07 > 03 > 08 > 02 > 01.

T09 3: Sh5!, one change, diagram flight, escape key.
T10 3: Qxd5?/Bxd5! changed threat + one change, both capture.
T11 5 Comm: bishop tries Bxd4?/Bf6?/Bxc7!, three mates on Qe7 over phases, every refutation different; capture key, Pg7 only blocks duplicate tries.
T12 4.5: Sxd3!, threefold change on Qe1, half pseudo Le Grand; captures, 23 units.
T13 5.5 HM: Sxf5!, try threats return as key mates, two black rooks to d2 with different mates, 6+9 airy; capture key.
T14 6 HM: Sce5!, Dombrovskis on Rxe3 + pseudo Le Grand, changed threats over phases; diagram flight e3, two king refutations.
T15 2: static capture key.
T16 3: Sc3! flight-giving, one change, 22 units.
Order: 14 > 13 > 11 > 12 > 09 > 10 > 16 > 15.

T17 6 Comm: Bb2?/Bd4! 2x2 change on Qxf7/Bxf7 self-pins, battery mates; escape key, plug.
T18 7 HM/Prize-: three queen phases Qf8?/Qg1?/Qg5!, three threats by one battery, doubled Dombrovskis, refutations return as variations; 7+5; diagram flight c5.
T19 5: Sg4! flight-giving, three self-blocks on f5, cross-check; 24 units, repeated refutations.
T20 2: Rd3! double threat (check keywords), unpins bQ.
T21 7.5 Prize: white first/second moves swapped in three pairs (Sxd4?/c4?, cxd4!/Sd2?, cxd4!/Sc1?) + four mates on Sg2 over phases; thematic capture key, plug, thin post-key.
T22 4: threat reversal Rd2!/dxc4?, old-style mass.
T23 4: one defence Qxd4 mated three ways over phases, switchback; capture key and try.
T24 6.5 Comm/HM: three bishop tries each with a white error refuted by the matching black c4 move (one-square triple), line strategy; capture key.
Order: 21 > 18 > 24 > 17 > 19 > 22 > 23 > 20.

T25 1: waiting key, block kept.
T26 2: Se4!, three changes, heavy mixed; Pg6 possibly superfluous.
T27 2: miniature, king-refuted tries.
T28 3: queen tries vs knight refutations (partial wheel), dual after Sb3.
T29 1: Bc7! double threat (check keywords).
T30 0.5: tempo key in pawn forest.
T31 6 HM: Sc4! flight-giving, three phases, pseudo Le Grand Sf7?/key on Sg6/Se6, changes set->key and try->key.
T32 4.5 Comm: Sd2!, Dombrovskis Se5?/key on Rxd3, knight tries on one scheme.
Order: 31 > 32 > 28 > 27 > 26 > 25 > 29 > 30.

T40 6.5 Prize-/HM: Qc2!, one black rook's three captures refute three queen tries, three changed mates; capture refutations, 17 units.
T35 6 HM: doubled reversal of White's 1st/2nd moves + threat reversals, Sd3 mated five ways over five phases; escape key, capture tries, try-only Pe5.
T33 5 Comm: Se4! incomplete block -> mutate, three changes set->key, threat-pair knight tries; clumsy corner.
T37 4.5: mirror bishop sacrifices, pseudo Le Grand; symmetric, captures.
T39 4: miniature, one change.
T36 3.5: Scd4! unpins bS, two mates.
T38 3: sac line-opening key, shared refutation.
T34 2.5: edge bishop key, no change.
Order: 40 > 35 > 33 > 37 > 39 > 36 > 38 > 34.

T41 0.5: triple threat, one check variation (check keywords).
T42 6.5 Prize-: Sdxe4!, three phases with reciprocal refutations (Sgxe4?/Se6?/key), two changed mates (partial 3x2 Zagoruiko), line clearance for Rh6; capture key.
T43 5.5 HM-: Qxf6! from edge (capture), pseudo Le Grand Qg3?/key, threat/mate interchange over three queen phases.
T44 5 Comm: Qf5! flight-giving, two changed mates vs Rc6?, one real try.
T48 4.5: royal battery cross-checks, bishop line selection; diagram flights.
T46 4: Se6! flight + unpin, thin pseudo Le Grand, rude tries.
T45 3: edge rook key, set lost.
T47 2: static key.
Order: 42 > 43 > 44 > 48 > 46 > 45 > 47 > 41.

T49 4.5: miniature, flight-giving Sg4!, one change, king-only play.
T50 5.5 Comm: royal battery Kc4/Bd5, three king-capture mates, two changes from set; key interferes thematically; 24 units, capture tries.
T51 4: royal battery four king mates, escape key, capture tries.
T52 6.5 HM: Rc5! sac flight-giving, two changed mates from one cause, unified dual avoidance.
T53 2: c8=Q double threat (check keywords), knight correction.
T54 3.5: Qb1! completes block, all set.
T55 2: d4! triple threat (check keywords), royal battery.
T56 4: castling key 0-0-0, light.
Order: 52 > 50 > 49 > 51 > 56 > 54 > 53 > 55.

T62 6.5 HM: Se1!, both bS capture on pinned e4; 2x2 change vs try Sf4?, queen tries' threats = Sf4-phase mates and try moves = key mates (threat/mate interchange); plugs, crude e2 refutation.
T61 5.5 Comm: double royal battery, bR checks, pseudo Le Grand Rde3?/Rfe3!, changed mates on checks; near-symmetric, escape key.
T60 4.5: royal battery cross-checks, scattered changes.
T57 3.5: single pseudo Le Grand pair, Sf6?/Bf6!.
T59 3: Rh4!, thin, shared refutation.
T63 1: double threat (check transcription).
T58 0.5: triple threat, no defences (check transcription).
Order: 62 > 61 > 60 > 57 > 59 > 63 > 58.

Re-judged with author keywords (multiple threats as theme):
T20 6 HM: English Novotny on d3 + self-unpin by interference; cxd3 separates nothing, escape key.
T58 5.5 HM-: Fleck singles + Brogi cycle of double mates, three Sx tries refuted thematically, 7+5; Pd6 superfluous (verified), null moves.
T63 4.5 Comm: English Novotny try e4?/key e3! with changed threat partner; four plugs.
T55 4.5 Comm: Novotny + Fleck + Brogi + king battery; incomplete, cluttered.
T29 4: half Fleck, escape key.
T01 3.5: cycle of threat pairs only in tries; solution unseparated.
T41 3: Novotny separates 2 of 3 threats, heavy.
T53 3: promotion swap c8/b8, threats never separated.

## Our ranking (blind; frozen before the awards are read)
1. T21  (placed)
2. T18  (placed)
3. T05  (placed)
4. T04  (placed)
5. T42  (placed)
6. T40  (placed)
7. T52  (placed)
8. T62  (placed)
9. T24  (placed)
10. T20  (placed)
11. T35  (placed)
12. T14  (placed)
13. T31  (placed)
14. T17  (placed)
15. T06  (placed)
16. T13  (placed)
17. T58  (placed)
18. T43  (placed)
19. T61  (placed)
20. T50  (placed)
21. T44  (placed)
22. T11
23. T33
24. T19
25. T32
26. T49
27. T63
28. T37
29. T55
30. T07
31. T12
32. T60
33. T48
34. T39
35. T29
36. T56
37. T22
38. T23
39. T46
40. T51
41. T57
42. T36
43. T54
44. T01
45. T03
46. T28
47. T16
48. T09
49. T10
50. T38
51. T59
52. T45
53. T41
54. T53
55. T08
56. T34
57. T27
58. T26
59. T15
60. T47
61. T02
62. T25
63. T30
