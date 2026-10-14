# Blind judging experiment 15: WCCT 8, section A (#2), the problems printed with a diagram (scored)

Source: the 8th WCCT book (2005-2008, wfcc.ch). An extractor agent decoded the 28 section A diagrams (Type-3 chess font; all keys
verified unique); scores, places, countries sealed in /tmp/claude-0/sealed/wcct8a_key.json. Three blind `judge` agents got FEN,
published solution and the set theme, with the checklist as calibrated after WCCT 9. V21 was first called unsound by its judge
(two pawns dropped when copying the FEN); re-solved with the exact FEN it is sound, and the same judge re-scored it before freezing.

> A synthesis of black correction and change of function of white moves is required as follows:
> In the actual solution, a random and at least one correction move by the same black piece are answered by white mating
> moves. These white moves must appear as first move(s) and/or threat(s) in at least one try.

## Frozen ranking (committed before unsealing)
```
V06 V22 V23 V16 V27 V18 V08 V28 V14 V03 V09 V24 V12 V05 V17 V25 V02 V01 V21 V13 V15 V04 V26 V07 V19 V10 V11 V20
```

## Scores and notes by group (judge's order)

    g0 V06 9|V08 7.5|V03 7|V09 7|V05 6.5|V02 6|V01 6|V04 5.5|V07 5|V10 4.5|V11 4
    V06: random + 4 corrections, five mates each a try threat, one black rook refutes every try, queen-sacrifice key. V08: doubled key-mate reversal, heavy 14+4. V03: two overlapping correction systems, d3/d4 pair. V11: static key (all set).

    g1 V22 9|V16 8.5|V18 8|V14 7.5|V12 7|V17 6.5|V21 6|V13 6|V15 6|V19 5|V20 4
    V22: knight random + corrections doubled over four phases, Zagoruiko 4x6, pawn-pair reciprocal mates. V16: rook correction, Zagoruiko 3x2, sequence reversal, Feldman added. V18: rook random + 3 corrections + Rudenko system. V21 (re-judged after a FEN copy error): cyclic Rc4/Nf5/Nb3 on one rook, diagram flight, king refutation.

    g2 V23 8.5|V27 8|V28 7.5|V24 7|V25 6|V26 5
    V23: knight random + 3 corrections, each mate the threat of its own try, heavy, try-only pawns. V27: cyclic shift of refutations and mates between tries and solution, queen sacrifice key. V28: one black correction + white tertiary threat correction. V24: cyclic chain, economical.

## Unsealed: WCCT place (place points from the five countries' marks: HR, GB, RUS, SRB, SK) against our blind score

