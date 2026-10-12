# Blind judging experiment: ‡2 Problemesis 2003 (informal tourney)

E. Bourd, 12 Oct 2026: "judge all problems of the tournament, and then compare with the actual judgement ...
not biased to their actual placement".

## Protocol (frozen before the award was opened)
- Field: the 25 orthodox #2 originals published in Problemesis 2003 (`source == "Problemesis 2003"`; the 8 fairy #2s
  went to the fairy tourney). Shuffled with seed 20261012 into labels; authors, numbers, sources and solutions hidden.
- Five blind `judge` subagents, five problems each, FEN only; no database, no anticipation gate, no award.
  None recognised any problem.
- Award page: http://christian.poisson.free.fr/problemesis2004/2cproblemesis03.html, downloaded unread,
  sha256 e41f5a4559c52c494f221f62d973a2ee48efa1ff85de5f77a173f94a4b853d1b.
- This file is committed before the award is read; the comparison follows in a later commit.

## Field
| label | id | FEN |
|---|---|---|
| P01 | psis-afd7945895 | `8/1Qr2p1K/3n1rp1/6B1/8/6NN/2p2p2/4k3` |
| P02 | psis-66d8db3efb | `K2RN3/p6r/p1p2R2/1b2kN1r/1Q2n3/3P1pP1/B3q3/b2r4` |
| P03 | psis-412c6eb1e7 | `6N1/n2KP1R1/1bP5/3k3p/r4Ppq/2pB1P2/6N1/2Q3B1` |
| P04 | psis-bb0dd6670b | `Qq2r3/2pp3p/2bP1B2/1p6/pN1pk1BK/3RPp2/NPR3PP/b4r2` |
| P05 | psis-aba981b8d6 | `b2br3/B1p1RN2/4np2/5p2/QN2kppq/K4n2/1P4r1/5R1B` |
| P07 | psis-3869200029 | `4N2q/3rQp2/3b2pp/1N2n3/2P1k1P1/1p2pnP1/2r1P3/1B5K` |
| P08 | psis-4733044e4b | `3K4/B3N3/3k4/3Pp3/5P2/2p3PR/RbP5/rQ5r` |
| P09 | psis-30735aa550 | `1K1bN1b1/2p2R2/4B1n1/4p3/4k3/1N1p1R2/1pP2rP1/1qB2n2` |
| P11 | psis-2ad46635cd | `4r3/1P1B2p1/2P2p2/3kN1b1/R3N1p1/1KBn2P1/1n6/3Q4` |
| P13 | psis-974d593203 | `7b/K5Q1/5pP1/1R1p1np1/5p2/2B1kBP1/2R1Pp2/5n2` |
| P16 | psis-7939ad8170 | `8/4R1n1/1Npp4/2pp1p2/2Pk1P1N/3p4/3K4/4R1n1` |
| P18 | psis-feb230bd48 | `K7/bR6/1B1P2p1/2N1R3/1prkr3/1B3Q2/2pP2bN/8` |
| P20 | psis-c49a600bd0 | `1NBR1R2/1PQ3PK/1B6/4P3/2P1k1pp/8/4P1n1/1b4r1` |
| P21 | psis-49233800b3 | `8/6p1/1p4P1/1P4PP/2Qpk1B1/1P4P1/6p1/6Kb` |
| P22 | psis-4665a0debc | `2r3q1/p2p1Np1/6b1/8/KQ1B4/1p1k3r/2RP3b/n2BR2n` |
| P23 | psis-96568549f1 | `4QK2/4N2B/3pp3/4k2P/1p4n1/2n2R2/4N3/8` |
| P24 | psis-cffb3f0985 | `1B6/5p1K/R4N2/1r1P1kp1/1p3p1P/p2N1p2/2R5/1B2br2` |
| P25 | psis-10e356bf06 | `8/1R1N4/1p1kp1n1/Rn1P2Q1/2Pb4/1K6/1B6/8` |
| P26 | psis-2b6418e028 | `8/p1P4K/3P4/pN3Q2/k2N4/P2R3R/1PnB4/1bnn4` |
| P27 | psis-13fbcd08d8 | `1bn1N1b1/2rp3B/N1n2Q2/3k1P2/6qr/1P1PRppp/2P5/2K5` |
| P28 | psis-15bf4d17ff | `2b1Q3/8/3r4/1B3p2/1K1kN3/1p2N3/4R3/6b1` |
| P30 | psis-43940241ef | `q3r3/7Q/b4b2/3p1r2/4kpN1/2P1p3/B1N3PB/3R3K` |
| P31 | psis-0897023e85 | `3bb2N/3p4/3R2n1/3Q1pk1/6pR/6B1/K3N3/8` |
| P32 | psis-5b86b162d2 | `b3K2B/3B1p2/1pP3p1/8/R2NkN1R/p2p2n1/3P4/4rr2` |
| P33 | psis-b96894f7a6 | `r2R1R2/B2pnbN1/1q6/1N2p3/1pB1k2n/4P3/3P4/1K3Q2` |

