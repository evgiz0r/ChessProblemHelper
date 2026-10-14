# Blind prediction 1: WCCT 12, section A (#2), all 63 entries, judged before the award

Frozen on 14 Oct 2026, before any award. Source: 12-WCCT-Section-A-entries.pdf (wfcc.ch, anonymous entries A01-A63). An extractor
agent read all 63 diagrams (piece counts and keys verified: every published key is the solver's only key). Six blind `judge` agents
(checklist as calibrated by WCCT 7-11) scored them 0-10 with the published solutions and composers' comments. When the award
appears: compare `our_rank` / `our_score` in predict_wcct12_A.json with the WCCT points (Spearman, and against each judging
country), as in the WCCT 10 and 11 experiments (full fields: 0.73 and 0.63).

## Theme
```
Theme (proposed by Serbia): Double Mate Correction with the solution and the thematic try starting by
moves of different white pieces.
Double Mate Correction (DMC) is a new thematic combination, involving changed mates (at least 3×1)
and changed defences (at least 3×1) in set-play, try (or tries), and solution:

Scheme (table printed as an image in the entries book):
              a     b     c
  set         X     ~     ~
  try         A     X     ~
  solution    B     ~     X

The empty squares with the sign “~” after black moves b/c may be:
1) any mate other than X (in any phase), other than A in the try, and other than B in the solution;
2) no mate (either black moves b/c don’t prevent the threat or they refute the try).
No thematic variation should repeat between the phases, even if the concrete black move doesn’t
defend against the threat in the try or solution. In other words, no thematic variation (defence+mate)
should work in another thematic phase.

Different DMC forms may be found in the Jurmala IT 2024 Announcement
(https://wccc2024.wfcc.ch/wp-content/uploads/2024/05/Jurmala-WCCC-2024-Internet-Tourney.pdf)
and in the award of the same tourney
(https://wccc2024.wfcc.ch/wp-content/uploads/2024/08/Jurmala-IT-2024 Award.pdf).
These two documents include 34 more DMC examples that are not thematic for 12th WCCT only
because the solution and the thematic try start by moves of the same white piece.
```

## Our ranking (entry code, our score)

| rank | entry | score | rank | entry | score | rank | entry | score |
|---|---|---|---|---|---|---|---|---|
| 1 | A44 | 8.5 | 22 | A16 | 6.5 | 43 | A53 | 5 |
| 2 | A47 | 8.5 | 23 | A38 | 6.5 | 44 | A30 | 5 |
| 3 | A54 | 8 | 24 | A51 | 6 | 45 | A08 | 4.5 |
| 4 | A42 | 8 | 25 | A22 | 6 | 46 | A04 | 4 |
| 5 | A52 | 8 | 26 | A63 | 6 | 47 | A17 | 4 |
| 6 | A46 | 8 | 27 | A09 | 6 | 48 | A11 | 4 |
| 7 | A49 | 7.5 | 28 | A57 | 6 | 49 | A55 | 4 |
| 8 | A25 | 7.5 | 29 | A62 | 6 | 50 | A29 | 4 |
| 9 | A10 | 7.5 | 30 | A58 | 6 | 51 | A61 | 3.5 |
| 10 | A02 | 7 | 31 | A28 | 6 | 52 | A27 | 3.5 |
| 11 | A05 | 7 | 32 | A32 | 6 | 53 | A43 | 3 |
| 12 | A15 | 7 | 33 | A56 | 6 | 54 | A06 | 3 |
| 13 | A41 | 7 | 34 | A35 | 6 | 55 | A60 | 3 |
| 14 | A20 | 7 | 35 | A23 | 5.5 | 56 | A24 | 3 |
| 15 | A33 | 7 | 36 | A31 | 5.5 | 57 | A40 | 3 |
| 16 | A13 | 7 | 37 | A37 | 5.5 | 58 | A01 | 3 |
| 17 | A45 | 7 | 38 | A14 | 5 | 59 | A07 | 2 |
| 18 | A34 | 7 | 39 | A36 | 5 | 60 | A50 | 2 |
| 19 | A21 | 7 | 40 | A59 | 5 | 61 | A12 | 2 |
| 20 | A03 | 6.5 | 41 | A39 | 5 | 62 | A19 | 2 |
| 21 | A18 | 6.5 | 42 | A48 | 5 | 63 | A26 | 2 |

## Judges' notes by group (labels P01-P63 map to entry codes in predict_wcct12_A.json)

    g0 P03 8.5|P05 8|P10 7|P11 7|P07 6.5|P01 6|P02 6|P08 5|P04 2|P06 2|P09 2
    P03: DMC as a full Zagoruiko 3x3, flight key with switchback. P05: four phases, mate after Bxd5 changes four times. P10: Salazar reversal of try/key moves with A/B. P11: double Dombrovskis via extra tries. P09: try and key by the same knight (fails the WCCT condition). P06: unprovided set check, B is one of seven battery mates. P04: formal only.

    g1 P19 8.5|P18 8|P17 7|P13 6|P15 6|P21 6|P20 5.5|P22 4.5|P14 3|P16 3|P12 2
    P19: DMC + extra try with Dombrovskis on all three defences, exd5 mated four ways. P18: DMC doubled on two defences, Zagoruiko 3x2, flight key. P17: DMC + Rukhlis, provided diagram flight. P12: theme not met. P14: A and B the same mate (on paper only).

    g2 P26 7.5|P25 7|P33 7|P27 6.5|P32 6.5|P31 6|P30 6|P24 5|P23 4|P28 3.5|P29 2
    P26: DMC doubled (two tries + key, four mates after Qe3), en passant defence. P25: try/key swap threat and first move, flight key, threat correction. P33: semi-reciprocal with set, Shanshin dual avoidance. P29: theme not strict (double threats).

    g3 P40 8|P34 7|P35 7|P38 6|P42 6|P37 5|P44 5|P36 4|P39 4|P41 4|P43 3
    P40: DMC + Sushkov threat returns, cyclic pseudo Le Grand, Dombrovskis refutation, flight key; heavy. P34: DMC + Zagoruiko 3x2, 7+6. P35: extra try, X transferred three times. P38: tertiary mate correction over three phases, telltale unprovided set move. P37: "after Bogdanov 2005" (low originality). P43: try with two refutations.

    g4 P51 8|P47 7|P49 7|P53 6|P52 6|P46 5|P48 5|P50 5|P45 4|P54 3|P55 3
    P51: two extra changes, flight-giving unpinning key creates the defence, 8+7. P47: Zagoruiko 3x2, four further changes, sacrificial flight key. P49: key to the try-refutation square, sacrifice, 8+9. P55: theme on paper only.

    g5 P56 7.5|P57 7.5|P60 7|P62 6.5|P58 5.5|P63 5.5|P59 3.5|P61 3
    P56: second try gives 3-step change, each first move opens a black line to d6; heavy. P57: b and c from pin releases, queen-sacrifice key. P60: mutual dual avoidance on d4, capturing try and key. P59: theme not strict (b variation repeats). P61: try-only queen.

## What our judges flagged as not meeting the theme strictly
P09 (try and key by the same knight), P12 (X never returns), P29 (double threats), P59 (a thematic variation repeats), P06 (B one
of seven battery mates), P04/P14 (A and B the same mate by two knights), P55 (A and B after a non-defence), P43 (thematic try with
two refutations). If the WCCT judges exclude or zero some of these, that is a check on our theme reading as well.
