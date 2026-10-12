# Blind judging experiment 8: The Problemist 2010 #2 informal tourney (yacpdb, with solutions)

E. Bourd, 12 Oct 2026: "go next". Built with `python tools/blind_tourney.py build "The Problemist" 2010 --tourney "The Problemist"
--label W --size 7`: 49 problems, 18 with a distinction (sealed in /tmp/claude-0/sealed/yac/P10). Judges got FEN, published
solution and author keywords; checklist with the StrateGems softening (weigh rude moves, do not filter). Seven blind `judge`
agents; none recognised a problem. Placing about a third (16).

## Field
```
W01: 3n2B1/2r5/r3p3/1Np4R/p1p1k1p1/2pp1pP1/Kb3P2/3QN3
W02: 5R2/8/2p2NKB/1p3BNP/1Q1b1kP1/5Ppb/3P2p1/r2nn1q1
W03: 4q3/1p1rBn2/3bPN2/2p1R1p1/2n2k2/2PP1Npb/4B3/2K3Q1
W04: 2R5/1B6/3pN3/B7/2PP4/pkNrr1b1/p3Q1q1/K1Rb4
W05: 2N2KB1/nr2PR1N/1Pp1RP1r/1p1k3p/1P2p3/2Bn1b1Q/6P1/8
W06: 1b6/8/3P2B1/3k4/1PRPR3/2K2nN1/8/1bB4Q
W07: 6K1/4N3/2R2p1B/p2pk3/Rb6/1QpP4/b1N3P1/8
W08: 5n2/4B2n/2R1Nrb1/r2pkN2/p2p1R2/4pQ2/8/7K
W09: 2BB2R1/8/Q1N4p/1K1PN2p/R3pk2/3P1p2/3Pq3/b6n
W10: 3q4/1b5Q/R2pN2B/3k1B2/2pP2N1/2rn4/1r1R4/3n1K2
W11: 8/3B1Kp1/1Pp2P2/1PpNBRr1/r1p1kq2/2QNp3/2P4b/5R2
W12: 1BB5/5q2/7p/2RP4/4k1P1/2PN3N/3QPb2/3K3n
W13: 6R1/p1p2N1B/2Q1rr1p/1p3n2/N2p1P2/bPPkP3/4Rn2/B3K3
W14: 2QqBB2/2PPP3/3kp1b1/nP3r2/K2PP3/8/8/8
W15: 1b2r3/1K2p1R1/ppp2Bn1/3N1k2/r5p1/1B1PQP1P/4b3/5N2
W16: 7B/3p4/1Kp1P2Q/1p1BRP2/3k2N1/N1p1p2R/2Pq4/5r2
W17: 6r1/p5B1/4P3/K1Q2p2/2BP1Np1/bPkP1b1q/R3Pn2/1n1R3r
W18: 4Q3/1K2NN1B/3p1P2/3pbPP1/3nkpR1/5p2/5P2/3R4
W19: K7/3k4/4NQR1/7B/8/8/8/8
W20: 3R3b/1r2Q3/2p1PB2/n1P1N1R1/2pPkpP1/3p1p2/BP3p2/3K1N2
W21: 6Q1/1N6/n1pN4/1p2pP1p/pR4nP/p1Pk2p1/PP1B2P1/3BK3
W22: 5r2/1pp2bN1/n1pP1P2/2pkP1Pr/3PpBQ1/1N5p/8/2R4K
W23: nQ6/N4N2/3p4/Pnk5/b1BR4/Pp3P2/1K3R2/6B1
W24: 4K2k/PP1PN1b1/4p1P1/4BP2/1r4R1/2n5/3r1R2/q3Q3
W25: 4BK2/ppp5/1k5P/5Q1R/8/R7/4Nr2/5qB1
W26: 3R4/4p1K1/3B4/2Pp2Q1/RN1kp3/Npr2p2/P1b5/3r2b1
W27: N3k3/2Q3K1/2b5/8/R7/8/8/8
W28: 1B5n/r1n4K/2P1pRp1/3bkBP1/1P2N3/1p5N/3Q2p1/b7
W29: 4R3/1q6/1b1P4/2P1PpP1/3Nkr2/3R4/B3P2B/Kn1N4
W30: 4R3/3N1pK1/2pQNpp1/2p2k1b/6rq/3pBPbP/8/8
W31: 2K5/2p1P3/2P1p3/P1k1N3/2P1Rb2/6p1/8/3QBBq1
W32: n2NN1K1/1Q4p1/2prR3/3k2r1/1Ppppn2/8/2B3qB/8
W33: 8/3np3/4P1PB/1Kp1P2R/1pPNkNB1/p4ppP/2PP4/Q4n1b
W34: 1B1R4/5QpK/4p3/3PP1p1/3NkN2/2P3Rn/3Pbq2/8
W35: 5Q2/p7/1Np2pr1/2PP1N1b/8/k1P2R2/Pp4r1/1K2B3
W36: B7/KRN5/Q3NB2/2pnp1R1/1P2k3/7r/4PP1b/2r5
W37: 3N4/2B1nB2/4p3/3bPkbK/4N1R1/3p1P1P/3Pq3/4RQ1n
W38: r2R4/1NPnN2P/1p2R1B1/1QPPP3/r1nk4/p7/Kb1B4/8
W39: B3Qn2/3p2R1/N1pN2p1/pPPk4/1prn1r2/2pRKp2/8/8
W40: 8/K7/Np6/1k6/8/1n6/R1Q5/8
W41: R3K3/5B2/4N3/1P2q3/P2N3p/3pP3/k1P2P1R/2Q3B1
W42: 3RNq2/2N5/4p3/3pkPPQ/2p1Pp1B/2P5/7K/1B6
W43: 5BK1/1B1P4/Q1NNp3/1npk2p1/Rq6/1nP2P2/1P6/8
W44: B7/1R6/2R3K1/3Np3/3rkNp1/3ppp2/3pP3/3Q4
W45: 1b1R4/4Q3/2r2B2/p1RPN3/3k4/2nNpP2/4P2K/8
W46: 8/pN1Bp3/k3n3/BRP5/4r3/4Q3/p7/K3R1b1
W47: 2B5/2N5/4Rp2/r1p2p2/1PkP4/R1B4r/1pQnb1Np/2b4K
W48: 5K2/4p1R1/4kN2/2PR4/8/8/8/8
W49: 3Q4/1pp2pNK/rp1r1p2/1pPBN2R/b2kP3/2R2P1p/2nPP3/7q
```