## Judges' reports (condensed)
Group 1: P01 promotion defences f1/c1, swap of Qd2/Qe2 mates try/key, changed threat; diagram flight d1 unprovided; rook promotion dual. 4 Comm at best.
P02 knight key with 5 tries by the same knight, distinct refutations, 4 changed mates; 3 black rooks (promoted); 21 units, mixed. 5 HM if promoted rook tolerated.
P03 capture key Qxc3 from c1, Grimshaw d4, no change. 2.
P04 rook c2 three phases, three threats (Rc5?/Rf2?/Rcc3!), Dombrovskis effect, sacrificial key; thin post-key, 26 units 12 pawns. 5 HM/Comm.
P05 half-pin Bh1 on Sf3/Rg2, Qa6 key, tries Qd7/Qb3 Se5!, Qb5/Qd1 Rd2!; Se1 triple dual. 4 Comm.
Order: P04 = P02 > P05 > P01 > P03.

Group 2: P07 Le Grand/Dombrovskis on Se5 random moves + changed correction mate (Sd3 exd3 -> exf3), self-unpin key; queen escape key, 21 units 9 pawns. 6.5 HM.
P08 fourfold threat, Qb1 out of play, no change. 1.5.
P09 double threat, static key, all set. 0.5.
P11 white knight corrections Sxg4?/Sf7?/Sc4!, each try refuted by the other's defence; key flight-giving self-interference; Pb7, Pc6 cook-stoppers. 5 Comm.
P13 threat reversal Rb3?/Bxf6!, 2 changed mates; capture key; 8 pawns. 5.5 HM low/Comm.
Order: P07 > P13 > P11 >> P08 > P09.

Group 4: P23 queen tries Qf7?/Qg6?/Qc6?/Qa8!, changed threats, d5 mate changes in the try only; e8 queen far away, obvious key. 3.
P24 masked battery Bb1-Rc2-Sd3; full white knight wheel, 7 tries with different refutations, key Sc1, reversal try Rg2?; no variations after the key. 4 Comm.
P25 Sc5 sacrifice, flight-giving key, 3 captures of the key + king capture, 6 mates; single phase. 5.5 Comm/low HM.
P26 3 black knights (promoted); double threat after the key; self-pin changed mates. 1 (FEN suspect).
P27 reciprocal change of random/correction mates try d4?/key Qc3! (Sb4/Re5), changes vs set play; 22 units. 6 HM.
Order: P27 > P25 > P24 > P23 > P26.

Group 5: P28 Grimshaw e6 + knight tries, 5/10 Comm. P30 Scxe3 capture key, f5 guards, 3/10. P31 BS wheel 2 phases, Dombrovskis effect, changed mates, 5/10 Comm. P32 septuple threat (any Sd4 move), 1/10. P33 Se6 sac, 3 captures -> 3 mates on d3 (Q, P, B) with motivated dual avoidance, 6/10 HM low.
Ranking: P33 > P28 = P31 > P30 > P32.

