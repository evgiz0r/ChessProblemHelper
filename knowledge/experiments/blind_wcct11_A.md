# Blind judging experiment 12: WCCT 11, section A (#2), all entries (scored)

Source: wfcc.ch (WCCT 11 section A entries book + report with scores, downloaded 12 Oct 2026). An extractor agent built
86 FENs (keys verified; 80 scored, 6 excluded by the tourney); scores, ranks, countries sealed in /tmp/claude-0/sealed/wcct11a_key.json.
Eight blind `judge` agents (11 entries each) got FEN, the entry's published solution and the set theme:

> Theme: In a try (or tries) and the key a white unit (including a
> pawn) vacates a square which is then occupied in the variation play or in the refutation by at
> least two black units. The white thematic unit may be the same or there may be different
> white units in try (tries) and key. White’s mates may result from the occupation itself or
> from some other self-weakening by Black.

## Frozen ranking (committed before unsealing)
Merged by score; ties by each judge's own order. Groups were judged by different agents, so the scales differ a little.
```
K02 K17 K61 K70 K81 K01 K20 K25 K37 K54 K33 K56 K77 K85 K06 K14 K63 K69 K39 K18 K45 K27 K36 K80 K32 K35 K65 K72 K29 K59 K74 K76 K09 K38 K48 K53 K79 K04 K13 K82 K28 K34 K62 K67 K49 K03 K21 K55 K84 K07 K24 K42 K58 K11 K30 K64 K68 K73 K75 K22 K52 K05 K19 K40 K46 K31 K44 K51 K66 K08 K71 K41 K78 K83 K12 K86 K15 K23 K10 K26 K43 K50 K16 K57 K47 K60
```

## Scores by group (judge's order)
```
g0 K02 9|K01 8.5|K06 8|K09 6.5|K04 6|K03 5|K07 5|K11 5|K05 4.5|K08 4|K10 3
g1 K17 9|K20 8.5|K14 8|K18 7.5|K13 6|K21 5|K22 4.5|K19 4|K12 3|K15 3|K16 2.5
g2 K25 8|K33 8|K27 7|K32 7|K29 7|K28 6|K24 5|K30 5|K31 4|K23 3|K26 3
g3 K37 8|K39 7.5|K36 7|K35 7|K38 6.5|K34 6|K42 5|K40 4|K44 4|K41 3.5|K43 3
g4 K54 8|K45 7|K48 6|K53 6|K49 5|K55 5|K52 4.5|K46 4|K51 4|K50 2.5|K47 2
g5 K61 9|K56 8|K63 8|K65 7|K59 7|K62 6|K58 5|K64 5|K66 4|K57 2|K60 2
g6 K70 9|K77 8|K69 8|K72 7|K74 7|K76 7|K67 6|K68 5|K73 5|K75 5|K71 4
g7 K81 9|K85 8|K80 7|K79 6|K82 6|K84 5|K78 3|K83 3|K86 3
```

## Judges' notes (condensed)
- g0: K02 9 (d5 vacated, three occupiers refute three tries, white correction 4 phases; heavy 9+14); K01 8.5 (Zagoruiko 3x2,
  reciprocal change Sc5?/key, flight-giving key); K06 8 (theme on two squares, reciprocal change Qxc5/Qd5); K03/K07 5
  (bishop-vacates tasks, five/four occupiers, static); K11 5 (cycle of refutations but double threat everywhere).
- g1: K17 9 (Zagoruiko 4x2 on Se4/Be4, eight mates, 16 units); K20 8.5 (three occupiers of e4 refute three tries, changes);
  K14 8 (Zagoruiko 3x2); K18 7.5 (theme doubled through promotions, pseudo Le Grand).
- g2: K25 8 (knight wheel, B/R/P on d5 each refute a try, cycle, Laitinen, Umnov; flight in diagram); K33 8 (Grimshaw on vacated
  c4 in three phases, Zagoruiko 3x2); K27 7 (four occupiers of e6, static); K29 7 (six phases, capturing key).
- g3: K37 8 (Qd5/Sd5/Bd5 refute three knight tries, partial changes); K39 7.5 (four occupiers of e3, static); K36 7 (four
  checking battery tries each refuted by a different interposition on c5: task; checking capturing key); K35 7.
