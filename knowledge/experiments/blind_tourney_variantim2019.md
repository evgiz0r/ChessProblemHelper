# Blind judging experiment 9: Variantim 2019, Israel Ring Tourney #2 (yacpdb, with solutions)

E. Bourd, 12 Oct 2026: "go next, ill come back and answer questions sometime". Built with `tools/blind_tourney.py build
"Variantim" 2019 --tourney "Israel Ring Tourney" --label V --size 7`: 20 problems (6 awarded in other tourneys excluded),
of which V09 and V16 turned out fairy (neutral pieces) and are excluded: 18 orthodox. Three blind `judge` agents with
solutions and keywords, told to name the line mechanism before weighing construction. Placing about a third (6).

## Field
```
V01: 1R1K4/2N2pBn/2pk4/1P1P2r1/1P2RP2/4b3/bN5q/4Q3
V02: 2N3QK/5p2/pp3k1b/2pBR1pb/2N3p1/r2pp3/1q6/BR6
V03: 1Bn5/2R1p3/6K1/5R2/2Ppkp2/2P1p3/2b1P3/4n3
V04: 2R5/p3P3/1bB1pK2/pQNpN3/P2kp1bR/8/8/n1B4n
V05: 3N4/1Pppp3/1pPkpp2/2p5/2PB4/2P4Q/5PK1/b7
V06: 2K3Rn/2Rp4/3k1b2/1PN4B/5P2/4N3/3B1n2/3r4
V07: 1r2B2Q/q4RpN/2R3b1/1P1k4/1p4P1/3P2BK/4N3/8
V08: b5K1/3p1P2/4kP2/R1bR2P1/6Pn/1Q2Npr1/6nB/8
V09: 2r5/4pPRR/3BP3/1p6/2Pk3K/Nb3pN1/1P2PP1n/8
V10: 7Q/6qr/1n4b1/R3p1B1/pPpk4/N2p4/1K1P4/4R3
V11: 2N4Q/8/4npP1/B3kNn1/2B2R2/4pP2/4P3/K7
V12: 5R2/4nBn1/8/2p5/2K2p1R/4NkN1/3P4/4B3
V13: r7/p3p3/K3p2Q/2B1kp1p/4P1nR/1R4n1/B1N1p1N1/b7
V14: 5q2/5p2/1PB5/b7/pkpQN3/pb1p4/PR4p1/RN1n2K1
V15: n4Qb1/8/1p3R2/5NRp/3Bk3/6P1/8/2K2B2
V16: K7/3RN3/2PP2RB/4k3/2p1p3/n1Pp1p2/3P1P2/8
V17: 8/2K4b/1p6/B3n3/1N3N2/1PR2P2/qQ1pPp2/2Rnkrb1
V18: 3q4/b7/1R4p1/3Q2P1/3PPB2/2P2k1P/4N3/1B3K2
V19: 3Q4/3PK3/2p5/1Bp5/R4P2/4k3/1Pp1N1PP/2bbB1Nq
V20: 3B2rN/5Rq1/3pp1p1/1bNPk3/2P4p/2PB1KP1/p5n1/3R4
```

## Judges' reports (condensed)
V01 8 Prize: Luukkonen, three captures on d5 each opening its own line, three set mates transferred, sac key Rd4!, threat-changing tries; set dual on f5.
V02 7 Comm: set/key reciprocal change by one bishop move (gives up a guard, closes a line, pin); heavy black.
V03 6: complete Karlstrom-Fleck, one phase, easy key.
V04 7.5 HM: double white correction (knight and bishop) with threat corrections, pseudo Le Grand, flight-giving capture key.
V05 4: changed mates, pawn wall.
V06 5: Le Grand + Mäkihovi on Ke7, one defence, known scheme.
V07 5.5: complete cycle of double mates over five mates, capture key from out of play.
Order: 01 > 04 > 02 > 03 > 07 > 06 > 05.

