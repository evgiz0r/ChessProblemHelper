# Blind judging experiment 7: StrateGems 2015 #2 informal tourney (field from yacpdb, with solutions)

E. Bourd, 12 Oct 2026: "Go next". Field: yacpdb `Stip("^#2$") AND Source("StrateGems") AND PublishedAfter("2014-12-31") AND
NOT PublishedAfter("2015-12-31")`, filtered to source year 2015 exactly, without twins/options; one entry awarded in a
separate miniature tourney excluded. 32 problems, shuffled (seed 2015) into G01-G32. Sealed:
/tmp/claude-0/sealed/yac/StrateGems_2015_v2.json. NEW: each judge got the FEN, the published solution and the author's
theme keywords (no author, source or award), as a real judge has; solution texts were checked for award words (none).
Four blind `judge` agents; none recognised a problem. Placing about a third (11).
Data note: G08 shows the white king in check in yacpdb's diagram (Kb4, bRg4, empty 4th rank); every try and the key parry it.

## Field
```
G01: Nnr2b2/3p1P1P/r1n5/QP1k1P2/p2PN3/2PP4/8/7K
G02: B7/4Qp2/K2P1p2/ppN5/3k3r/1PR3br/1PP4p/5n2
G03: 8/prr5/KpR1pp2/3kp3/3B2Q1/2Rp4/4N3/3b4
G04: 3RR3/8/4Npp1/2Nn4/3pp1Q1/2nBkp2/6Pp/K3B3
G05: 2R5/1n4Pb/2N5/ppNk4/1Qr2B2/5n2/B3R3/7K
G06: 3Q4/3K3B/p1PpP3/1n1kb3/3P4/pPp1P1p1/1N1PN3/3R3b
G07: 8/1K2p3/1b1pNp2/1Np1Bp1n/2B1kp2/3p4/1Q1P1R2/1b4r1
G08: 8/Q3Np2/4kP2/R3B1R1/pK4rr/2pp1P1B/pn3N2/q7
G09: K6B/p3R2n/r3p3/1BPk4/2RNpb1r/3P4/2n1p2p/1b1Q4
G10: 4R1B1/3p2p1/Np1k1b1q/1Pr1N1P1/2p1pQ2/B2n4/3R4/K2n4
G11: 1NK5/2P2Q2/R2Pr3/1N1kp2R/pp4p1/PP6/4P3/6B1
G12: 2q1n1n1/2B5/pR4N1/2pk1r2/6RQ/K2P1p2/N7/2r5
G13: bn6/2p5/1pN5/1RPk4/PB3R1b/2P2K1Q/4P3/5B2
G14: 6Q1/1K3n2/2R5/1p1kP1n1/3N1P2/3PB3/1r1b4/1R3N2
G15: 2Q2BB1/1p3rn1/2qP4/PpN4p/1pk3bR/1N1R4/K1P5/n7
G16: q3R3/2p1N3/2n1B3/p2P3R/K1QNkp2/8/5Pb1/8
G17: 6Bn/1QR2r2/P2p4/2q2N1n/1Pk1P3/bpB1R3/r2P1K2/1N6
G18: bbB5/3R4/5pKn/5R1p/4ppkr/6n1/2q3Qp/3r2NN
G19: 4R3/1N1p4/P2Pb1N1/2Pk1P1K/P1pnnp1Q/2B2B2/8/8
G20: K1Nn4/1p4p1/4pkP1/QN4pP/P3R1P1/r4n2/1q1r4/B4R2
G21: 2bR3K/4NN2/1n2kpQP/Rp2p2p/4p3/B2P3n/6p1/b7
G22: 8/5p2/1R6/8/K7/6Bk/7P/1Q6
G23: 8/3K4/1p1NpP2/1nNkB1R1/4p3/bpR3P1/4n1r1/Q6B
G24: 5R2/1p2pP2/4k3/1N3r2/3P2B1/3P2K1/8/7Q
G25: b7/2pP1KQB/1q1P4/1p1kP1NR/3N1p2/1PRp4/4P3/8
G26: B2QKn2/1r1pp3/3p1p1r/3PkP1P/2R1N3/5pN1/4PP2/3R4
G27: Kn5B/3p2rp/1p1Q2b1/5k2/R3p3/4b1R1/2BNr3/7q
G28: 1K1NR2B/QppPN2n/2PqBpPb/4k3/8/2pRPP2/8/3r4
G29: 8/8/5K2/6Bk/6pp/8/4n3/6Q1
G30: 4B2K/3nPP2/1r2RPNR/2Pp1kp1/2p5/2N5/bn1BQP2/8
G31: 2K1RN2/1QN5/p4p1r/2p1nk1p/7P/2PR2P1/4B3/2b5
G32: Q5n1/3pp2b/2p5/1p4R1/2p1k3/5p1N/3R1p1n/1K3N2
```