## Judges' reports (condensed)
W01 6.5 Comm: Se1 knight tries with threat correction (Sg2?/Sc2?/Sxd3?/Sxf3!), refutations answered across phases; capture key/try, 21 units.
W02 4: single king Le Grand, diagram flight, heavy.
W03 3.5: sac flight key, e5 trio spoiled by a dual.
W04 7 HM: Salazar (Bd5?/Rb8?/Bc6!) + Dombrovskis + Vladimirov-type; escape key, rude Rxc3.
W05 2.5: mixed changes, double-threat try, heavy.
W06 3.5: Rudenko-type separation, thin, unprovided flight.
W07 7.5 Prize: doubled Dombrovskis (g4?/Kf7?/Sd4!) with changed mates, set mates transferred, sac flight-giving key, 16 units.
Order: 07 > 04 > 01 > 02 > 03 = 06 > 05.

W08 4: three white captures on d4 with own threats, pseudo Le Grand; all first moves capture, thin.
W09 6.5 HM: Sc6 white correction (random/Sb4?/Se7!), flight-giving key; random tries refuted by king, few changes.
W10 5 Comm: Bh6 fan of line-clearing tries with distinct refutations, Bf8! cuts bQ; one change, edge key.
W11 7 Prize-: four phases, threat reversal + pseudo Erokhin + Dombrovskis effect + transferred/changed mates + flight exchange; capture key, diagram flight, heavy.
W12 5 Comm-: set/key reciprocal change on two queen defences, pin motive; light, familiar.
W13 5.5 Comm: pseudo Le Grand e4?/Rg3! + caprice try, several changes; overloaded, edge key.
W14 3.5: mirror promotion echo; multiple threat, promotion duals.
Order: 11 > 09 > 13 > 10 > 12 > 08 > 14.