- g4: K54 8 (d5 triad, cycle of refutations, 8 of 9 mates differ, no double threat); K45 7 (same triad, 4x3 Zagoruiko, double
  threat in every phase); K48 6 (4x2 Zagoruiko, capturing key); K53 6 (white knight correction 3x2).
- g5: K61 9 (white correction, four occupiers of d5 refute random/corrections, Sd5 mated four ways); K56 8 (Grimshaw on vacated
  c3 + white correction + Mäkihovi, duals in one try); K63 8 (Zagoruiko 4x2 + cycle of defences/refutations); K65 7 (same scheme).
- g6: K70 9 (rook vacates b3: Sc5/Qd1/Rb7 refute three tries, Sb3 and Qb3 each mated three ways); K77 8 (four occupiers of e4,
  each try cuts a white line, static task); K69 8 (bishop white correction, three occupiers on d4).
- g7: K81 9; K85 8; K80 7 (see g7.md in the run directory).

## Unsealed: WCCT points (5 countries, max 10) against our blind score

| entry | WCCT code | place | points | our rank | our score | author |
|---|---|---|---|---|---|---|
| K17 | A59 | 1 | 9,6 | 2 | 9.0 | Marjan Kovačević |
| K63 | A04 | 2 | 9,4 | 17 | 8.0 | Mikola Chernyavsky |
| K45 | A01 | 3-4 | 9,0 | 21 | 7.0 | Zoltán Labai, Juraj Brabec, Peter Gvozdják, Ladislav Salai Jr |
| K81 | A76 | 3-4 | 9,0 | 5 | 9.0 | Zoran Gavrilovski |
| K02 | A11 | 5 | 8,7 | 1 | 9.0 | Dragan Stojnić |
| K03 | A35 | 6 | 8,0 | 46 | 5.0 | Kaj Engström, Indrek Aunver |
| K48 | A41 | 7 | 7,8 | 35 | 6.0 | Peter Gvozdják |
| K62 | A03 | 8-11 | 7,2 | 43 | 6.0 | Valery Kopyl, Vasil Krizhanivsky |
| K06 | A23 | 8-11 | 7,2 | 15 | 8.0 | Wolfgang Gäb |
| K11 | A53 | 8-11 | 7,2 | 54 | 5.0 | Michel Caillaud, Jean-Marc Loustau, Gérard Doukhan |
| K32 | A84 | 8-11 | 7,2 | 25 | 7.0 | Peter Gvozdják, Štefan Sovík, Ladislav Salai Jr, Emil Klemanič |
| K65 | A02 | 12-13 | 6,8 | 27 | 7.0 | Petro Novitsky, Mikola Chernyavsky |
| K07 | A67 | 12-13 | 6,8 | 50 | 5.0 | Stefan Parzuch |
| K53 | A29 | 14-17 | 6,6 | 36 | 6.0 | C.G.S. Narayanan |
| K14 | A42 | 14-17 | 6,6 | 16 | 8.0 | Miroslav Svítek |
| K35 | A49 | 14-17 | 6,6 | 26 | 7.0 | Zoran Gavrilovski |
| K61 | A75 | 14-17 | 6,6 | 3 | 9.0 | Dragan Stojnić |
| K37 | A17 | 18-20 | 6,4 | 9 | 8.0 | Dimitris Liakos |
| K58 | A73 | 18-20 | 6,4 | 53 | 5.0 | Klaus Baumann |
| K54 | A78 | 18-20 | 6,4 | 10 | 8.0 | Luis Gómez Palazón |
| K64 | A09 | 21-22 | 6,3 | 56 | 5.0 | C.G.S. Narayanan |
| K72 | A19 | 21-22 | 6,3 | 28 | 7.0 | Paz Einat |
| K59 | A16 | 23-27 | 6,2 | 30 | 7.0 | Ivo Tominić |
| K34 | A33 | 23-27 | 6,2 | 42 | 6.0 | Stefano Mariani |
| K52 | A38 | 23-27 | 6,2 | 61 | 4.5 | Kabe Moen |
| K56 | A50 | 23-27 | 6,2 | 12 | 8.0 | Jean-Marc Loustau, Gérard Doukhan |
| K74 | A83 | 23-27 | 6,2 | 31 | 7.0 | Henk Prins |
| K69 | A06 | 28-35 | 6,0 | 18 | 8.0 | C.G.S. Narayanan |
| K20 | A07 | 28-35 | 6,0 | 7 | 8.5 | Marco Guida |
| K19 | A20 | 28-35 | 6,0 | 63 | 4.0 | Michael Lipton |
| K39 | A36 | 28-35 | 6,0 | 19 | 7.5 | Cornel Pacurar |
| K38 | A44 | 28-35 | 6,0 | 34 | 6.5 | Jean-Marc Loustau, Gérard Doukhan |
| K36 | A54 | 28-35 | 6,0 | 23 | 7.0 | John Rice |
| K85 | A72 | 28-35 | 6,0 | 14 | 8.0 | John Rice |
| K76 | A79 | 28-35 | 6,0 | 32 | 7.0 | Imanol Zurutuza, Miguel Uris |
| K05 | A08 | 36 | 5,8 | 62 | 4.5 | Rainer Paslack |
| K09 | A05 | 37 | 5,7 | 33 | 6.5 | Mark Erenburg |
| K46 | A32 | 38-42 | 5,6 | 65 | 4.0 | Miroslav Svítek |
| K04 | A37 | 38-42 | 5,6 | 38 | 6.0 | Marek Drejak |
| K24 | A40 | 38-42 | 5,6 | 51 | 5.0 | Janne Syväniemi |
| K12 | A48 | 38-42 | 5,6 | 75 | 3.0 | Martin Hoffmann |
| K82 | A66 | 38-42 | 5,6 | 40 | 6.0 | Nikola Stolev, Zoran Gavrilovski |
| K80 | A25 | 43-45 | 5,4 | 24 | 7.0 | Kabe Moen |
| K50 | A34 | 43-45 | 5,4 | 82 | 2.5 | Jorge M. Kapros |
| K77 | A61 | 43-45 | 5,4 | 13 | 8.0 | Charles Ouellet |
| K44 | A43 | 46-48 | 5,2 | 67 | 4.0 | Suleyman Abdullayev |
| K27 | A68 | 46-48 | 5,2 | 22 | 7.0 | Ljubomir Ugren |
| K29 | A80 | 46-48 | 5,2 | 29 | 7.0 | Francesco Simoni |
| K66 | A21 | 49-52 | 5,0 | 69 | 4.0 | Andreas Schönholzer |
| K18 | A46 | 49-52 | 5,0 | 20 | 7.5 | Steffen Slumstrup Nielsen |
| K33 | A47 | 49-52 | 5,0 | 11 | 8.0 | Aleksandr Kryuchkov |
| K83 | A86 | 49-52 | 5,0 | 74 | 3.0 | Janne Syväniemi, Jorma Paavilainen |
| K25 | A10 | 53-56 | 4,8 | 8 | 8.0 | Miguel Uris |
| K13 | A14 | 53-56 | 4,8 | 39 | 6.0 | Charles Ouellet |
| K41 | A18 | 53-56 | 4,8 | 72 | 3.5 | Jorge J. Lois, Jorge M. Kapros |
| K42 | A55 | 53-56 | 4,8 | 52 | 5.0 | Aleksey Gasparyan |
| K49 | A15 | 57-62 | 4,6 | 45 | 5.0 | Kabe Moen |
| K73 | A39 | 57-62 | 4,6 | 58 | 5.0 | Antanas Vilkauskas |
| K08 | A52 | 57-62 | 4,6 | 70 | 4.0 | Suleyman Abdullayev |
| K30 | A56 | 57-62 | 4,6 | 55 | 5.0 | Miroslav Svítek |
| K86 | A58 | 57-62 | 4,6 | 76 | 3.0 | Aleksey Gasparyan |
| K47 | A85 | 57-62 | 4,6 | 85 | 2.0 | Andreas Schönholzer |
| K84 | A60 | 63 | 4,5 | 49 | 5.0 | Emanuel Navon |
| K43 | A70 | 64 | 4,4 | 81 | 3.0 | Ovidiu Crăciun |
| K40 | A27 | 65-68 | 4,2 | 64 | 4.0 | Bogusz Piliczewski |
| K68 | A51 | 65-68 | 4,2 | 57 | 5.0 | Tibor Érsek |
| K28 | A63 | 65-68 | 4,2 | 41 | 6.0 | Grigory Atayants |
| K16 | A81 | 65-68 | 4,2 | 83 | 2.5 | Ovidiu Crăciun |
| K75 | A13 | 69-70 | 4,0 | 59 | 5.0 | Bent Martin Muus, Steffen Slumstrup Nielsen |
| K78 | A82 | 69-70 | 4,0 | 73 | 3.0 | Antanas Vilkauskas |
| K57 | A65 | 71 | 3,8 | 84 | 2.0 | Tibor Érsek |
| K22 | A45 | 72-73 | 3,6 | 60 | 4.5 | Indrek Aunver |
| K60 | A57 | 72-73 | 3,6 | 86 | 2.0 | Gábor Tar |
| K10 | A26 | 74-75 | 3,4 | 79 | 3.0 | Henk le Grand |
| K15 | A71 | 74-75 | 3,4 | 77 | 3.0 | Dimitris Liakos |
| K31 | A62 | 76-77 | 3,2 | 66 | 4.0 | Janne Syväniemi |
| K67 | A74 | 76-77 | 3,2 | 44 | 6.0 | Antanas Vilkauskas |
| K26 | A28 | 78 | 3,0 | 80 | 3.0 | Rolf Uppström |
| K23 | A31 | 79 | 2,0 | 78 | 3.0 | Henk le Grand |
| K71 | A12 | None | 0,0 | 71 | 4.0 | - |
| K21 | A22 | no score (excluded) | - | 47 | 5.0 | - |
| K79 | A24 | no score (excluded) | - | 37 | 6.0 | - |
| K55 | A30 | no score (excluded) | - | 48 | 5.0 | - |
| K01 | A64 | no score (excluded) | - | 6 | 8.5 | - |
| K70 | A69 | no score (excluded) | - | 4 | 9.0 | - |
| K51 | A77 | no score (excluded) | - | 68 | 4.0 | - |
(K71 = A12 scored 0: the country sent A12 and A13 as versions, only the higher-graded counts. Six entries excluded by the
tourney, among them two of our top six, K70 and K01 (A64, which Serbia called one of the most original entries); the
reasons are not given in the report.)