V08 6.5 Comm: reciprocal change by switching the battery's rear piece (Qc4?/Qd3!) on Bd6/Rxg4; set=try, heavy black.
V09 -: fairy (neutral pieces), excluded.
V10 7.5 HM: Sushkov pair Rexe5?/Raxe5! + pseudo Le Grand + set changes, 8+9.
V11 8 Prize: white knight wheel as cumulative white correction (random Kxf4!, Sd4? Sxf4!, Sd6? Sg7!, Sg7? Sxf3!, Sfe7!), black correction too; open flight f4.
V12 3.5: reciprocal mutate, author says anticipated.
V13 5: Salazar exchange on Sxh6, capture try, heavy.
V14 3: static key.
Order: 11 > 10 > 08 > 13 > 12 > 14.

V15 4.5: pseudo Le Grand on two flights, static king key, diagram flights.
V16 -: fairy (neutral pieces), excluded.
V17 6 HM: threat anti-reversal e4?/Re3! + Le Grand/Dombrovskis on dxc1=Q+ (key opens the c-file for the check); idle wQ, plugs.
V18 7.5 Prize: 2x2 grid of Q/R line moves deciding Qxd4/Bxd4 mates (cxd4/Sxd4), four phases, sac key Rf6!, four black units; capture refutations, plugs.
V19 5: doubled Fleck/Brogi (Qg8?/Qh8!), twelve-mate separation changed; mechanical, heavy.
V20 5.5: seven defences with combinatorial effects, key mostly adds a threat.
Order: 18 > 17 > 20 > 19 > 15.


## Our ranking (blind; frozen before the award is read)
1. V11  (placed)
2. V01  (placed)
3. V18  (placed)
4. V10  (placed)
5. V04  (placed)
6. V02  (placed)
7. V08
8. V17
9. V03
10. V20
11. V07
12. V19
13. V13
14. V06
15. V15
16. V05
17. V12
18. V14
(V09, V16: fairy problems with neutral pieces, excluded; tools/blind_tourney.py now filters them.)

## The real award (opened after commit bcbcf1c): judge V. Kopyl, 8 of 18 orthodox placed
| real | label | keywords | ours |
|---|---|---|---|
| 1st-3rd Prize | V18 (Gockel) | Reciprocal | **3** |
| 1st-3rd Prize | V04 (Doukhan) | White correction, threat correction, caprice | **5** |
| 1st HM | V19 (Maleika) | Fleck, Brogi, cycle of double mates, changed mates | 12 |
| 2nd HM | V01 (Uris) | Luukkonen, transferred mates | **2** |
| 3rd HM | V02 (Murashev) | (reciprocal change by one bishop move) | **6** |
| 1st Comm | V11 (Piliczewski) | Black correction, white knight wheel | **1** |
| 2nd Comm | V17 (Papack) | Threat anti-reversal, Zhuravlev, Le Grand | 8 |
| 3rd Comm | V14 (Svitek) | (cyclic defence effects) | 18 (last) |

AUC 0.76 on the 18 orthodox problems (0.80 printed by the tool counts the two fairy entries placed last). Five of his eight
are in our top six; his two Prizes are our 3rd and 5th.

## What we learn (Variantim 2019)
1. **Best agreement on a strong field so far** (0.76): the "name the line mechanism" instruction and the softened rude-move
   weighting may have helped (W05-type misses did not recur), but one tourney of 18 is not proof.
2. **The doubled Fleck/Brogi change (V19, 1st HM)** was read correctly and judged "mechanical bookkeeping" (5). Kopyl paid for
   the complete changed separation scheme. Judges again differ on tasks (Morice and Wiedenhoff also placed tasks we put low).
3. **V14 (3rd Comm, our last)**: the author's cyclic defence effects (AB/BC/CD/DA) "do not show on the board" for our judge.
   An open question for E. Bourd: how to read such cyclic labels.
