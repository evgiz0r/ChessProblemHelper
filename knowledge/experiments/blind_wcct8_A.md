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