Group 3: P16 incomplete block, R7e6! adds dxc4 Rxd6#, e-file rook tries; thin, 3 mates. 3.5 Comm at most.
P18 twin a/b/c, cycle of three keys/threats (Se6/Rd5/Qd3), Le Grand a-c on Rxe5, pseudo Le Grand, Zagoruiko 3x2; flight e5 in the diagram, keys take it, dual in c), twins redundant (c alone holds the content). 5 Comm/low HM.
P20 g8=Q double threat, static key, tries refuted by Kxe5+. 0.5.
P21 waiting key b4, only king moves, tries refuted by king moves. 0.5.
P22 Bb2! clearance, pinning defences of wQ (Rc4 Qxc4#, Rh4 Re3#), 6 variations 5 mates, bishop tries Be3? Rh4!, Bc3? Rc4!; 20 units. 6 HM.
Order: P22 > P18 > P16 > P20, P21.

## Our award (blind)
Weighing across groups (the judges' scales differ; content first, then construction):

1. Prize: **P27** reciprocal change of random/correction mates (try 1.d4? / key 1.Qc3!) plus changes from set play. Heavy (22 units).
2. Prize: **P18** twin cycle of keys and threats, Le Grand + pseudo Le Grand + Zagoruiko 3x2. Flight e5 in every diagram, the keys take it; twins partly redundant.
3. Prize: **P07** Le Grand on random knight moves + changed correction mate, self-unpin key. Queen-escape key, 9 pawns.
- 1 HM **P33** sac key captured three ways, three mates on d3 (Q, P, B), motivated dual avoidance.
- 2 HM **P22** clearance key, pinning defences of the white queen, thematic bishop tries.
- 3 HM **P13** threat reversal with two changed mates. Capture key.
- 4 HM **P04** one rook, three phases, three threats, Dombrovskis effect, sac key. Thin post-key, 26 units.
- Comm (unordered): **P25** (sac flight-giving key, 6 mates), **P02** (knight tries, 4 changed mates; promoted bR),
  **P11** (wS corrections with crossed refutations), **P31** (bS wheel two phases), **P28** (Grimshaw + knight tries),
  **P24** (white knight wheel task in tries, no post-key play).
- Nothing: P05, P01, P16, P23, P30, P03, P08, P26, P32, P09, P20, P21.

Expectation stated in advance: our rules punish promoted black force (P02, P26), double threats (P20, P09, P08, P32)
and king-move refutations (P21) as fatal; a 2003 judge may tolerate some of these. We may undervalue task
problems (P24) and overvalue heavy positions with many changes.

## The real award (opened after commit 21d3528): judge Philippe Robert
35 orthodox #2 originals (D35-D69). Our field had only 25: D60-D69 are stored in the database with source
"Inédit" instead of "Problemesis 2003", so the field selection missed them (among them the 2nd Prize D67,
2nd HM D66 and 3rd Comm D68, all three seen after unsealing, so they cannot be judged blind any more).

| Real place | No. | Author | label | our place |
|---|---|---|---|---|
| 1 Prize | D55 | M. Mladenovic | P31 | Comm (judge: 5, "thin play") |
| 2 Prize | D67 | E. Bourd | - (not in field) | - |
| 1 HM | D49 | E. Bourd | P27 | **1 Prize** |
| 2 HM | D66 | E. Bourd | - | - |
| 3 HM | D51 | A. Armeni | P24 | Comm |
| 1 Comm | D46 | E. Bourd | P01 | nothing (judge: diagram flight d1, f1=R dual) |
| 2 Comm | D42 | B. Delobel | P13 | 3 HM |
| 3 Comm | D68 | R. Aliovsadzade | - | - |

Named and rejected by Robert ("ambitious but unacceptable flaws"): D44 P21 (symmetry, tries whose threats are
never realised: no real Dombrovskis), D50 P02 (promoted black piece, duals), D53 P18 (Rb7 idle in a) and b), major
dual in c)), D57 P20 and D58 P07 (thematic try captures a black piece), D59 P28 (try captures a black piece),
D65 (dual in the solution). The other 20 were "pleasant, well built, not enough for an award".