W15 6.5 Comm: carousel over set/Sb4?/Sc7! on Rf4/Bf4/exf6 + Grimshaw f4; set duals, escape key.
W16 8 Prize: Zagoruiko 3x2 (set/Rhxe3?/Sxe3!) with three white captures on e3 (Stocchi type); capture try and key thematic.
W17 7.5 HM: cycle of three threats on d5 over three phases, pseudo Le Grand; repeated check, unthematic refutation, 23 units.
W18 8.5 Prize: Se7 white correction with secondary and tertiary threat correction, earlier threats return as mates after Sxd5!, flight-giving; capture key, plugs.
W19 3.5: aristocrat Y-flight miniature, flights.
W20 6.5: Se5 tertiary white correction, threats return; heavy, three variations.
W21 7 HM/Comm: Sd6 white correction ending in zugzwang key Sc4!, set->key changes, flight-giving sac key; 23 units.
Order: 18 > 16 > 17 > 21 > 15 > 20 > 19.

W22 7.5 Prize: three threat-reversal pairs (Qd1?/dxc5?, Qf5?/e6?, Qd7?/dxc7!), refutations linked; capture key, 11 pawns.
W23 6.5 Comm: set/key reciprocal change + battery mate on Kxd4 changed three times; set hint.
W24 5.5: white knight wheel of interferences, promotion duals, no change.
W25 4.5: Sushkov cycle of excluded threats, thin solution, escape key.
W26 3: two changes, capture escape key.
W27 4: rook/bishop duel miniature, untidy tries.
W28 7 HM: Bd~ mated five ways over set + three knight tries + key, each refutation the bishop move spoiling that mate; escape look, unpin checks.
Order: 22 > 28 > 23 > 24 > 25 > 27 > 26.

W29 7.5 Prize: Barnes + pseudo Le Grand inside a Sd4 white correction (random Sc2?/Sb5?, correction Sb3?, key Se6!), flight-giving key.
W35 7 HM: two pawn batteries, each knight phase destroys one (Se3?/Sd6!), changed mates by one motive; 2x1, 8 pawns.
W34 6.5 HM: tertiary arrival threat correction on e6 (dxe6?/Sdxe6?/Sfxe6!), two changed mates; same pawn captured thrice, escape key.
W33 6.5 HM-/Comm: reciprocal threat correction of two knights + pseudo Le Grand; 24 units, plugs, thin key phase.
W30 5.5 Comm: Novotny try + Grimshaw + Hannelius in tries; static king key.
W32 5: Barnes with two changes; capture escape key.
W31 4.5: king tertiary threat correction, light, capture key.
Order: 29 > 35 > 34 > 33 > 30 > 32 > 31.

W42 8 Prize: two threat-reversal pairs (Qe2?/exd5?; f6?/g6!), bQ refutes every try, three changed mates; pawn-heavy, mates converge on Bf6.
W38 7 HM: three-phase cyclic Dombrovskis/Hannelius on Scxe5/Sdxe5 (cxb6?/Qb3?/h8=Q!), two changed mates; plain promotion key, heavy.
W36 6 Comm: black knight wheel, eight unblock mates; mostly set, escape key.
W37 5 Comm: f4! flight-giving, three captures on e4, one change; heavy.
W39 4.5: anti-reversal on d7, two changes; capture key from idle rook, heavy black.
W41 4: white knight wheel all set, capture key.
W40 3: single Dombrovskis miniature, likely anticipated.
Order: 42 > 38 > 36 > 37 > 39 > 41 > 40.

W43 4.5: flight-giving key, thin transferred mates, multi-threat try.
W44 7 Prize-/HM: third-battery block, three rook tries each losing a line with own refutation, quiet zugzwang key, two changes; scaccografia pawns.
W45 6.5 HM: clean Le Grand Qa7?/Sf4! + Rxc5 change, light 16 units; single pair.
W46 7.5 Prize: queen creates batteries in try Qa3? and key Qd3!, changed cross-check mates, rook interference echo; escape look.
W47 5.5 Comm: Bf3 mates transferred over three phases; symmetric tries, heavy.
W48 5 Comm-: 7-unit miniature, 3-phase change on two captures of Sf6, same-square key; flight, likely known.
W49 4: theme in tries only, static capture key, 25 units.
Order: 46 > 44 > 45 > 47 > 48 > 43 > 49.