| entry | WCCT code | place | place points | marks | our rank | our score | author |
|---|---|---|---|---|---|---|---|
| V14 | A57 | 1 | 24 | HR 3 GB 3.5 RUS 3.5 SRB – SK 4- | 9 | 7.5 | Marjan Kovačević |
| V22 | A31 | 2 | 23 | HR 3 GB 3.5- RUS 3.5 SRB 2 SK – | 2 | 9 | Peter Gvozdják |
| V21 | A1 | 3 | 22 | HR 3 GB 2.5 RUS 3+ SRB 3+ SK 3+ | 19 | 6 | Philippe Robert, Michel Caillaud |
| V08 | A76 | 4 | 21 | HR 3 GB 3 RUS 3- SRB 2.5 SK – | 7 | 7.5 | Emil Klemanič, Štefan Sovík, Peter Gvozdják |
| V25 | A67 | 5 | - | HR 3.5 GB 2.5- RUS 3- SRB 2.5 SK – | 16 | 6 | Ľudovít Lačný, Juraj Brabec, Emil Klemanič, Peter Gvozdják |
| V04 | A50 | 6 | 20 | HR 4 GB 3+ RUS 2.5 SRB 1.5+ SK 3- | 22 | 5.5 | Daniel Papack |
| V24 | A65 | 7 | 19 | HR 3.5 GB 3+ RUS 2- SRB 2.5+ SK 2.5+ | 12 | 7 | Mikhail Khramtsevich, Nikolai Belchikov, Aleksandr Bulavka |
| V28 | A9 | 8 | 18 | HR 2.5 GB 3 RUS 2 SRB 3.5- SK 2.5- | 8 | 7.5 | Janez Nastran |
| V06 | A16 | 9 | 17 | HR 3.5 GB – RUS 2+ SRB 2.5- SK 2.5+ | 1 | 9 | John Rice |
| V07 | A14 | 10 | 16 | HR 3 GB 3+ RUS 2.5- SRB 2+ SK 2.5 | 24 | 5 | Mikhail Khramtsevich |
| V15 | A8 | 11 | 15 | HR 2.5 GB 3 RUS 2.5- SRB – SK 2+ | 21 | 6 | Dragan Stojnić |
| V27 | A23 | 12 | 14 | HR 3 GB 3.5 RUS 2.5 SRB 1.5- SK 2- | 5 | 8 | Rainer Paslack |
| V26 | A78 | 13 | 13 | HR 2.5 GB 2+ RUS 3 SRB 1.5+ SK 3- | 23 | 5 | Vasyl Dyachuk |
| V05 | A36 | 14 | 12 | HR 3 GB 2 RUS – SRB 2- SK 2.5- | 14 | 6.5 | Valery Shanshin, Anatoly Slesarenko |
| V09 | A18 | 15 | 11 | HR 2 GB 2- RUS 2.5+ SRB 3 SK 2+ | 11 | 7 | Viktor Melnichenko, Valentin Rudenko |
| V12 | A79 | 16 | 10 | HR 3.5 GB 2.5+ RUS 2.5 SRB 1.5- SK 1.5 | 13 | 7 | Jean-Marc Loustau |
| V18 | A59 | 17 | - | HR 2.5 GB 2.5- RUS 2.5- SRB 1.5 SK 2.5+ | 6 | 8 | Vasyl Dyachuk, Mark Basisty, Anatoly Vasilenko |
| V10 | A48 | 18 | - | HR 2.5 GB 2.5 RUS 2 SRB – SK 2 | 26 | 4.5 | Marjan Kovačević, Dragan Stojnić |
| V13 | A62 | 19 | 9 | HR 2.5 GB 2.5 RUS 2.5+ SRB 1.5- SK 2+ | 20 | 6 | Aharon Hirschenson, Paz Einat, Uri Avner |
| V03 | A73 | 20 | 8 | HR 2 GB 2.5- RUS 2.5 SRB 1.5+ SK 2.5- | 10 | 7 | Aharon Hirschenson |
| V02 | A55 | 21 | 7 | HR 2 GB 2.5- RUS 2- SRB 1.5 SK 2.5 | 17 | 6 | Nikola Stolev |
| V01 | A68 | 22 | 6 | HR 3 GB 3- RUS 1.5+ SRB 1 SK 1.5+ | 18 | 6 | Ricardo Vieira, Almiro Zarur |
| V23 | A2 | 23 | 5 | HR 3 GB 2.5 RUS 1.5 SRB 1+ SK 2- | 3 | 8.5 | Ion Murărașu |
| V17 | A34 | 24 | 4 | HR 3 GB 2 RUS 2- SRB 1.5- SK 1.5+ | 15 | 6.5 | Zoran Gavrilovski |
| V20 | A13 | 25 | 3 | HR 2.5 GB – RUS 2 SRB 1.5 SK 2- | 28 | 4 | John Rice, Christopher Reeves |
| V16 | A47 | 26 | 2 | HR 2 GB 2.5 RUS – SRB 0.5- SK 3- | 4 | 8.5 | Valery Shanshin |
| V11 | A33 | 27-28 | 0.5 | HR 3.5 GB 1.5 RUS 2 SRB 1.5 SK 1 | 27 | 4 | Alexander Zidek |
| V19 | A43 | 27-28 | 0.5 | HR 1.5 GB 3 RUS 1.5 SRB 2- SK 1.5+ | 25 | 5 | Aleksej Gasparjan |

## Agreement
- Spearman against the place: **0.30** (against the place points 0.32). Against each country: GB 0.25, SK 0.25, RUS 0.19, HR 0.08,
  SRB -0.01. **The countries among themselves: -0.01 to 0.52, mean 0.22**; each country against the other four: 0.06 to 0.32.
  As in WCCT 9, a field of the problems printed with a diagram gives a low agreement for everybody; we sit inside the countries' range.
- 2nd place A31 (Gvozdják, V22) our 2nd; 1st A57 (Kovačević, V14) our 9th; 3rd A1 (Robert, Caillaud, V21) our 19th; 4th A76 our 7th.

## Disagreements and what they teach
1. **Our WCCT 9 line overcorrected.** "Effects the theme produces by itself are the floor" was applied to a Zagoruiko, Dombrovskis and
   Hannelius that this theme does NOT force (black correction + change of function). The 1st place (V14: "an elegant, economical
   blending of the theme with Zagoruyko after the random and correction moves", GB) was our 9th; A67 (V25, 5th) our 16th, where our
   judge wrote "most of that comes with the theme itself". Only what the theme's wording logically entails is the floor; check it
   against the definition before discounting.
2. **A provided diagram flight and a try refuted by the king did not stop 3rd place** (V21, Banny-Zagoruiko 3x2 in zugzwang with
   doubled Salazar, our 19th). Russia named the "poor refutation of the first phase"; the others paid for the content. Our judge was
   also first misled by a FEN copy error (two pawns dropped): a judge must copy the FEN exactly, every time.
3. **A correction must be a real correction** (V16, Shanshin, our 4th, 26th): GB: "the first-rank cluster is a plain BR Grimshaw ...
   R and B can also move off the Grimshaw lines and commit an unguard error avoided, not corrected, by the Grimshaw moves. That isn't
   full-value correction"; Serbia: "artificially added variation do not improve the well known mechanism". A corrected move must
   commit a new error of its own; a move that merely avoids the random move's error is not black correction.
4. **Within the field, the better version shades the other** (V23, our 3rd, 23rd: "good content and key, but put into the shade by
   A16 [V06]. Unlike A16, the tries here are diffuse and lack unity"). Serbia also listed eight predecessors that "largely reduce
   marks for around 80% of the entries": anticipation again, which a blind panel without a search cannot see.