## What we learn
1. **We were too generous: we placed 13 of 25, he placed 8 of 35 (23%).** Real informal awards are short.
   Of his 5 placed problems in our field we placed 4 (missed P01), but 8 of our 13 he did not place.
2. **Our biggest miss was my aggregation, not the judges.** The group-3 judge named exactly Robert's reasons
   against P18 (Rb7 idle in a and b, dual in c, redundant twins) and scored it 5; I raised it to 2nd Prize for
   its ambition. That broke our own rule: a dual in a thematic variation is fatal. Ambition does not buy a
   major dual in a phase.
3. **A try that captures a black unit disqualifies it for him** (P07, P20, P28). Our checklist only treats a
   capturing key as a flaw; a capturing try was not even named as a flaw (P07 1.Qxd6? got our 3rd Prize).
4. **Clarity and economy beat volume at the top.** His 1st Prize P31 (7+7, no white pawn, good key, a clean shift of
   two mates between try and solution) has no secondary play, and he says outright that this does not bother him.
   Our judge marked it down for "thin play: 3 mates". Our 1st Prize P27, with the same kind of change, got only
   1 HM from him: "construction a bit heavy", Pc2 only for the try, three black pawns weighing on it.
5. **A clear task is rewarded** (P24, the white knight's rosace (wheel) in the tries, got 3 HM; we gave Comm).
   We had predicted this bias in advance.
6. **His tolerance differs from our fatal list.** P01 (doubled Röpke, the mates swapped between phases) got a Comm despite
   the d1 diagram flight; P11/P22/P33/P04/P25 were "pleasant but not enough". The bottom of our list matched his
   rejects completely.

## Comments compared, problem by problem (Robert's words vs our blind judge)
| No. / label | Robert | our judge | match |
|---|---|---|---|
| D55 P31 | theme not new; mates A/B shift from a black correction in the try to threat + primary of the same correction; clear, economical, no wP, good key; no secondary play "does not bother me" | Dombrovskis effect, changed mates, light 7+7, long quiet key; marked down for thin play | same pluses, opposite weight on thin play |
| D49 P27 | Feldmann 2 (mates of primary and secondary of one black correction exchanged), well shown; heavy; Pc2 only for the try and against a check of wK, so 3 bPs on the 3rd rank | reciprocal change random/correction (did not name Feldmann); 22 units, f3-h3 pawn mass is construction, Kc1 cook-stopper | same content and flaws; he traced the cause (Pc2 -> wK -> pawns) |
| D51 P24 | virtual rosace of the wS at the head of a half-battery, nothing new, pleasant, tries cleverly refuted except 1.Sxe1? | 7 tries, all different refutations; known task; capture refutations cheap; no post-key play | same; he did not count the missing post-key play |
| D46 P01 | doubled Röpke with reciprocal swap of mates; skilful, graceful | saw the swap; called the d1 flight and the f1=R dual fatal | content same; he ignored both flaws |
| D42 P13 | 3 changed mates; "pseudo-reversal" because the try's threat is multiple | threat reversal, 2 changed mates (missed fxg3 Be5 -> Bxg5), capture key | he named the multiple threat, we the capture key |
| D53 P18 | Rb7 idle in a) and b), major dual in c) | the same two, plus redundant twins | identical (the aggregation overrode it) |
| D50 P02 | promoted black piece, duals | promoted bR, duals | identical |
| D44 P21 | symmetrical; tries' threats never realised, so no real Dombrovskis | "mock Dombrovskis using the king", king refutations | same |
| D57 P20, D58 P07, D59 P28 | thematic try captures a black piece | not named (P20 rejected for other reasons, P07 and P28 praised) | missed |