## Our ranking (blind; frozen before the award is read)
1. W18  (placed)
2. W16  (placed)
3. W42  (placed)
4. W07  (placed)
5. W46  (placed)
6. W22  (placed)
7. W29  (placed)
8. W17  (placed)
9. W44  (placed)
10. W35  (placed)
11. W38  (placed)
12. W04  (placed)
13. W28  (placed)
14. W11  (placed)
15. W21  (placed)
16. W45  (placed)
17. W34
18. W09
19. W23
20. W01
21. W33
22. W15
23. W20
24. W36
25. W30
26. W47
27. W13
28. W24
29. W48
30. W10
31. W12
32. W37
33. W32
34. W25
35. W39
36. W31
37. W43
38. W27
39. W02
40. W08
41. W41
42. W49
43. W06
44. W03
45. W19
46. W14
47. W40
48. W26
49. W05

## The real award (opened after commit 0f1735c): judge C. Wiedenhoff; 18 of 49 placed in yacpdb (no 2nd Prize recorded)
AUC 0.67 (`tools/blind_tourney.py compare`). Two entries are E. Bourd's: W17 (Comm; ours 8th) and W23 (1st HM; ours 19th).

| real | label | keywords | ours |
|---|---|---|---|
| 1st Prize | W28 (Pereira & Reeves) | Black correction, Changed mates | 13 |
| 3rd Prize | W34 (Rice) | Tertiary arrival threat correction | 17 |
| 4th Prize | W44 (Rosner & Reeves) | Third battery, scaccografia | 9 |
| 5th Prize | W15 (Bruch) | Carousel, Grimshaw | 22 |
| Special Prize | W33 (Shire & Reeves) | Reciprocal threat correction, reciprocal obstruction | 21 |
| 1st HM | W23 (Bourd) | Reciprocal, black correction, battery | 19 |
| 2nd HM | W01 (Shire) | Threat correction, changed and transferred mates | 20 |
| 3rd HM | W05 (Savournin) | Half-battery, changed mates | **49 (last)** |
| 6th HM | W22 (Rice) | Threat reversal (three pairs) | **6** |
| 7th HM / 8th / 9th | W31 / W11 / W35 | | 36 / 14 / 10 |
| Comm. | W42, W46, W17, W12, W25, W27 | | 3, 5, 8, 31, 34, 38 |

Unplaced in yacpdb but high with us: W18 (our 1st, Shire, white + threat correction), W16 (2nd, Stocchi-Zagoruiko),
W07 (4th, doubled Dombrovskis), W29 (7th, white correction + Barnes).

## What we learn (Problemist 2010)
1. **Giving solutions did not raise agreement here** (0.67, against 0.70 at StrateGems and 0.66-0.69 at The Problemist
   2014 without solutions). On these strong yacpdb fields our agreement sits at about 0.67-0.70, against 0.80-0.86 on the
   complete Problemesis fields. In a field where nearly every entry is competent, and the judge places 18 of 49 with many
   HMs, the order inside the middle is the judge's taste.
2. **The 1st Prize was in our upper third, not at the top**: a black correction with the random mate changed over set, four
   knight tries and the key, each refutation the bishop move that spoils that phase's mate. Our judge read it exactly right
   (7, HM) and gave more to the threat reversals and white corrections; Wiedenhoff preferred the classical black-correction
   cycle of five phases.
3. **A half-battery read as "mixed changes"** (W05, 3rd HM, our last): the tries 1.Rg7? and 1.Rxc6? and the key 1.Rxe4! are rook moves
   that the author describes as half-battery play, each phase with its own mates (e.g. 1...Rxf6+ answered by Rexf6, Rxf6, Sxf6). Our judge
   counted rude captures and 23 units and did not see the mechanism. Same lesson as Morice: name the line mechanism
   (half-battery, battery creation and destruction) before weighing the construction.