## Agreement
- Spearman over the 79 scored entries: **0.63** (our blind score against the WCCT total).
- Against each judging country: GBR 0.47, IND 0.54, ISR 0.56, SRB 0.52, SVK 0.52. The countries among themselves: 0.34-0.72
  (mean about 0.54). **On a full world-level field, our blind panel ranks like a sixth judging country.**
- Top 10 overlap 5 of 10, top 20 overlap 11 of 20; AUC of the real top 11 against the rest: 0.76.
- 1st place K17 (A59, Kovačević, Zagoruiko 4x2): our 2nd. 3rd-4th K81 (A76): our 5th. 5th K02 (A11): our 1st.

## Disagreements and what they teach
1. **Double threats paid for by a record** (K45 = A01, 3rd-4th, our 21st; K11 = A53, 8th-11th, our 54th). Our judges called the
   double threat in every phase "close to fatal". The countries took it as "the price to pay for this record thematic
   achievement" (SRB: Zagoruiko 3x3 in four phases, 9 different mates, cyclic refutations); Israel "less bothered with the double
   threat" in A53. Third experiment in a row (Problemist 2014, WCCI 8, WCCT 11) where a double threat did not stop a top place.
   Our own composing rule stands (E. Bourd's fatal list), but as judges of others we over-punish it.
2. **Tasks again** (K03 = A35, 6th, 8.0 points, our 46th): a bishop on d4 with five black units refuting five tries on d4. Our judge:
   "mechanical task, static, key piece gives no mate". India and Serbia gave 3.0: "this specific arrangement was not shown before".
   Same miss as Problemist 2011 and the Problemesis tasks: a new arrangement of a task is placed.
3. **Zagoruiko 4x2 is the currency** of this tourney (Israel: "such a task cannot be ignored"); 1st and 2nd place are both 4x2
   (K17, K63). We put K63 at 17th: three thematic defences, Bc5 shared mate. Count the Zagoruiko size first.
4. **Where we were too generous, the reason was invisible originality or a flight**: K25 (A10, our 8th, 53rd-56th) has flight-taking
   tries and key and an idle bishop (Israel, Serbia); K33 (A47, our 11th, 49th-52nd) "the Grimshaw in the solution is well known"; the
   British judge called most entries "partially or almost wholly anticipated" (51 of 86 used the same wS idea, Serbia).
   Without a predecessor search we cannot see this; tools/blind_tourney.py-style fields would need an anticipation check
   (`tools/blog.py check` does one for our own problems) before scoring.
