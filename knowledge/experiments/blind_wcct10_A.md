# Blind judging experiment 13: WCCT 10, section A (#2), all entries (scored)

Source: wfcc.ch (WCCT 10 section A entries + final award, downloaded 12 Oct 2026). An extractor agent built 93 FENs (all
keys verified as unique; J01 needs Black's right to castle); scores, places, countries sealed in /tmp/claude-0/sealed/wcct10a_key.json.
Nine blind `judge` agents (11 entries each, 5 in the last) got FEN, the entry's published solution (composer's comments kept)
and the set theme. They used the checklist as calibrated after WCCT 11 (double threat paid for by record content, task
arrangements as content), so this run also tests that calibration.

> Section A (orthodox #2) set theme:
> Theme: Anticipatory unpin of a white piece. In the diagram position a white piece A is not pinned. The first move of a try and/or solution ensures that this white piece A is not pinned later, in order to provide a mate.

## Frozen ranking (committed before unsealing)
Merged by score; ties by each judge's own order.
```
J06 J21 J26 J46 J75 J78 J91 J35 J52 J60 J09 J19 J31 J71 J90 J45 J74 J55 J39 J80 J18 J82 J81 J66 J32 J43 J89 J13 J25 J40 J73 J17 J07 J16 J63 J05 J56 J23 J44 J48 J57 J76 J83 J30 J86 J22 J04 J36 J79 J92 J03 J51 J64 J69 J01 J27 J38 J65 J67 J08 J12 J34 J58 J84 J14 J15 J50 J10 J41 J87 J93 J28 J47 J68 J33 J61 J77 J02 J62 J54 J37 J20 J29 J49 J70 J88 J11 J59 J42 J24 J53 J72 J85
```

## Scores and notes by group (judge's order)

    g0 J06 9|J09 8|J07 6.5|J05 6|J04 5.5|J03 5|J01 5|J08 5|J10 4.5|J02 4|J11 3
    J06: Rd3 blocks c4-f1, Zagoruiko 3x2, double Dombrovskis, pseudo Le Grand, flight key. J09: Kxa3 leaves rank 4, Zagoruiko 3x2 + double Dombrovskis, capturing key. J03: three pin lines systematically in tries, no play after key.

    g1 J21 9|J19 8|J18 7.5|J13 7|J17 7|J16 6.5|J22 6|J12 5|J14 5|J15 5|J20 3.5
    J21: b6! blocks rank 6, Hannelius + doubled Dombrovskis + Zagoruiko over 6 phases. J19: e5! blocks rank 5, Zagoruiko 3x2 with Salazar reciprocity, flight key. J18/J16: same Kxc7 Hannelius scheme. J13: half-battery role reversal, heavy.

    g2 J26 9|J31 8|J32 7|J25 7|J23 6|J30 6|J27 5|J28 4|J33 4|J29 3|J24 2
    J26: Sg4! closes rank 4, Zagoruiko 3x2 with Le Grand, Mochalkin, Rudenko, Dombrovskis. J31: fourfold Fleck, four thematic variations, one try changes all four mates. J32: choice of which unpin to anticipate, three mates on Bxd5.

    g3 J35 8.5|J39 7.5|J43 7|J40 7|J44 6|J36 5.5|J38 5|J34 5|J41 4.5|J37 3.5|J42 2.5
    J35: king key out of one pin into another, reciprocal change Sfe4?/Kb4!. J39: Zagoruiko 3x2, heavy. J43: Hannelius, try threats return. J40: Le Grand + Dombrovskis, economical.

    g4 J46 9|J52 8.5|J45 8|J55 8|J48 6|J51 5|J50 4.5|J47 4|J54 3.5|J49 3|J53 2
    J46: theme in two phases unpinning different pieces, Zagoruiko 3x2 with set play. J52: king key leaves two pin lines, Kc8?/Kd8? each fail to the other. J45: doubled in key, Zagoruiko 3x2 + Dombrovskis. J55: white rook correction, economical. J53: theme not found.

    g5 J60 8|J66 7|J63 6|J56 6|J57 6|J64 5|J65 5|J58 5|J61 4|J62 4|J59 3
    J60: Bf7! closes the f-file, Hannelius-type return of try threats, changed mates. J66: Rf5! same pattern with 6 black units. J63: reciprocal change set/key, diagram flights. J59: theme barely present.

    g6 J75 9|J71 8|J74 8|J73 7|J76 6|J69 5|J67 5|J68 4|J77 4|J70 3|J72 2
    J75: choice of anticipatory unpin by Sc6, Zagoruiko 3x2, flight-giving key, 8+7. J71: multistage white correction, 3 changed mates. J74: Hannelius with Dombrovskis. J73: king leaves three pin lines, schematic, no change.

    g7 J78 9|J80 7.5|J82 7.5|J81 7.5|J83 6|J86 6|J79 5.5|J84 5|J87 4.5|J88 3|J85 2
    J78: two-phase anticipatory closing of rank 5, try refuted by the pin itself, Zagoruiko 3x2, flight key, 7+9. J80: Zagoruiko 3x2 + double Dombrovskis, corner-knight key. J82: double Dombrovskis, Rukhlis, heavy. J81: king key removes four pins, no tries.

    g8 J91 9|J90 8|J89 7|J92 5|J93 4
    J91: K key leaves three pin lines (triple secondary Dombrovskis), tries refuted by the pin each does not avoid. J90: b4 shuts rank 4, Zagoruiko 3x2 + Dombrovskis. J89: two-phase theme, heavy. J93: theme incidental.
