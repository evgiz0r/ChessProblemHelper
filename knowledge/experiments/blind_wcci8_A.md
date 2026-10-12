# Blind judging experiment 11: WCCI 8, section A (#2), the winners (scored)

E. Bourd uploaded WCCI8-A-Winners.pdf (12 Oct 2026). An extractor agent built 15 FENs (all keys verified), cleaned the published
solutions of names, scores and comments, and sealed ranks, scores and authors (/tmp/claude-0/sealed/wcci8a_key.json).
Two blind `judge` agents (FEN + cleaned solution), told to spread their scores among strong problems. Scale note: judge 1
(C01-C07) scored higher overall than judge 2 (C08-C15); merged by score, ties by the judges' own orders.

## Field
```
C01: 6b1/2p3K1/3BP1NR/1Q2pk2/2PP2nP/3PRNbB/4rq2/8 w - - 0 1
C02: K7/2p2p2/8/PR1RB3/P1k1p3/1N3q2/n2P4/1B1Q2b1 w - - 0 1
C03: 1b6/3R2KB/4N2n/1pNPkp2/1QP3Pp/2p3q1/2p1n2B/2rb1R2 w - - 0 1
C04: 4r1r1/bB6/8/1K1R1P2/3Bkp2/3p2P1/1P4n1/5Q2 w - - 0 1
C05: 4R3/1KPp3b/pQ1p3p/P2k4/1PpN1Pn1/2P1pP2/1r1N3q/3R4 w - - 0 1
C06: 7r/8/6N1/1Q5p/3RPN1P/3P1k1K/6Rb/n1n3B1 w - - 0 1
C07: 8/4Qp2/r2r4/p2kP3/K3p1BR/5p2/2NN4/2R3B1 w - - 0 1
C08: 1Br5/4P2R/2P1k3/2Pb3p/3P2rN/KB3R1Q/5pN1/8 w - - 0 1
C09: 2RB1br1/1B2p1PQ/2N1N1r1/1p6/1R4P1/p1kP4/p2p1P2/qn1K4 w - - 0 1
C10: 1n4B1/3P4/7p/r3Nk1P/2r1R1N1/b1P4Q/8/2B1nK2 w - - 0 1
C11: 8/2NK4/p3P3/r1P3B1/P1Bk2N1/PQbP3R/1n4n1/2R5 w - - 0 1
C12: 2R5/2P1P1BB/pN4n1/1pPNn2r/1Qpk1P2/2pP1P1p/5P2/R3K3 w Q - 0 1
C13: 4K3/n2Q1p2/p2N4/PRp1pp2/B1NkP3/8/2P1bP2/b3B3 w - - 0 1
C14: 6R1/6Q1/4N3/5Bbr/1p1pNP1P/5kp1/R1n3p1/2Bbn1K1 w - - 0 1
C15: 1B1Q4/3p1pnK/N2Nkr1b/1R1pp2P/n3p1Pq/3B1P2/r1P5/1b1R4 w - - 0 1
```

## Judges' reports (condensed)
C01 6.5: Zagoruiko 3x2 + pseudo Le Grand; capture key with check, diagram flight.
C02 6: valve on e3 shown in three phases, change on Bxd4; one defence.
C03 5: crossed threat/refutation paradox, Ventura key; heavy, capture tries.
C04 8: threat-pair cycle in double-threat tries (Qf2?/Bc3?/Bg1?), key Bg7! single threat, refutations return as mates; Bd4 white correction, 15 units.
C05 9: Zagoruiko 3x2 with knight key/mate cycle (Nc2/Ne2/Ne4), doubled Vladimirov; 12 pawns.
C06 7.5: Zagoruiko 4x2 with set play, try move/mate swap, long quiet key, 16 units.
C07 4: known reciprocal swap, rude tries, diagram flight.
Order: 05 > 04 > 06 > 01 > 02 > 03 > 07.

C08 6: Barnes + Vladimirov, key unpins bR (three defences answered by A/B/C); thin change, rough refutations.
C09 7: reciprocal key/mate exchange Ba5?/Rxb5! + Le Grand on Kxd3, Zagoruiko 3x2; capture key, diagram flight, heavy.
C10 5: double threat split by Sf7?/Sf3!, Le Grand twice; unprovided flight, promotion-only pawn.
C11 4: Le Grand + Zagoruiko 3x2; unprovided flight, king refutation, capture try.
C12 6: threat reversal + castling dual avoidance, Zagoruiko; 24 units 12 pawns.
C13 6: clean Zagoruiko 4x2, routine, capture key.
C14 7: Zagoruiko 4x2 on self-pinning flight and Se3, transfers, Levman; unprovided flight.
C15 8: 2x3 task (B, S, P to e4 and c4, dx answered by different mates) + theme B + Dombrovskis + Vladimirov; 25 units.
Order: 15 > 09 = 14 > 08 = 12 = 13 > 10 > 11.


## Our ranking (blind; frozen before the scores are read)
1. C05
2. C04
3. C15
4. C06
5. C09
6. C14
7. C01
8. C02
9. C08
10. C12
11. C13
12. C03
13. C10
14. C07
15. C11

## The real scores (opened after commit 0831a98)
WCCI points (the PDF prints totals only): C10 10; C05 9.75; C01, C02, C06, C07, C11, C12, C13 9.5; C03, C08, C14, C15 9;
C04, C09 8.5. Spearman between our order and the points: **-0.32** (n = 15, a narrow range of 8.5-10).

| problem | points | ours | why we put it there |
|---|---|---|---|
| C10 (Dyachuk) | **10** | 13 | Burmistrov combination (double Le Grand), Zagoruiko on two defences on e4; "unprovided flight, promotion-only pawn" |
| C05 (Guida) | 9.75 | **1** | Zagoruiko with key/mate cycle |
| C11 (Gavrilovski) | 9.5 | 15 (last) | Le Grand + Zagoruiko; "flight, king-refuted try, capturing try" |
| C07 (Kovačević) | 9.5 | 14 | reciprocal swap; "rude tries, diagram flight" |
| C04 (Kovačević) | **8.5** (lowest) | 2 | cyclic threats in tries + Dombrovskis; "clean, 15 units" |
| C09 (Dyachuk) | 8.5 | 5 | reciprocal key/mate exchange |

## What we learn (WCCI)
1. **At world level the scale inverts our weighting.** Every entry is rich; the judges paid for content (Burmistrov, Zagoruiko
   with Le Grand, complete multi-phase complexes) and ignored the flaws our judges count (unprovided flight, a pawn for a try,
   king-refuted try, capturing tries). Our judges rewarded cleanliness and economy (C04 2nd), the WCCI judges did not.
2. **E. Bourd's rule "tolerance grows with content" is not applied strongly enough**: at this level, flaws that are serious
   in an informal tourney move a problem by fractions of a point, not to the bottom.
3. **Burmistrov is undervalued again** (also Moscow 2012, Problemist 2011). A three-phase double Le Grand on one or two
   defences is top content for real judges.
4. Caveat: 15 problems in a 1.5-point range; noise is large. WCCT 11 (full entries book, anonymous, scored) is the next test.