## Judges' reports (condensed)
G01 5: bS correction over 3 phases + pseudo Le Grand Qc7?/Qb6!; escape key, pawns only for an artificial promotion try.
G02 6.5 HM: knight tries each refuted by a different bB correction (one black unit, theme A), changed-threat interference try, sacrificial key Sa4!; 9 pawns.
G03 5: Bd4 white threat correction (secondary/tertiary), key Bxe5! capture, thin post-key.
G04 3: white knight correction drowned in captures and king refutations.
G05 6 Comm: Sb3! indirect unpin, B+S battery, cross-check, switchback; one phase.
G06 7 Prize: Banny pair (Qg5?/Qa5? and key dxc3!) tied to the set black corrections, changes over three phases; capture key, 11 pawns.
G07 4: transferred mates, crossed refutations of bishop tries; three capturing first moves.
G08 2: White in check in the diagram (probably a data error); Sc4 three changed mates.
Order: 06 > 02 > 05 > 01 > 03 > 07 > 04 > 08.

G09 5.5: Moscow theme 2x2 (Sxe6?/Sc6!); capture try, heavy.
G10 6 HM: Bb2?/Rb2! unpins with switchbacks, self-pin on e5 in both phases; crude refutation, heavy.
G11 6.5 HM: zugzwang Lacny cycle on Ke4/bxa3/g3 (Rh4?/Rxa4!); diagram flight, capture key and refutation.
G12 5: three mates on c4 over phases, untidy tries, predictable key.
G13 4: two batteries never meet, provoked checks.
G14 4.5: white knight correction skeleton, capture key.
G15 3.5: anticipatory Novotny, superfluous Rh4.
G16 8 Prize: Salazar + pseudo Le Grand from one half-battery (Sc8?/Bg4!), quiet key and refutation, 16 units.
Order: 16 > 11 > 10 > 09 > 12 > 14 > 13 > 15.

G17 6.5 HM: three-phase pseudo Le Grand cycle by Bc3 (Bf6?/Bd4?/Bb2!), distinct refutations; static key phase, heavy.
G18 7.5 Prize: rook tries Rd6?/Rdd5?/Rd4!, half-pin by key, 2x2 reciprocal change, each try refuted by the other thematic defence; heavy black.
G19 7 HM: doubled Dombrovskis through selfpin (Qh1?/Qf6?/Qg5!), pseudo Le Grand between tries; diagram flight c6, 8 pawns.
G20 5: doubled English Novotny (Sc3?/Sd4!), shared Qe5, heavy.
G21 5: threat correction + queen dual avoidance; capture key, unthematic refutation.
G22 3.5: miniature king-move Dombrovskis, flights.
G23 4.5: cycle of double mates task, capture escape key, mechanical.
G24 3.5: block, one change, flights.
Order: 18 > 19 > 17 > 20 > 21 > 23 > 24 > 22.

G25 5: threat reversal e6?/Se4!, triple change on Qxd4; unprovided diagram flight, try refuted by king.
G26 4: Se4 knight threat correction (Sc3?/Sxf6?/Sxd6?/Sd2!); diagram flight, capture tries, thin key.
G27 7 Comm: pseudo Le Grand Sxe4?/Rxe4! + Rice theme + double switchback, 7 white units, no white pawns; thematic captures, heavy black.
G28 7.5 Prize/HM: Zagoruiko 3x3 (Qa2?/Bf5?/Sg8!) + reciprocal change; escape key, 22 units.
G29 2.5: queen miniature, obvious key.
G30 6: sac flight-giving key Se4!, try threats return as mates; heavy.
G31 7 HM: threat reversal Rd5?/Qb1!, Zagoruiko 3x2, flight Ke4 mated three ways; random duals.
G32 3: Fleck fragment, crude tries, corner queen key.
Order: 28 > 31 > 27 > 30 > 25 > 26 > 32 > 29.


## Our ranking (blind; frozen before the award is read)
1. G16  (placed)
2. G18  (placed)
3. G28  (placed)
4. G06  (placed)
5. G19  (placed)
6. G31  (placed)
7. G27  (placed)
8. G02  (placed)
9. G11  (placed)
10. G17  (placed)
11. G10  (placed)
12. G05
13. G30
14. G09
15. G21
16. G20
17. G25
18. G01
19. G03
20. G12
21. G14
22. G23
23. G26
24. G07
25. G13
26. G24
27. G15
28. G22
29. G32
30. G04
31. G29
32. G08
