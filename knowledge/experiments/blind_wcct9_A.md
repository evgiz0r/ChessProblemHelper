# Blind judging experiment 14: WCCT 9, section A (#2), the problems printed with a diagram (scored)

Source: the WCCT 9 final award booklet (wfcc.ch). An extractor agent built 27 FENs (every problem of section A with a diagram;
all keys verified unique); scores, places, countries sealed in /tmp/claude-0/sealed/wcct9a_key.json. Three blind `judge` agents
got FEN, published solution (composer's comments kept) and the set theme, with the checklist as calibrated after WCCT 10, and
were told to spread scores (probably the better part of the field).

> Theme: In a directmate in 2 moves, two tries have the same threat A. Another two tries have
> the same threat B. In the solution neither move A nor move B is a threat but both become
> mates in variations.

## Frozen ranking (committed before unsealing)
```
W21 W10 W27 W01 W17 W26 W07 W12 W03 W16 W20 W25 W09 W14 W22 W24 W08 W18 W02 W19 W23 W05 W11 W13 W15 W04 W06
```

## Scores and notes by group (judge's order)

    g0 W10 8.5|W01 8|W07 7|W03 6.5|W09 6|W08 5.5|W02 5|W05 4.5|W11 4.5|W04 4|W06 3.5
    W10: four queen tries, Hannelius with Dombrovskis, pseudo Le Grand, block key with six variations. W01: textbook Hannelius + Dombrovskis, quiet key. W07: third pair adds cyclic pseudo Le Grand, heavy. W09: reciprocal threat correction + Rukhlis, static key. W06: static key.

    g1 W21 9|W17 7.5|W12 7|W16 6.5|W20 6.5|W14 6|W22 6|W18 5.5|W19 5|W13 4.5|W15 4.5
    W21: symmetric Hannelius/Dombrovskis, Zagoruiko on both defences, quiet pawn key, 9+7. W17: two Dombrovskis + two Hannelius in 14 units, diagram flight. W12: three pairs, knight corrections, heavy. W22: double white correction with crossed threats in the tries, static key.

    g2 W27 8|W26 7.5|W25 6|W24 5.5|W23 4.5
    W27: Hannelius crossing (Rxe4/dxe4), all four try refutations return, changed mates, quiet key, 11+9. W26: Hannelius + pseudo Le Grand queen tries, capturing key. W25/W23: rich try sets but static key (set mates unchanged).

## Unsealed: WCCT points (GER, RUS, SRB, SVK, UKR; 0-4 each, own country not judged) against our blind score

| entry | WCCT code | place | points | our rank | our score | author |
|---|---|---|---|---|---|---|
| W21 | A67 | 1 | 9.75 | 1 | 9 | Pavel Murashev, Anatoly Slesarenko & Aleksandr Feoktistov (Russia) |
| W07 | A20 | 2 | 8.75 | 7 | 7 | Vasil Krizhanivsky (Ukraine) |
| W17 | A40 | 3 | 8.0 | 5 | 7.5 | C.G.S. Narayanan (India) |
| W03 | A58 | 4 | 7.5 | 9 | 6.5 | John Rice (Great Britain) |
| W09 | A65 | 5-8 | 7.0 | 13 | 6 | Janez Nastran (Slovenia) |
| W11 | A34 | 5-8 | 7.0 | 23 | 4.5 | Yosi Retter & Paz Einat (Israel) |
| W22 | A32 | 5-8 | 7.0 | 15 | 6 | Marco Guida (Italy) |
| W23 | A04 | 5-8 | 7.0 | 21 | 4.5 | C.G.S. Narayanan (India) |
| W14 | A31 | 9-12 | 6.75 | 14 | 6 | Marjan Kova evi (Serbia) |
| W20 | A57 | 9-12 | 6.75 | 11 | 6.5 | Valery Shanshin (Russia) |
| W24 | A28 | 9-12 | 6.75 | 16 | 5.5 | Marjan Kova evi (Serbia) |
| W25 | A74 | 9-12 | 6.75 | 12 | 6 | Emil Klemani (Slovakia) |
| W04 | A25 | 13 | 6.5 | 26 | 4 | Alekseï Gasparyan & Shamil Chobanyan (Armenia) |
| W02 | A59 | 14-15 | 6.25 | 19 | 5 | Emil Klemani (Slovakia) |
| W27 | A63 | 14-15 | 6.25 | 3 | 8 | Vasil Dyachuk & Valery Kopyl (Ukraine) |
| W06 | A35 | 16-18 | 6.0 | 27 | 3.5 | Daniele Giacobbe (Italy) |
| W08 | A14 | 16-18 | 6.0 | 17 | 5.5 | Vasil Dyachuk & Valery Kopyl (Ukraine) |
| W19 | A33 | 16-18 | 6.0 | 20 | 5 | Zoran Gavrilovski (Macedonia) |
| W10 | A55 | 19 | 5.75 | 2 | 8.5 | Štefan Sovík (Slovakia) |
| W01 | A26 | 20-27 | 5.5 | 4 | 8 | Nikolaï Belchikov & Valery Frigin (Belarus) |
| W05 | A24 | 20-27 | 5.5 | 22 | 4.5 | Mikhaïl Khramtsevich & Viktor Zaitsev (Belarus) |
| W12 | A09 | 20-27 | 5.5 | 8 | 7 | Janne Syväniemi (Finland) |
| W13 | A60 | 20-27 | 5.5 | 24 | 4.5 | Jorge Lois & Jorge Kapros (Argentina) |
| W15 | A46 | 20-27 | 5.5 | 25 | 4.5 | Robert Burger (USA) |
| W16 | A70 | 20-27 | 5.5 | 10 | 6.5 | Oleg Pervakov & Anatoly Slesarenko (Russia) |
| W18 | A71 | 20-27 | 5.5 | 18 | 5.5 | C.G.S. Narayanan (India) |
| W26 | A06 | 20-27 | 5.5 | 6 | 7.5 | Paz Einat & Emanuel Navon (Israel) |

## Agreement
- Spearman against the total over the 27 entries: **0.16**. Against each country: GER 0.36, RUS 0.22, UKR 0.13, SVK 0.00, SRB -0.06.
- **The countries among themselves: -0.50 to 0.37, mean 0.08**; each country against the sum of the other four: -0.03 to 0.13. In
  this field (the 27 entries printed with a diagram, 5.5 to 9.75 points, marks in half points) the real judges' order is close to
  noise, and ours agrees with the total better than any country agrees with the other four.
- **1st place found**: A67 (Murashev, Slesarenko, Feoktistov, 9.75 points) is our 1st (9). 2nd A20 our 7th, 3rd A40 our 5th, 4th A58
  our 9th. Same picture as WCCI 8: in a compressed field of good problems only the outstanding one is a shared verdict.

## Disagreements and what they teach
1. **What the theme forces is not extra content.** Our 4th and 6th, A26 (Belchikov, Frigin: "textbook Hannelius + Dombrovskis, quiet
   key") and A06 (Einat, Navon: Hannelius + pseudo Le Grand), were 20th-27th. A threat returning as a mate after the refutation of its
   own try IS a Dombrovskis, and a refutation of an A-try met by B IS a Hannelius: the theme produces them. Serbia: the record set by
   the theme's examples (Kiss, three thematic variations with Dombrovskis) "was hard to match"; they paid for "genuine five-phase
   combinations" and for DIFFERENT refutations of the four tries, and cut repeated refutations. Score what goes beyond the scheme.
2. **The out-of-play key piece** (A55 = W10, our 2nd, 19th): Germany praised the blend of Dombrovskis, Hannelius, pseudo Le Grand and
   changed mates, then: "key piece unfortunately out of play". It is on E. Bourd's fatal list too; our judge noted the bishop "stands
   attacked" and missed that it is idle in the diagram.
3. **Static keys were not punished as hard as we punished them**: A04 (W23, our 21st, 5th-8th; three pairs of thematic tries, three
   threats returning) and A35 (W06, our last, 16th-18th). In a theme about tries, a rich try layer with a solution that only repeats set
   mates still scores; the theme lives in the tries.
