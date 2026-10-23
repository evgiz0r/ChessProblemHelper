# Sessions with Evgeni Bourd

## Session 1 (Sept 2026): Bristol
* Shown: Variantim 2015 #2635 (Bristol + tries). Evgeni's process: line and central king first, queen mates
  from the corners, simple defences d4/f2 to start, pick threat square (Qe5 over Qd4), close holes (d3 mates),
  then refine (heavier defences, tries on e5/f6/g7/h8, rotate board if pawns need it, check participation).
* Claude's attempt (Kf8 Qa1 Bb2 Sf4 Sh2 / Kh6 Bc8, 1.Bh8!) judged: king escape, king refutes both tries,
  same refutation twice; too simple for its flaws.
* Tool gains: Bristol detector, move identity fix, critique module (participation = guards king field /
  checks / pins; necessity by removal), knowledge file.
* Open: bPe6 in Evgeni's prototype appears unnecessary (asked). Pickabish definition to confirm.

## Session 2 (Sept 2026): White interference tries (blocking White bishops)
* Evgeni's sketch 3b4/6n1/N2R4/2RP1p2/3Pkp2/K3pN2/BB2P3/7r: key 1.Rc2! (2.Sc5#); 1.Rc4? cuts Ba2 (d5) 1...Se6!;
  1.Rc3? cuts Bb2 (d4) 1...Bb6!; rook must stay on c2-c4 to stop ...Rc1 (forcing mechanism).
  Evgeni's own verdict: defences uninteresting, mates unimpressive (guard/unguard), key rook without role.
* Lessons recorded in lessons.jsonl (construction limits, square choice, meaningful guards, shifting the
  board for space, forcing mechanisms, content, participation of the key piece, exploring material changes).
* Tool gains: knowledge API (themes/principles/lessons, free-text theme lookup, record_lesson), motives
  (why each defence defends / why each mate works), Grimshaw detector (finds Variantim 2015 d6 Grimshaw),
  interference tries judged against the solution's answers, critique: thematic vs mechanism refutations,
  guard/unguard content, varied motives.
* Open directions from Evgeni: one queen instead of two bishops; flight-giving tactics; give the key rook a mating role.

## Session 3 (Sept 2026): option 1, one queen instead of two bishops
* Geometry: only Qb3 keeps two cut lines through c4/c3 (d5 by diagonal, d3 by rank). Thematic tries survive:
  1.Rc4? (cuts Q from d5) 1...Se6!; 1.Rc3? (cuts Q from d3) 1...Bb6!.
* Cooks from queen power (Qc2#, Qd3#) closed with bBb1 + bSf2; then 1.Rc2 fails to 1...Bb6! 2.Sg5+ Kxd4:
  the queen cannot also guard d4 (Bb2's job). Repairs tried: wSb5 (new threat Sc3, cooks), wKc3 (no solution).
* Status: open. Needs a structural change around d4 (Evgeni's judgement requested).

## Session 3b: Novice Composers TT 2002, 5th Place (yacpdb 2753), sight test
* Claude solved blind first: key 1.Bxf5! (2.Qe4#), 1...Qxf5 2.Qc4#, 1...Sxd7 2.Se6#, 1...Qxc6+ 2.Sxc6#; missed
  1...Qd6 2.Qd3# (queen interposes on the d-file pin, unpinning d5, and self-pins the knight); wrongly gave
  set 1...Q~ 2.Bc4# (not even check; the real mate is 2.Bxe5#).
* Tool gains: half-pin detector, unpin / cross-check / capture-of-guard motives. Critique still calls wPc6 a
  cook-stopper although it is the bait for the cross-check variation (a 'bait' role to add).
* Evgeni: the pawn pin plays only in one thematic variation (confirmed: d5 pin decides only 2.Qc4#).
* Improvement ranking: (1) quiet key instead of the obvious capture, (2) uniform use of the pin, (3) change
  dimension (1...Qd6 unprovided in the diagram), (4) 2+2 balance of half-pin defences. All 16 units are
  necessary (tight). Quiet-key search (bishop start squares x one Black unit anywhere): no solution; bPf5 is
  multi-functional (guards e4 vs Qe4#, stops Se6+), removing it gives 8 keys.

## Session 4: adding content to the 2002 half-pin (E. Bourd's key-search method)
* New tool compose/key_candidates.py: from a FIXED post-key position, enumerate keys as "one White unit
  relocated" (modes: arrive / park), report tries and whether refutations are thematic.
* Evgeni's idea tested: wSd6 blocks Rd7, so dxe4 holds; the knight's departure creates the pin and the
  threat Qe4#. Raw mechanism gives FOUR moves that all work (Sb7/Sc8/Se8/Sf7) = try material.
* Adding bBg8 leaves a unique key 1.Sf7! with four tries, but three share the refutation 1...Sxd7!
  (mechanism, not theme) and the key allows a dual after 1...Sxd7 (Se6#/Qd3#). Not yet good enough.
* Claude error this session: used a post-key FEN without Se5 (first searches returned nothing).

## Session 5: scheme-first half-pin with dual avoidance
* New technique: compose/scheme_search.py. score_core/analyse_core test a POST-KEY position (mate in 1 after
  every Black reply), ~4000 candidates/s, so exhaustive enumeration of cores is possible. Holes tolerated.
* Random hill-climbing again failed to build coordinated dual avoidance; exhaustive core enumeration found:
      wKb5 wBh8 wRc6 wQg3 wBb1 / bKd4 bRf6 bBe5      (Black to move, post-key)
      threat 2.Qd3#;  1...Rf3 2.Qxe5#;  1...Bd6 2.Rxd6#
  Both mates need Bh8 (pin used) and each fails after the other defence: genuine half-pin dual avoidance.
  Holes to close: Bb8, Bc7, Bf4, Bxg3, Kd5. wBb1 is not yet doing anything.
* Next: close the holes, then look for a key (compose/key_candidates), then thematic tries.
* Evgeni corrected the pin test: 2.Qxe5# captures the pinned unit and only needs Bh8 as a guard -> not
  thematic. New tests: pin_exploited() (pinned unit could capture the mating unit or interpose if free) and
  avoidance_reason() (the 'additional effect'; 'king escapes' scores as weak).
* With the strict test: bRf6+bBe5 gives 0 cores, bQf6+bSe5 gives 166. Best core (8 units, 6 holes):
      wKb5 wBh8 wRa8 wRe3 wQc1 / bKd4 bQf6 bSe5   (Black to move, post-key)
      threat 2.Qc5#
      1...Qd6 (Q leaves the line, Se5 pinned)  2.Qd2#  - pinned Se5 cannot interpose on d3
      1...Sd3 (S leaves the line, Qf6 pinned)  2.Rd8#  - pinned Qf6 cannot capture on d8
  Avoidance: after 1...Sd3 the knight blocks d3 so Qd2 gives no check; after 1...Qd6 the freed queen
  captures on d8 / interposes. Both effects are real, not king flights.

## Session 6: Evgeni's own solution (sound, verified)
* 8/7B/1NP1p1rr/5n2/1Q1pk3/4P2R/1K2P2B/8  #2 (9+6): key 1.Qc4! (2.Qd3#); 1...Rg3 2.Qxd4#; 1...Sg3 2.Qxe6#.
  Thematic tries 1.Qb3? (commands only e6) refuted by 1...Rg3!, 1.Qd2? (only d4) refuted by 1...Sg3!.
  Incidental tries 1.Qd6? 1.Qc5? (different threats).
* Half-pin h7-g6-f5-e4 (bRg6 + bSf5, pinner Bh7). BOTH mates exploit the pin by capture prevention:
  pinned Sf5 cannot take on d4; pinned Rg6 cannot take on e6. This is the purity we were searching for -
  and the defences are unified (same square g3, both non-capturing, both blocking Bh2 for a flight).
* Tool gains: critique now separates tries carrying the KEY's threat (thematic set) from tries with a
  different threat, so 'same refutation' is measured inside the thematic set only.
* Verified flaw: wPc6 is superfluous (removing it leaves key and all four tries unchanged).
* Dual-avoidance motive marked explicitly (new motives.dual_avoidance / format_dual_avoidance):
      1...Rg3 2.Qxd4#  (2.Qxe6+? Rxe6!)      capture by the freed rook
      1...Sg3 2.Qxe6#  (2.Qxd4+? Kf5!)       king flight to the square the knight vacated
  (Evgeni guessed Ke5; the actual flight is Kf5 - after 1...Sg3 the pinned Rg6 blocks its own pinner Bh7
  from guarding f5.) Reasons differ -> second-layer unity missing, now reported by critique and rewarded
  in scheme_search scoring (+12 when both avoidance kinds match).
* Same test on the 2002 problem: reasons also differ (capture / king flight).

## Session 7: purer dual-avoidance motives (two post-key schemes from Evgeni)
* 8/3nRR2/3Qr1p1/1p2b3/2p1k1B1/1N2p1B1/4P3/1K6 (post-key, Black to move; threat Bf3#; NO holes):
  three Black units to f6 - 1...Sf6 2.Sc5#, 1...Rf6 2.Qd4#, 1...Bf6 2.Qc6# - each sibling mate refuted by
  the DEFENDER ITSELF retaining the line it held (Sf6 interposes d5; Rf6 keeps rank 6 -> Rxc6; Bf6 keeps the
  diagonal -> Bxd4). Unified.
* 2N5/8/K1p4p/1pk2N2/R2n3r/1P2n2p/7Q/4r1BB (post-key; threat Qd6#; one hole: Rf4):
  1...Sdxf5 2.Qe5# (2.Qc2? Rc4!) / 1...Sexf5 2.Qc2# (2.Qe5? Rxe5!) - each knight capture OPENS a line for a
  Black rook, which refutes the other mate. Unified.
* Tool gains: motives.dual_avoidance_after works from a diagram (with a key/try) or straight from a post-key
  position, and classifies the motive - defender retains control / line opened by the defence / another unit /
  king flight / no check - ranking the thematic reason and reporting unity. Both new motives filed as themes.
* Claude errors: treated the two FENs as diagrams (they are post-key positions), and pushed a null move on a
  Black-to-move board, which flipped the side to move.

## Session 8: black half-battery of two PAWNS (task from Evgeni)
* Evgeni's constraint: impossible on a diagonal (the rear pawn's guard square lies ON the pin line, so a mate
  there blocks its own pinner). Only same row or column work. Filed as a definition.
* Derived: on a FILE (Rd8 / bPd6 / bPd5 / bKd4) neither pawn can advance, so both defences are captures
  (automatic unity); the squares c4/e4/c5/e5 are both bait and mate squares, so they must be assigned
  crosswise; each bait must be essential to the threat; the mating unit arrives beside the king and so must
  be guarded.
* Best core found (prefiltered exhaustive search, 470k positions):
      wKh1 wQc2 wRd8 wRc1 wBd2 wSe4 wSe5 / bKd4 bPd6 bPd5     (Black to move)
      1...dxe5 2.Qc4#  (2.Qc5+? Kxe4!)      pinned Pd5 cannot capture on c4
      1...dxe4 2.Qc5#  (2.Qc4+? Kxe5!)      pinned Pd6 cannot capture on c5
  Both mates exploit the pin; avoidance unified but of the WEAK kind (king flight).
  Flaws: threat is a dual (Sc6#/Sf3#) and one hole (Kxe5). Patch search over one added White unit +
  one Black pawn found no version with a unique threat and no holes. Key search: no candidates yet.

## Session 9: two more pawn half-battery structures + the motif map
* 8/3K2bb/1p6/1p1kppR1/1P6/2PPQ3/8/8 (rank half-battery, pinner Rg5, pawns e5/f5, bKd5): pure structure -
  1...f4 2.Qd4# (2.Qe4? Bxe4!) / 1...e4 2.Qxe4# (2.Qd4? Bxd4!). Each pawn ADVANCE opens a diagonal for a
  black bishop behind (Bh7->e4, Bg7->d4) = unified line-opening avoidance, and both mates still exploit the
  pin. Correction to session 8: pawn defences must be captures only on a FILE, not on a rank.
* 3R4/2b2p2/2bp4/2Np4/1BPk1P2/1P3P2/Kn2Q3/8 (file half-battery, baits c5/c4, mates e4/e5): valid post-key
  position (threat Qf2#, no holes). ALSO unified by line opening - the pair to the rank structure:
      1...dxc5 2.Qe4#  (2.Qe5? Bxe5!)   the d6 pawn's departure opens Bc7's diagonal
      1...dxc4 2.Qe5#  (2.Qe4? Bxe4!)   the d5 pawn's departure opens Bc6's diagonal
  Claude first reported this as mixed (king flight) because the tool kept the first legal escape (Kd3)
  instead of the thematic one; fixed - every escape is now classified and the most thematic kept.
* New tool compose/motif_space.py: classifies each thematic variation as
  (how the unit leaves the line | how the pin is exploited | why the sibling mate fails) and keeps a
  catalogue in knowledge/motifs.json. 5 of 30 cells filled by everything seen so far; gaps() lists the rest
  as candidate mechanisms to build - a systematic answer to "how do I look for new motivations".

## Session 10: completing the file pawn half-battery into a problem
* Post-key cleaned: replacing bSb2 by bSf1 removes the 1...Sd1 dual and makes the threat unique (Qd3#).
* Key found with compose/key_candidates (arrive mode): the White knight comes from d7.
      3R4/2bN1p2/2bp4/3p4/1BPk1P2/1P3P2/K3Q3/5n2   #2 (9+7)
      1.Se5? (2.Qd3#) but 1...dxc4!     the knight blocks its own mating square e5
      1.Sc5! (2.Qd3#)
        1...dxc5 2.Qe4#  (2.Qe5? Bxe5!)
        1...dxc4 2.Qe5#  (2.Qe4? Bxe4!)
  Key is a knight sacrifice to the thematic pawn; unified line-opening avoidance preserved.
* Tool fixes: dual_avoidance_after now excludes moves answered by the threat; piece_necessity judges
  CONTENT (duals, lost variations, degraded avoidance motive) rather than bare soundness - it had wrongly
  called the thematic bishop c7 superfluous.

## Session 11: Evgeni's extended file half-battery (b2R4/b6p/8/N2pPQ2/2Npp2R/1pPk3P/1Pp5/2n2KB1)
* 1.Qf4! (2.Qd2#): 1...dxc4 2.Qe3# (2.Qxe4? Bxe4!), 1...dxc3 2.Qxe4# (2.Qe3? Bxe3!), 1...e3 2.Qf5#
  (2.Qxe3? dxe3!). Unified line-opening avoidance across THREE variations; f4 is the only square commanding
  d2/e3/e4/f5; tries 1.Qg5? 1.Qf2? carry the threat but cannot reach e4.
* Features Claude missed, pointed out by Evgeni and now detected by the tool:
  - the mate 2.Qf5# is a SWITCHBACK (the key piece returns to its diagram square);
  - the key UNPINS bPe4 (pinned by Qf5 against Kd3), and that unpin creates the third variation.
* Evgeni's judgement: extra variations are a necessary evil but fine here because one ends in a switchback;
  the key is slightly weak (the queen is out of play) but redeemed by the unpin; the tries prove the half-pin
  and justify the heavier position; dual avoidance simple but unified. Overall "not too complex but decent".
* Correction (Evgeni): 1...e3 is NOT thematic - Pe4 is not one of the half-pinned units (those are Pd5/Pd4).
  It is extra play that happens to be pretty. Tool now finds half-batteries geometrically
  (motives.find_half_batteries), marks non-half-battery variations as extra play, and measures
  dual-avoidance unity over the thematic defences only.

## Session 12: task - key by the White king opening a line, two tries closing other White lines
* Skeleton designed: wRc8 guards c5/c4/c3 but is blocked by wKc6; any king move off the c-file opens it.
  King destinations b5/b6/b7/d6/d7 are the candidate keys; those landing on another White line are the tries.
* Searches run (tens of thousands of positions, with short-mate rejection and full uniqueness):
  - bare black king: every try refuted by the flight 1...Ke5!, key merely guards a flight. Wrong mechanism.
  - black pawns added to cut flights: found positions with a unique king key where the other destinations do
    cut White lines (e.g. 2R5/8/2K5/3p4/3kp3/1Q5B/8/8, 1.Kd6! 2.Qc3#, 1...e3 2.Qxd5#), but the cuts are not
    what refutes the tries, and the content is thin (one variation).
* NOT achieved. Derived spec for the next attempt: the position needs two thematic defences d1,d2 with
  distinct mates m1,m2 that depend on different White lines L1,L2; then a king destination cutting L1 is
  refuted by d1 and one cutting L2 by d2. Same shape as Evgeni's session-2 sketch (1.Rc2! with Rc4?/Rc3?
  cutting Ba2/Bb2), but with the king as the key piece.
* Second round of searches (post-key-first, three-way spec, and 'refutation lands on a square the cut line
  guarded'): 0 hits in ~150k positions over six geometries. Diagnosis: two added White pieces cannot make
  the cut lines load-bearing. Next attempt needs a richer mating net built first - hand-sketched or searched
  with 3-4 added White pieces and a stronger prefilter.

## Session 13: Evgeni's solution to the king-key task
  b5BQ/8/4pK1B/1N6/1p2P3/1P1krpN1/1R6/8   #2 (9+6)
  1.Ke7! (2.Qd4#)  - the king leaves the h8-a1 diagonal, opening it for the queen
     1...Rxe4 2.Rd2#   the rook's departure opens Bh6's diagonal to e3
     1...e5   2.Bc4#   the pawn's advance opens Bg8's diagonal to c4
  1.Kg5? closes Bh6 (not open yet!) - 1...Rxe4!
  1.Kf7? closes Bg8 (not open yet!) - 1...e5!
  1.Kg6? closes nothing - 1...Bxe4+!
* The double paradox: each try commits a self-interference on a line that is still blocked by the very
  Black unit whose defence would open it, so the cost appears only one move later.
* Evgeni's order of work: lines and king moves first, then the mates, then extend so the defences open the
  White lines. Content deepened by motivation, not by more variations.
* Tool gain: motives.anticipatory_closing detects both flavours (a supporting line cut, and the mating
  piece's own path cut) and reports whether the closing is anticipatory.
* Earlier, simpler version: 2N5/4p3/1R6/npk5/b5P1/2P1NK2/2P4B/5B1Q #2 - 1.Kf2! (2.Qd5#), 1...Bb3 2.Rxb5#,
  1...e6 2.Bd6#; 1.Kg3? cuts Bh2's own path to d6, 1.Ke2? cuts Bf1's line to c4. Both ordinary shut-offs -
  the detector correctly reports anticipatory=False here and True in the final version.
* Evgeni's h4 idea (a third line pointing at c4) tested: adding Rh4 gives extra king tries but no thematic
  one, because Bf1 already guards c4. Candidates for the needed third defence (black knight f4/f5, bishop
  g6/g5/g7) all either kill the threat by guarding d5 or refute the key incidentally. Confirms his
  "not so easy to set up that extra defense".

## Session 14: three-try version (rotated setting)
  3b4/4p1R1/1PP1kN2/6P1/2N3Pn/B1K2p1n/4P3/QB1R4   #2 (13+6)
  1.Kb3! (2.Qe5#)  1...Bc7 2.Rxe7#   1...Sg6 2.Bf5#   1...exf6 2.Rd6#
  1.Kb4? closes Ba3 (guard of d6/e7) - 1...Bc7!
  1.Kd2? closes Rd1's own path       - 1...exf6!
  1.Kc2? closes Bb1's own path       - 1...Sg6!
  Three tries, each cutting a different White line, each refuted differently; key cuts nothing.
  Here the closings are ORDINARY (the lines are open in the diagram) - the detector reports anticipatory=False,
  distinguishing this version from the two-try double-paradox one.
* Evgeni's construction notes: rotate the board to make room for the third defence; give Black a universal
  resource (bSh3 hitting g5, so 1...Sxg5 unguards f6) so that slow White alternatives all fail and the
  intended threat is forced.
* Tool fix: piece_necessity now counts TRIES as content - wPb6 looked superfluous (sound without it) but its
  removal kills the tries 1.Kb4? and 1.Kd2?.

## Session 15: task - king key opening a line, tries that SELF-PIN a White piece
* Scheme from Evgeni: 8/7B/8/5K2/3N4/4k3/r7/b2Q4 - 1.Ke5? Ra3! and the knight is pinned by Ba1 (verified:
  Ke5 and Kf6 both self-pin Sd4). The scheme itself has no solution; it illustrates the mechanism.
* NOT achieved. Searches: 102k rigid positions (no unique king key at all - stage counter showed 0),
  a two-mechanism skeleton (bBa1+wSc3, bRf8+wSf5) with 0 hits, and a hill climb that drifted to two queens.
* New tool compose/pin_geometry.py: for a given White king square it enumerates every
  (destination, pinned White unit, pinner square) triple, and plan() reports which destinations pin which
  unit and which pin nothing (candidate keys). Finding: with White units on the usual squares around the
  king, nearly every destination completes SOME pin - the scarce resource is a CLEAN destination for the key.
* Evgeni's realisation (session 15):
      1B1R3Q/4p1K1/6p1/1p1Npp2/R1b1kpN1/4P3/3bP1r1/6qB   #2 (10+11)
      1.Kf8! (2.Qxe5#)   - the king leaves g7, opening h8-a1 for the queen; pins nothing
         1...Bc3 2.Sxc3#      1...Qa1 2.Sf2#
      1.Kg8? / 1.Kf7?  self-pin Sd5 (Bc4 on c4-d5-e6-f7-g8)  - 1...Bc3!
      1.Kxg6?          self-pins Sg4 (Rg2 on the g-file)     - 1...Qa1!
  Two pin lines, two pinned knights, each mate denied by its own pin; the key square is the clean one.
* His method: build the lines, decide which White units can be self-pinned, THEN find mates and the
  defences that make those mates necessary.
* Tool gain: motives.self_pin_tries detects the mechanism and reports whether the key pins nothing;
  wired into the critique.

## Session 16: changed mates (2Rn1N2/7K/3P4/3k4/pB1p1P2/3n1P2/1p1Q1p2/8)
* Evgeni built it as set play + solution and asked for a try+solution version. The tries are already there:
      1.Qc3? (2.Qc4#) but 1...dxc3!
      1.Qe2? (2.Qe4#)  1...Sc6 2.Qe6#   1...Sxb4 2.Qe5#   but 1...Sc5!
      1.Qc2! (2.Qc4#)  1...Sc6 2.Qxc6#  1...Sxb4 2.Qc5#
  Two mates change between try and key, plus a changed threat (Qe4# -> Qc4#).
* Remaining flaw: duals after 1...Se5 (Qc5#/Qe4#) and 1...Sxf4 (Qf5#/Qc5#/Qe4#).
* Attempts to remove them all failed (single additions, single relocations, permanent blockers on d3,
  removing wPf4, blocking e5). Reason: Qe4 must be reachable from e2 (the try's threat) but not from c2,
  and both go through d3 - the very square the defending knight vacates. A black blocker on d3 captures the
  queen; a white one kills the defences or cooks.
* Set+solution version (Evgeni's suggestion, built by Claude): queen placed on e2 in the DIAGRAM, and two
  Black pawns added on f5 and g6:
      2Rn1N2/7K/3P2p1/3k1p2/pB1p1P2/3n1P2/1p2Qp2/8   #2 (8+9)
      set:  1...Sc6 2.Qe6#    1...Sxb4 2.Qe5#
      1.Qc2! (2.Qc4#)  1...Sc6 2.Qxc6#   1...Sxb4 2.Qc5#
  The post-key play is now DUAL-FREE (all five variations unique) - the fix that was impossible in the
  try version. Key: bPf5 guards e4, so Qe4 is neither an immediate mate (cook) nor a dual; in the try
  version Qe4 had to remain available as the try's threat, which is why the same fix could not be applied.
  Remaining flaws: set-play duals (1...Se5, 1...Se1/Sc1), 17 units, and three of the five variations
  ending on Qc5#.

## Session 17: second changed-mates problem
  b3r3/2pQ2p1/4n1P1/1R6/4k1P1/2K1P2R/8/4n3   #2 (7+7)
  set:  1...Sd4 2.Qxd4#   1...Sf3 2.Qd3#
  1.Qf7! (2.Qf5#)   1...Sd4 2.Qf4#   1...Sf3 2.Qxf3#   (+ 1...Rf8 2.Qxe6#)
  The queen switches from the d-file to the f-file - a clean geometric change, dual-free in the post-key play.
  Evgeni's construction: one defence unguards a flight (forcing White's reply), one is a direct defence,
  extra pawns block Black's other moves; the setting was rotated to enforce a single thematic defence.
* Tool fixes: necessity now counts SET PLAY as content (wPg6 exists only so that 1...g6 is provided), and the
  dual-avoidance line no longer says "0 thematic defences" when there is no half-battery.

## Session 18: same-piece changed mates (task set by Evgeni; his solution verified)
* Task: a simple #2 with changed mates where the SAME Black unit makes both thematic defences (his sessions 16
  and 17 used two different knights).
* Claude's attempt: a whole-diagram search (set play + quiet key + changed mates, holes tolerated, then a beam
  hole-closer, then the full solver). Four skeleton families, ~5M positions. Found geometries but nothing sound:
      bKd5 bSc6 (guards d4 and e5) wRe4: every set mate on d4, every solution mate on e5;
      8/8/2n2B2/1K1k4/1Q2R3/8/8/8: reciprocal change 1...Se5 2.Rxe5 / 1...Sd4 2.Qxd4 -> Qxe5 / Rxd4 after 1.Qe7,
      but the key square is attacked by the knight and 1...Sa7+ has no answer.
  Two hand completions were cooked (mates in 1 the solver saw and Claude did not); a third became a complete
  block that every waiting move solves. Recorded as a negative result in lessons.jsonl.
* Evgeni's solution:
      8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8   #2 (9+5)
      1.Bxb4? (2.Qg6#)  1...Sd4 2.Sbc3#   1...Se3 2.Sdc3#   but 1...e6! (closes the 6th rank)
      1.Bxe7! (2.Qg6#)  1...Sd4 2.Sd6#    1...Se3 2.Sf6#
  His order: (1) the squares and the effect that creates several mates at once - here the c2 knight's self-blocks
  on d4/e3, each of which lets EITHER White knight mate; (2) the differentiation - the mating squares are guarded
  by Black pawns and each bishop capture removes one guard, so each phase allows one pair; (3) then a threat and
  cleaning. The flight the defence unguards picks the knight (2.Sf6+? Ke3!, 2.Sd6+? Kd4! - unified dual
  avoidance), the phase picks the square. His own verdict: play somewhat natural, not an ideal problem, but the
  required theme.
* Critique (tool): capture key; wBd6 plays only the key; wKh7 passive; 14 units. Extra phases 1.Qa7?/1.Qb6?
  (zugzwang, 1...Se3 2.Qxe3#) refuted by 1...Sd4!.
* Tool gain: compose/changed_mates_search.py (the whole-diagram evaluator and beam hole-closer), kept with its
  negative result documented.

## Session 19: two different units defend on the same square, mates changed
* Evgeni's lessons: mating squares and lines must be close to the king; a fast start is two units CAPTURING a
  White unit on the same square (8/3n4/8/3kP3/8/4r3/8/8) or a Grimshaw near the king; then arrange the mates,
  then the differentiation, then a threat those defences parry.
* Claude's searches (Grimshaw families near d5, then his capture scheme with Q/R/S/P enumerations, ~4M
  positions) found no sound skeleton; the recurring cost is covering the king's field for a queen mate on the
  other side of the self-block. Hand line: 1...Rxe5 2.Qd3# by line opening was reached, the Sxe5 side was not.
* Evgeni's solution:
      1K3b2/1P1p1B2/3r2p1/Q3P1RN/R1n1k2p/3p1p2/4nP2/4Nb2   #2 (10+11)
      1.e6? (2.Qe5#)  1...Rd4 2.Bxg6#  1...Sd4 2.Rg4#  1...Rxe6 2.Qd5#   but 1...Bg7!
      1.Qd2! (2.Qe3#) 1...Rd4 2.Sf6#   1...Sd4 2.Qf4#  1...Re6 2.Qxd3#  (1...Kd4 2.Rxc4#)
  Technical details verified: Sc4 pinned by Ra4 (only Se2 reaches d4; Sxd2 impossible; Kd4 met by Rxc4#);
  Bxg6 fails after the key because the bishop leaving f7 abandons d5 once the queen has left a5; Rg4 fails after
  the key because f5/e5 are no longer held (in the try the e6 pawn holds f5, the queen e5); Sf6 fails in the try
  because f4 is open (Qd2 covers it in the solution); bPg6 and bPh4 each removable alone, not together.
* Tool gains: critique counts lost changed-mate relations as content and marks a try-playing unit thematic
  (wPe5 was 'cook-stopper', bPg6 'not needed').
* Smaller task from Evgeni: ONE knight move, ONE changed mate, set vs solution, from 8/8/8/5n2/3Pk3/8/8/8.
  Search (wK, wQ, one unit around his three units; criterion: a specific knight move with a mate no other knight
  move gets) -> 85 hits; best skeleton wKd2 wQg5 wRd3 wPd4: set 1...Sxd4 2.Re3#, 1.Qf6! (2.Qe5#) 1...Sxd4 2.Rxd4#.
  Beam closer -> sound:
      5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3   #2 (7+3)   1.Qf6! (2.Qe5#) 1...Sxd4 2.Rxd4#, 1...Kd5 2.Qe6#
      set 1...Sxd4 2.Re3#;  1.Qh5? 1...Sxd4 2.Rg4# but 1...Kd5!
  Flaws: d5 an unprovided flight in the diagram (inherent: the queen must stand behind the knight on the 5th rank,
  any other cover of d5 gives Qg4# in 1 or a Re3 dual after the key), a try refuted by the king, Rg8/Sf8/Se1 only
  for soundness. Boards now rendered as SVG for Evgeni instead of ASCII.
* Evgeni's one-knight version 8/2K2p2/6pB/3p1nQ1/3Pk1P1/2P5/4P3/5r2: boxed king, 1.Qf6! 1...Sxd4 2.Qxd4# (set 2.Qe3#).
  Lessons: never build around a king with a flight; the moved key piece just gives the other mate; reuse ideas and
  the search process, not structures (rotate, reflect, manipulate, respect the constraints).
* Bishop version (task): with a no-flights filter in the evaluator the same enumeration gave sound miniatures directly:
      7b/8/3K4/8/3Pk3/2Q5/8/5R2   #2 (4+2)   set 1...Bxd4 2.Qf3#;  1.Kc5! (2.Qf3#) 1...Bxd4+ 2.Qxd4#
  King key protecting d4. Flaws: one defence, the defence checks, Bg7/Bf6/Be5+ unprovided.
* Evgeni: an unprovided CHECK in the set play is a fatal flaw -> the 6-unit miniature (1...Be5+) is rejected; rule
  added to the evaluator (rejects) and the critique (major). Rerun with no flights + no unprovided checks:
      7n/6b1/1Np5/R7/3Pk1K1/2Q5/8/8   #2 (5+4)   set 1...Bxd4 2.Qf3#;  1.Ra4! (2.Qf3#) 1...Bxd4 2.Qxd4#
      tries 1.Rf5? Sg6!  1.Rd5? cxd5!  1.Ra3? Bxd4!
  Quiet defence, no flights, no unprovided checks; four unprovided quiet moves in the set. Closer bug found: cook
  count was capped, so a 12-key position looked like a 2-key one; fixed (exact count up to 20).
* Task: changed mates with two Black units self-pinning (8/3r4/8/8/1R1Pk3/8/8/6b1, Rxd4/Bxd4 pinned by Rb4).
  NOT achieved this round. Findings: (a) with the bishop on g1 (guards e3) no White placement with Q+K+2 units
  gives both captures a changed mate (p1/p2: ~3M positions, 0 hits); (b) moving the bishop to g7 makes it guard e5
  THROUGH its capture square, so the pinned bishop's "attack" on e5 and the pinned rook's on d5 are both
  exploitable: 63 placements give distinct set mates for both captures, the best being knight mates
  4N3/3r2b1/8/1Q6/1R1Pk3/4P3/4K3/8 (1...Rxd4 2.Sd6#, 1...Bxd4 2.Sf6#); (c) no key changes both: the new mates
  Qd5/Qe5 need d5 AND e5 protected, no single key square protects both, and any static protector of e5 makes
  Qe5 a set dual. The key must switch the set mates OFF (remove a guard they need) while switching the new
  mates ON - a two-effect key not yet found.
* Evgeni's own setting for the self-pin task: 3rN2b/1p5b/8/2Q5/1R1Pk1P1/4P3/4K3/8 - set Rxd4 2.Sd6#, Bxd4 2.Sf6#;
  1.Sc7! (2.Qc2#) Rxd4 2.Qd5#, Bxd4 2.Qe7# (interposition on e5 impossible for the pinned bishop); 1.Qh5 meant
  as a try showing the set mates. Solver: COOKED by 1.d5+ (discovered check, Rb4 protects d4 for the queen) and by
  1.Qh5 itself (2.Qh1# unstoppable). Two-unit repairs (g4/e3 changes + one Black unit) found none. The evaluator
  accepts his position under every filter, so the miss was the material budget (one pawn slot, no Black plugs)
  and a wrong hand assumption (new mates must be adjacent and protected) - recorded in lessons.
* Evgeni's sound version: 3rN2b/7b/8/n1Q5/1R1Pk1P1/4P3/4K3/8 - the knight a5 refutes 1.d5+ AND 1.Sc7 (1...Sc4!),
  so the phases are inverted: 1.Sc7? shows Qd5#/Qe7#, the key 1.Qh5! (2.Qh1#) shows Sd6#/Sf6#. I had found the
  a5 knight and rejected it because it refuted Sc7 - the missing intuition is 'a resource that refutes the cook and
  the key makes the key a try'. Recorded as lessons. Process feedback from Evgeni: iterate at the composer's level
  (cause -> remedy -> verify), not by launching an enumeration per micro-question.
* Task: self-pin mates with two Black rooks (scheme 8/7B/8/r4N2/4k3/8/8/5r2), single solution first. Built by
  hand in five solver passes (no enumeration): 8/7B/p6K/r4N2/1N1Pk3/2P4P/6PQ/5r2 - 1.Qg3! (2.Sd6#/Qe3#)
  1...Raxf5 2.Qe5#, 1...Rfxf5 2.Qf3#, each pinned rook still 'guarding' the mating square, the other rook's
  real guard as dual avoidance. What was lacking each step: a check-proof king (rooks reach everything ->
  blockers + a6 plug), a plug that kept the rook's thematic line, protectors without lines to the king, a
  protector that does not capture with mate. Still open: the double threat (Qe3 protected by the front knight)
  and the gxf3 dual.
* Evgeni's two-rook version 8/3Rp1K1/6B1/1r3N1R/2N1k2P/1p4B1/2b1P3/1n2Qrq1: try 1.Qc3? (Qe5#/Qf3#) refuted by
  1...e5!, key 1.Qd2! (Qd5#/Qf4#) - both self-pin mates changed by the queen post; threat by the Bg6/Sf5 battery.
  Solver: sound; thematic dual after 1...Rbxf5 (Qd5#/Rxe7#, the d7 rook mating on the e-file for the same pin
  reason) - Rd7->d8 removes it with nothing else changed; also Qd4+ Rxd4/Qxd4, 18 units.

## Session 20: composing on the bench, and what the journal showed

* Tooling: the Composing Bench artifact (board with place/move/remove, rotate, mirror, shift, undo, FEN load,
  pre-key solving via `analysis.js`, post-key solving with threat/holes, journal to the artifact db). Evgeni
  composed on it for three sittings; the journal (383 steps, 90 solves, no typed notes) was read back with
  `read_db` and condensed. The journal now has a "story only" filter (solves, notes, transforms) and collapsed
  solve lines, because the raw list was too verbose to review.
* His task: self-pin mates by two Black units capturing on one square, changed between set and solution.
  What he reported as the hard part: a REASON why the thematic captures are defences.
* Sitting 1 (17:49, 2 min): the scheme from our task, 8/3r4/8/R4N2/1R1Pk1P1/6P1/K3P3/3N2b1; post-key: double
  threat Re5#/Sc3#.
* Sitting 2 (17:53-18:38, 206 steps): same scheme with Rc4/Rb4 pinning, queen on b5/c1/a5, then a rotation
  (18:01), a shift, a second double rotation (18:10) and two more rotations (18:27, 18:28) - the structure was
  turned around looking for a threat the captures would stop. Every post-key solve gave a threat with one or two
  holes or "no threat"; the two pre-key solves (18:07, 18:37) found only checking tries and no key. A 16-minute
  stretch (18:10-18:26) of placements without a single solve produced nothing. Ended at
  b3R3/K5b1/B5p1/6Q1/3kN2R/1PN5/3B1n2/4r3 (threat Qc5#, hole Sxe4), abandoned.
* Sitting 3 (19:26-19:59, 164 steps): board CLEARED and rebuilt from the idea: bKd4, wPe4 as the capture
  square, bRe8 on the file, a Black bishop/rook on the a8 diagonal, wRh4 pinning the rank, knights a5/c5, Ka1.
  Queen tried on g3 (double threat Qe3/Qc3), a2 (Qc4#), e2 (double threat Qd3/Qd1 with Kf6), then knight
  threats Sab3/Scb3 - each solve showed a double threat or holes, none gave the captures a reason. 19:49: the
  a8 rook became a QUEEN, the White king went to e1 with a Black pawn e2 and knight d1 in front; 19:56: Rg5 and
  Qh2 removed, Qh5 placed (set mates Qe5#/Qd5#), moved to e2: post-key threat Qd3# and the captures on e4 now
  PIN the queen against Ke1 while self-pinning against Rh4 - the reason found. Then pre-key: 1.fxe8=S cook
  (f7 pawn removed), Qf3/Qxe2 double key (Bh1 added: 1.Qf3? Bxf3!), Sf2 dual Qxf2 (h3 -> g3).
* Result (E. Bourd): q3r3/8/3B4/N1N4Q/p1PkPR1r/6p1/3Pp3/3nK2b - set 1...Rxe4 2.Qe5#, 1...Qxe4 2.Qd5#;
  1.Qf3? (2.Qd3#) Bxf3!; 1.Qxe2! (2.Qd3#) 1...Rxe4 2.Se6#, 1...Qxe4 2.Sc6#. Sound. Capture key, 18 units;
  the solver's necessity check shows bRh4 and the Rf4 shift unnecessary: q3r3/8/3B4/N1N4Q/p1PkP2R/6p1/3Pp3/3nK2b
  (17 units) has the same play. Recorded as bourd-queen-pin-selfpin.
* Critique change: a White king anchoring a pin that a defence creates is now reported as 'thematic king'
  (with the pinning defences) instead of 'passive king'.

## Session 21: two captures on one square, three phases (Evgeni on the bench)

* Three more bench sittings after session 20. Sept 13, 20:13-20:46 (203 steps, 40 solves) and 21:33-22:06
  (211 steps, 36 solves): the two-captures idea with a Black queen and bishop on the same White knight, rotated
  eight times in all, ending both times in zugzwang positions with 20-27 holes and no threat. Sept 14,
  22:10-22:31 (182 steps, 43 solves): finished.
* Result: KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n - set Qxe5 2.Bg6#, Bxe5 2.Sg5#; 1.Qxh1? (2.Qf3#)
  Qxe5 2.Bh3#, Bxe5 2.Qf1# but g2!; 1.Qg2! (2.Qf3#) Qxe5 2.Bh3#, Bxe5 2.Sxg3#. Sound. Bxe5 mated three ways
  over three phases, Qxe5 two ways; both captures open a battery for the other's mate, so dual avoidance is
  unified (no check: the other line is still closed). Flaws: 22 units, 10 pawns, d5/e6 pure cook-stoppers,
  Ka8 idle, six-fold bishop duals after Qxe5 in the non-thematic tries. Recorded as
  bourd-two-captures-three-phase.
* Bug he found: the dual-avoidance line "2.Sxg3? Sxg3! another unit captures the mating unit" after 1...Qxe5.
  Sxg3 gives no check there (Bd4 still closes Rc4-f4), so no Black move is the reason. All three classifiers
  (Python _avoid_kind, dual_avoidance, JS dualAvoidance) tested the capture branch before the check test;
  now no-check comes first and the closed battery with its blocker is named. Regression test added.
* Bench: refresh button (new journal session, board emptied, earlier sessions hidden behind a toggle),
  story-only journal by default, solve lines lead with the cook/key verdict.

## Session 22: a corner key, solution only (Claude)

* Task from Evgeni: something simple, solution only, key to a corner. Chosen mechanism: Bristol clearance
  along a8-h1 with the queen following to g2, the bishop keeping g2 protected from h1.
* Kernel Q7/KB6/6N1/8/8/8/7k/8 is already sound (1.Bh1! 2.Qg2#; 1.Ba6? Kg1!). From there: box the king
  in the diagram (Se2 for g1/g3, Sf2 for h1/h3), then the cooks of a corner queen (a-file, 8th rank, first
  rank, long diagonal) and the reason interpositions are hard to answer (they cut the queen's protection of
  h1). Dead ends kept as lessons: a first-rank rook protecting h1 mates on h1 in one; a g4 pawn guarding h3
  blocks the 4th-rank rook mate; every non-pawn interposer can step back onto the b8-h2 diagonal against Qb8.
* First result Q1K5/1B6/8/8/3n1p1p/8/4NN1k/4N3 #2 (6+4) REJECTED by Evgeni: three white knights, a promoted piece is fatal. Corrected: Q1K5/1B6/8/8/5p1p/R1n5/4NN1k/8 #2 (6+4) - 1.Bh1! (2.Qg2#) Sd5/Se4 2.Rh3#, h3 2.Sg4#, f3 2.Qb8#; the a3 rook replaces the e1 knight (blocks the a-file, mates on h3 when the c3 knight interposes) and the black knight moved from d4 to c3. Earlier result, for the record: (6+4) - 1.Bh1! (2.Qg2#) Sc6 2.Sf3#, Sf3 2.Sxf3#, h3 2.Sg4#,
  f3 2.Qb8#. No flights in the diagram, no duals, one try of note (1.Bg2? Sxe2!). Flaws: Kc8 passive, three
  knights, f3 mated twice on the same square. Recorded as claude-bristol-corner.
* Tooling: corner/bristol_search.py in the scratchpad (kernel + n units, prefilter 'the key still forces
  mate', then full solve); 60k positions in ~4 minutes for one White plus one Black unit.

## Session 23: three underpromotion keys (Claude)

* Task from Evgeni: a #2 with an underpromotion solution; three problems covering all underpromotions.
* Chosen reason, common to all three: after the wrong promotion Black is stalemated. Knight:
  8/4P3/4bB2/6K1/1N2k3/8/4P1N1/8 - 1.e8=S! B~ 2.Sd6# (Q/R pin the e6 bishop, B has no mate). Bishop:
  K7/4P3/5PN1/4b3/2P1k1P1/5N2/4PP2/8 - 1.e8=B! (2.Bc6#) (Q/R pin the e5 bishop, S has no mate: f6 blocked
  and d6 guarded by the bishop's diagonal). Rook: 8/4P3/8/5P2/4N2k/5P2/6P1/K7 - 1.e8=R! Kh5 2.Rh8# (Q/B
  cover h5 and stalemate, S lets the king out to h6 after Kh5). All sound, 8, 11 and 7 units, all thin.
* Dead ends kept as lessons: the check-avoidance route (king on the promotion file) fails because the
  hole the knight mate fills is a flight the quiet key cannot answer; pinned bishops self-block the knight's
  mating squares with duals; pinned knights self-block the bishop's mating squares; a boxed king turns every
  protected adjacent check into a mate in one.
* Enumeration: one/two-unit additions around each kernel (about 150k positions) found no version with a
  second variation - the stalemate motivation leaves Black nothing to move.

* Session 24 addition: bishop promotion by flight, not pin: 8/2K1P3/3P4/3kP3/7R/3N4/8/5R2 - 1.e8=B! Ke6 2.Bf7# (Q/R stalemate by covering e6 on the file; S has no mate after Ke6). 8 units. First draft cooked six ways (Sf4# in one, checks followed by e8=Q#); fixed by choosing box units that cannot check d5. Recorded as claude-underpromotion-B-flight.

* Session 24, from Evgeni: bourd-four-promotions (all four promotions of the d-pawn as tries/key). Judging principle recorded: flaws are weighed against content; a tripled theme carries flaws that would be fatal in a simple problem. Solver fix: zugzwang and stalemating tries are now shown (they were hidden on the bench).

* Session 24: Evgeni's four-unit 1.d8=B! (7K/3P1k2/3Q4/8/8/8/8/8, bourd-minimal-bishop-promotion) checked exhaustively with chesscomp.compose.minimal: 2.67M placements, 29 unique bishop-promotion keys, 11 with the flight variation, all queen-based, none with another extra unit. Lessons on his shrink-to-minimum method and on turning a cook between two promotions into a tripled theme are in lessons.jsonl and the compose skill.

* Session 24: minimal forms confirmed by enumeration: rook 3 units, bishop 4, knight 4 (Evgeni's prediction). Positions recorded as minimal-rook-promotion, minimal-knight-promotion, minimal-knight-promotion-rook.

## Session 25: a key that gives two flights (Claude, on Evgeni's scheme)

* Task: "compose a problem where the key gives 2 flights", then "use the scheme on my board now, Se4
  will give two flights" - his bench board held bK d5, bP e5, wS c5 and nothing else.
* Before his scheme: two-flight searches in the abstract (bK e4, a bishop or queen leaving the a7-g1
  diagonal so d4 and e3 open, up to three added units, about 10M positions in 20 minutes of four cores)
  found nothing. His three units with the key move named reached a sound position in one sitting.
* Result: 2R2B1b/8/4P1bN/2Nkp3/p4p2/2Q5/3K4/8 #2 (7+6). 1.Se4! (2.Qc4#) 1...Kxe6 2.Qc6#, 1...Kxe4 2.Qd3#.
  Tries 1.Sd7?/1.Sa6? give the same flights and mates but fail to 1...Bd3!. Recorded as
  claude-two-flight-knight-sacrifice. Thin (no non-king defence), 13 units; every unit necessary, no pair
  removable (checked).
* How it was found, in order: the mates first (Qc6 needs the c-file, so the knight's departure unmasks it;
  Qd3 needs d3 guarded in the diagram by bBg6 THROUGH e4, so the key closes the line and the capturing
  king closes it again); then the threat Qc4 with the rook's protection of c4 masked by the knight; then
  four cooks, each with a cause: Qb3+ Kd4 Qd3# (bPa4), any f-file rook checking on the d-file (no rook;
  Sh6 for f5/f7), Sd7 with Qxe5# (bBh8 protects e5), and Se6 - the one other knight move that covers d4,
  so Qc6 became a second threat and Kxe6 walked into the same Qc6#. Fixed by occupying e6 with a white
  pawn the king can capture: the cook-stopper became the second flight. Lessons in lessons.jsonl.
* Searches were used for placement only (one or two units around a fixed kernel, 300-420 s budgets, four
  jobs); around the final kernel three added units found no lighter setting.
* Compose-alone test: the lean agent (45 tool calls, 20 minutes, notes file) was stopped by the watchdog at
  20 minutes having made 22 tool calls and 16 solves. It had chosen a two-flight key on its own and reached
  a sound but thin 9-unit position (Q3b3/8/4p3/1P6/3k4/3N4/1N1K2P1/8, both flights met by the threat), and
  was enumerating around it when stopped. Recorded as claude-alone-two-flight-thin. Skill change: at the
  15-minute mark the agent writes its best sound position as the result instead of starting a search.

## Session 26: a black knight correction, built in Evgeni's order (Claude)

* His recipe: decide the threat; a defence by a knight moving away (a line opening makes any move a
  defence); then a correction adding a plus and a minus (guarding or capturing a piece that creates a
  self-block is the easiest).
* Result: b3N3/8/ppn1p3/4k3/3R2P1/4P3/7K/2Q5 #2 (6+6). 1.Qc4! (2.Re4#) S~ 2.Qc7#, Sxd4 2.Qxd4#; try
  1.Qc2? (2.Qe4#) S~ 2.Qc7# but Sxd4!. The random move opens a8-e4 for the bishop (defence) and the
  c-file for the queen (error); the correction captures the rook that covered e4 and is captured with
  mate. Recorded as claude-knight-correction. Flaws: the correction is a capture, not a self-block; the
  four queen tries share the refutation Sxd4; thin (one correction, no other defence).
* Method note: a knight cannot re-guard the square it left (parity), so knight corrections are captures,
  interpositions or arrivals whose loss a mate exploits. Three mechanism searches (8M positions) found
  nothing; the hand sequence with the solver reading set play at each step took about fourteen solves.
  Dead ends and unit roles in themes/references/black_correction.md and lessons.jsonl.

## Session 27: adjacent-knight self-block correction (Claude, not finished)

* Task: "one more correction problem", knight adjacent to the king, the correction a self-block (not a
  capture), the random move an unguard or line opening. Started with bK e5, bS d6, wPd3 so that 1...Se4
  self-blocks for d4# (the pawn gave up e4, the knight fills it).
* No sound position yet. About thirty hand-built settings were solved, each cooked or unsound; the
  causes were recorded as rules (lessons.jsonl 2026-09-22, themes/references/black_correction.md).
  The big ones: every knight destination attacks d6, so a line through d6 is interposed by every
  move; the only mating line no far move touches is h2-e5, parried by e4/f5 guarding g3; a d-file rook
  that enables d4/d5 after the knight leaves gives Bd4#/Rd5# for free; a 6th-rank rook gives Re6#;
  once every flight is covered the queen may not have a single check; the defence line (Ba3-e7) and
  the random-mate line (f8-c5) cannot share the a3-f8 diagonal.
* Two mechanism searches around the fixed core (900 s, four jobs, ~1.8M positions) found nothing.
  The hand sequence again did better at finding causes than the search did at finding positions.
* Next step proposed to Evgeni: enable the random mate by an unguard (the knight on d6 guards c4 and
  f7, both knight-mate squares) or start from the other cell (knight on d5, self-blocks on f4/f6).
  Scratch notes: scratchpad corr/selfblock_notes.md and corr/why.py (lists black replies and mates
  after a given key, faster than reading the full report when a threat problem has no solution).
* Review while he composed: four diagrams (cell; Bg3# with e4/f5 guarding g3; the d-file rook duals;
  the shared a3-f8 diagonal) were what made the argument land ("finally got somewhere"). Principle
  recorded in bourd_principles.md: a board per idea, arrows for the moves that matter.
* His own attempt on the bench (session mucy12up, about 320 journal steps in 45 minutes): bK c4,
  bS b5 adjacent; the knight's departure GIVES the king b5 (that is why every knight move defends
  against Qf7#), the error is leaving the b-file (Qb3#); corrections Sxd4 (guards b3, self-block d4,
  Se5#) and Sc3 (cuts Rh3-b3, self-block c3, Se3#). B4BK1/1Q2R3/2N5/PnP5/2kP4/b6R/2rpP3/3N4, key
  1.Re8! (2.Qf7#). Trim scan: the a8 bishop is removable and taking it out also removes the
  Kd5 dual (Qf7#/Se3# becomes Se3# alone): 5BK1/1Q2R3/2N5/PnP5/2kP4/b6R/2rpP3/3N4 (11+5).
  Left: three tries refuted by 1...Kd5 (his own rule), wPa5 a pure cook-stopper.
* FINAL (his verdict: "the result is good, the complex thematic play is strong"):
  BQ2R3/3K4/2N5/1np2p2/2k2P2/p4R1b/4P3/3Nb3 #2 (9+7), recorded as bourd-knight-double-correction.
  1.Re7! (2.Qg8#) S~ 2.Qb3#, Sd4 2.Se5#, Sc3 2.Se3#; tries Rh8? Kd5!, Re5? Sd4!, Ree3? Sc3!. His
  reading: White has no true random move; Rh8 is the nearest and loses e4; the aggressive corrections
  Re5/Ree3 are refuted by the opponent's corrections (a mirror); Re7 is the correction without a
  negative effect; the black knight then plays the same random-plus-correction. Doubling the theme
  from both sides is "somewhat exponential in terms of chess". Moving the rook from e6 to e8 saved
  the c7 pawn and removed four same-refutation tries. Principles: start small and keep the mechanism
  light so it can be extended; draw the diagrams.
* Second scheme the same evening (bench session mud7dke1, ~300 steps): bK c4, bS c5 next to the king
  on the file. 4Q1B1/b3K3/p2B1p2/PPnP3b/2kN1p2/8/1R1R4/1N6 #2 (11+7): 1.Sf5! (2.Rd4#, the knight
  opens the d-file). Any knight move opens a7-d4 for the black bishop (defence) and d6-b4 for the white
  bishop (error): 2.Rb4#. Corrections Sd3 (blocks d3, attacks b4) 2.Rdc2#, Sb3 (blocks b3, covers d4)
  2.Rbc2#: two rooks mating on one square, the choice made by the blocked flight. Tries Se6? (cuts
  Bg8-d5) Sd3!, Sc6? (cuts Qe8-b5) Sb3!, Sf3? Bxf3, Se2? Bxe2: the white knight's posts refuted by the
  black corrections again. Checks: wPf4 stops a second threat Se3# (not removable); wPa5 is set-play
  filler and comes off (17 units, same play); b5 stops Qa4+/Sb5; d5 exists for legality (Bg8).

## Session 28: the report marks random moves, corrections and promoted force (Claude, for Evgeni)

* His ask, on a 3-knight sketch (8/KB3Q2/N2k4/3p4/pP1N4/4nN1b/3B2p1/2r3b1): mark in the solution the
  random moves and the corrections, counting as a correction only a move that stops the random move's
  mate (Sf1/Sd1 random, Sg4/Sc4 corrections; Sf5/Sc2 keep Bf4# so they are random moves with a
  dual); and flag a promoted piece, fatal and easy to see (three white knights).
* Done in chesscomp (analysis.corrections per phase, report line "S~ random ... ; corrections ...",
  core.promoted_force, critique major finding), in docs/analysis.js (same rule, exported), and in the
  bench page (pre-key header line; post-key "Random moves and corrections" block; the journal's solve
  line keeps PROMOTED and the S~ lines). Two regression tests; 44 pass. Bench republished.
* He asked for an online problem database searchable by our themes. Nothing reachable from this
  environment: yacpdb.org, pdb.dieschwalbe.de, meson.co.uk, kotesovec.cz, phenix-echecs.fr,
  selivanov.world (Problemesis mirror) and christian.poisson.free.fr are all denied by the network
  policy; general web search works. Plan once the hosts are allowed: a `search-db` skill using
  YACPDB's predicate language (Keyword/Stip/Text with AND, OR, NOT), then re-solve hits with our solver
  so the report marks random moves and corrections. Problemesis (Poisson) is a PDF archive to crawl.
* "The solution is way too verbose": added a compact solution form, now the bench default (a "full
  report" checkbox restores everything). Verdict first (cooks, promoted force, unprovided checks), the
  key with its threat, the play grouped per piece as random move | corrections, duals on one line,
  "(n other moves allow the threat)", one line per try with its refutation, and the set play only as
  "differs: Se7 Sa5#->Qc5#" or "same mates". Python: `--compact`; JS: formatCompact/phaseCompact.
* "Find me a key" on 5b2/2N5/p7/5n2/K1kPp2p/1Np4q/2P5/3Q4 (cooked by Sa5#): my one- and two-change
  search (about 1,700 solves) and his hand reached the same wPa5 fix; he was faster. A one-unit
  cook-stopper is a hand job: name the cook's reason (Qd1 protects d4, Sc7 holds d5) and block the
  mating square. Search earns its keep only when the fix must also keep several variations intact.
  Left: Sd6 2.Qd5#/Qc5# is structural (Sd6 cuts f8-c5 like Se7 but does not guard d5).
* He then rebuilt the sketch: knight f4 and bishop d4 instead of pawn d4 and knight f6, black knight
  b1 to stop the second key 1.Be3 (c2! interposes on c3 after Qxc2+), pawn a6 kept to guard b5.
  Result 5b2/8/p7/P4n2/K1kBpN1p/1Np4q/8/1n1Q4 #2 (6+9): 1.Qh5! (2.Qf7#) S~ 2.Qd5#, Se7 2.Qc5#, Se3
  2.Qe2#; dual Sd6 2.Qd5#/Qc5#; try 1.Be3? c2!; set 1...Sxd4 2.Qxd4# changes to Qd5#. His view: the
  position is airier, the key takes the queen from an active post to an ambush behind the knight and
  the queen still plays every white move; no tries, no changes, but the raw play is good for the size.
  My reading of the mechanism: the knight's departure unmasks Qh3-e6 (why every knight move defends)
  and opens h5-d5 (the random mate); each correction closes another black line (f8-c5, h3-d3). The
  Sd6 dual is the twin of Se7 on the a3-f8 diagonal; strict one- and two-unit searches around the
  position found nothing, so it stays unless the scheme changes. The bench journal now keeps the
  "[duals]" line in its solve summary, so a dual is visible in the timeline too.
* He rebuilt the scheme once more, and this one is finished: bishop e7 (so d6 is the only interference
  square on the diagonal), rook d8 guarding d5 so that 1...Sd6 cuts a white line and a black line at
  once and Qd5 stops working, black pawn c5 and bishop a3 (his replacement for my Pa3+Pb4) to answer
  1...Sxd4 2.Rxd4+ with cxd4. 3R4/4b3/K7/1Np2n2/2kPp2p/B1p4q/2P5/3Q4 #2 (7+8): 1.Qh5! (2.Qf7#) S~
  2.Qd5#, Sd6 2.Qxc5#, Se3 2.Qe2#, no duals, every unit load-bearing. Recorded as
  `bourd-knight-ambush-correction`. The strict two-change search and his hand found the same repair
  (Pb4+pc5) within a minute of each other; he then improved it by hand.
* His reservation on the finished form: Sd6 (two line cuts) is much stronger than Se3 (one), and in
  a symmetrical theme the thematic variations should be roughly equal in effect. Recorded as a
  principle in bourd_principles.md and as a lesson.
* The Problemesis database from the other session (PR #1, merged) is now on this branch too. First use:
  20 of his own problems are in it; by label, 25 black-correction and 7 Bristol twomovers, one with both
  (Loustau, Phénix 1999, 2nd Prize: 4th-degree white bishop correction with anti-Bristol). A solver run
  over all 815 orthodox twomovers (`python -m chesscomp.db run themes --stip '#2' --orthodox --no-twins
  --jobs 4`, 90 seconds, run file `knowledge/runs/themes-2m.jsonl`) found 54 key-phase corrections, 12
  by a knight, and no Bristol by our detector (the labelled ones are clearances the detector does not
  see: worth a look). Closest to his work: Pilchenko & Shavyrin 2001 (adjacent knight b5 beside Kc4,
  Sd4 2.Se5#), noted on his session-27 problem; Kapros 2002 (queen tries refuted by knight corrections,
  1.Qh5!), the mirror idea he described in session 27.
* "Did you solve all the problems?" Yes: all 815 orthodox untwinned twomovers, 90 seconds on four
  processes, twice (`themes` and `check` runs, both committed under knowledge/runs/). Check against the
  published keys: 789 agree, 1 mismatch (a castling key the FEN cannot express), 13 "cooked" that are
  nearly all intentional multi-solution problems (his own Qa1/Qa2/Qa3/Qa4 among them; Zolotarev 1996
  looks like a real cook or a misparsed diagram), 5 "unsound" that are parsing or fairy cases (castling,
  a blind-rook fairy piece), 7 without a printed key. The FEN has no castling or en-passant rights, so
  keys of that kind are invisible to the solver.
* "Show me some Dombrovskis examples ... add a solution near those problems, in a clean format": four
  cards (diagram, author and source, tries with A/B and a/b letters, key, themes) for Slesarenko &
  Gvozdjak 1999, Veliky & Dyachuk 2003, Keller & Zirkwitz 2000 and his own Problemesis 2004 twomover.
  The renderer is now `tools/card_png.py` (spec on stdin, or `--id` for a database record with its
  printed solution). The themes run was rerun after a bug (patterns live under `relations`): by play
  the solver sees Dombrovskis in 202 twomovers against 88 labelled (77 in both), Bristol in 12 against
  7 labelled (4 in both). The solver-only Dombrovskis hits are mostly single-defence paradoxes the
  magazine did not think worth naming.
* "Can you try to compose a Dombrovskis, one variation": five hand kernels around bKd5/bPe6 with a queen on
  the e-file all died to mates in one (a boxed king makes every protected check a mate). Rebuilt with
  Slesarenko's trick (queen as the sole guard of e4 and e5, king key covering e6) and let a new search,
  `chesscomp.compose.pattern_search`, add the last two units with the solver's own Dombrovskis detector
  as the judge: 14 hits in seven minutes, lightest 6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1 (6+3): 1.Sf3? (2.Qd3#)
  e5!; 1.Kf7! (2.Qxe6#) e5 2.Qd3#. Recorded as `claude-dombrovskis-one` with its flaws (one variation,
  two tries one refutation, try-only knight, tempo pawn). Judged before showing.
* His own Dombrovskis sketch on the bench (session mulzjgkr, five minutes, 38 steps, 3 solves, 3 notes):
  bKd5, wPe5, bPd6, the capture dxe5 as the paradox defence; a try that guards e5 but unguards d6
  (Be7-f6, threat Sb6#) so dxe5 refutes by the d6 flight; a key that controls d6 so the same capture
  self-blocks e5 and allows the mate. His notes: doubling with a second capturable guard near the king;
  "impure" if the mate after dxe5 already exists in the set play, the paradox then lives only in the
  tries; therefore the key itself should take control of d6. Stopped at 8/4B3/3p4/1P1kP3/1PN5/8/8/3K4
  with no key yet (e4, e6, c4 still open after the capture).
* "What do you think, any ideas" on his dxe5 sketch: two searches around it (bare and with guards) found
  no key in two added units, so the missing part is structural. Twelve hand versions later, a sound
  skeleton: 2b4R/3p4/3p4/3kPP2/BP1p2NB/3P4/8/6K1 (9+5), 1.Rh6! (2.Rxd6#, protected only by e5) dxe5
  2.Bb3#; tries 1.Rxc8? (2.Bb3#) dxe5!, 1.Bg3?/1.Re8? (2.Sf6#) dxe5!. The Dombrovskis on dxe5 goes
  through the capturing try only, because no quiet move can newly cover c6 (knight symmetry, light
  bishop hits d5, rook on the 6th hits d6). Recorded as lessons; not recorded as a problem.
* His Dombrovskis, two more sittings (Sept 29 evening, 470 steps, and Sept 30, 39 steps; 147 solves, 28
  cooked, 7 no-solution reports): 7b/4K2b/3N1p2/n3Np2/1PpkPBp1/6R1/BP6/8 #2 (9+8), 1.Bxc4! (2.Rd3#)
  fxe4 2.Sb5#, Sc6+ 2.Sxc6#; tries 1.Re3? and 1.Bb1? (2.Sb5#) fxe4! The paradox defence is a capture
  that removes a white guard: the e4 pawn holds d5, so fxe4 opens d5 and Sb5+ meets Kd5 in the tries;
  the key bishop takes over d5 (and d3 for the threat) by capturing c4. Pure: fxe4 has no set mate.
  Solver confirms Dombrovskis by refutation on fxe4 against both tries. Flaws: capture key, two tries
  with one refutation, one thematic variation plus a knight check, 17 units, Bh8 idle.
* Sept 30, third sitting (steps 40-124 of session mun61h87): he rebuilt the scheme into a doubled
  Dombrovskis on two different captures, 2b1KB2/3p4/4N1N1/1P1kPBp1/1P4R1/1P1pp3/pbrr4/q1R5 (11+11):
  1.Bc5! (2.Sc7#) dxe6 2.Be4#, Bxe5 2.Se7#, Rxc5 2.Rxc5#; tries Ke7? dxe6!, Bg7?/Bd6?/Re4? Bxe5!.
  Quiet key covering d4 and d6 at once; both paradoxes of equal weight (his balance rule). Recorded
  as `bourd-double-dombrovskis`. Trim: d3 and e3 each removable for soundness but both carry the
  Ke7 try, so the position is tight at 22.

## Session 29 (6-7 October 2026): the daily blog, look-up on the bench, a pawn-step problem

* Daily blog set up (tools/blog.py, blog/, daily-problem skill, mentor issues, nightly dispatch); see
  knowledge/daily_log.md. The bench got a look-up mode: he plays legal lines from the diagram without
  editing it; each step is journalled as `look`, each finished look-up as `lookup`.
* His request: compose a problem on "Black defends by a pawn single and double step", as if for a
  competition. New tool `chesscomp/compose/evolve.py` (evolutionary search scored by the solver). Changed
  mates and reciprocal change were tried first: no reciprocal exists in the searches or in the archive.
  The working mechanism came by hand: king e8, pawn d7, both steps free d7; d6 cuts Ba3-e7, d5 cuts the
  queen's road a2-e6. Result 1r2k3/1N1p3p/7n/8/8/B7/Q1B1K3/7R (6+5): 1.Rf1! (2.Rf8#) d6 2.Qe6#, d5 2.Ba4#,
  Sf5 2.Qg8#, Sf7 2.Qxf7#; try 1.Ba4? Rxb7!. Recorded as `claude-pawn-steps`. The key is plain; asked.
* His verdict on the pawn-step problem: play not bad, nice dual avoidance; 1.Rf1 really bad (a piece out of
  play); set-play changes need a whole new mechanism, not a few units. New critique rule `idle key piece`
  (major, minor when the key piece has thematic tries), with a regression test.
* His own problem on the theme with changes, 2B5/2p1N3/3k4/3NpK2/8/3pQ3/3P4/8 (6+4): 1.Ke4! (zugzwang)
  c6 2.Sf5#, c5 2.Qh6#; try 1.Be6? (c6 2.Sc8#, c5 2.Qxe5#) but e4!. Each self-block releases a different
  white piece; try and key each vacate a knight square and close a queen line. Recorded as
  `bourd-pawn-steps-changed`. He found the short solution silent on the changes: the compact report (Python
  and bench) now prints `changed:` under each try and `Set play also:` for set duals; bench v15.
  Journal muy1hp6i: 20 minutes to the mate pairs, a long dual-killing stretch, then after a break the
  selectors (bishop f6/d8, king g5/f4), the shift one file left, the post-key position first and the key
  retracted. New tool `chesscomp/compose/separate.py` (dual separator) from that process.
* Composing exercise with timing (his request): "two self-blocks by the same black knight". 13.5 minutes,
  log in knowledge/timelog_s29_knight_selfblocks.tsv; solver and searches 94 s of it, the rest thinking.
  Concept: Kd4, bSf4; only Sd3/Sd5 guard b4 (threat Rb4); each self-block frees the white knight that guarded
  the square; each rival mate fails by White self-interference (Sc2 cuts Qc1's file, Se6 cuts the e-rook).
  Mechanism right twice, key wrong twice: 8/2N3R1/8/8/3k1n2/4p3/7B/1RQ1N2K 1.Re7! (2.Rb4#) Sd5 Sb5#, Sd3
  Sf3# (idle rook, key takes e4/e5); lighter 8/2N2p2/8/4pK2/3k1n2/8/6N1/1RQ5 1.Se1! (key piece has a role,
  takes d3; Se6 fails only to fxe6). Two king keys looked sound but the king stood in check: new critique
  rule `white in check` (fatal in the blog gate), and `retract` skips such diagrams. Tool:
  chesscomp/compose/retract.py.
* His answer to my two drafts, three minutes on the bench from draft B: 2N1B3/p1R5/p3pK2/3k1n2/8/2P1pP2/8/8
  (6+6) 1.Ba4! (2.Bb3#) Sd6 2.Se7#, Sd4 2.c4#; tries Bf7?/Bd7? Sg7!, Bb5? axb5!. No queen, the threat
  bishop in play, every guard of a self-block square is also its mating unit. Recorded as
  `bourd-knight-selfblocks-sketch`.
* His next problem (bench muyhjkp8, 19:13-19:35), K e4 with black knight g2: Sxf4 and Se3. His notes: "I'm
  trying changes, one time I will have to guard a king's flight, and one time I cannot as the square is not
  possible to mate on"; "I need to think what releases e5, and what makes mates on f3 impossible"; then eight
  minutes with no moves, the scheme placed in one minute, rotated three times; "the mechanism is basically
  ready, but no threat of course. I will try to find a threat that these knight moves defend. A diagonal
  one usually works." Position 7B/1K5B/1p2P3/5P1N/3PkPN1/pQ1p4/p3P1n1/1b6: set 1...Sxf4 2.Sg3#, 1...Se3
  2.Sf2# (Qb3 guards d5, Bh8 protects d4 through f6); 1.Qc3! (2.Qc6#, gives d5: Kd5 Qc6#) Sxf4 2.Shf6#,
  Se3 2.Sgf6# (the queen protects d4 itself, the f6 knights cover d5). Cooks 1.Kc6, 1.e7, 1.Be5. Finishing
  attempt: a white pawn b5 protects c6 so the king can leave b7 (1.Kc6 gone, 1...Kd5 2.Qc6# kept). 1.Be5
  protects d4 from e5, past f6: inherent while the guard of d4 runs h8-e5-d4. 1.e7 comes from the e6 pawn
  that stops 1.Qe6#. No single added unit fixes either (searched).
* Process profile of his must/can't problem (bench muyhjkp8 + muyiuskd, 19:13-20:04, 260 actions): 85 solves,
  half of them after a single edit ("touch and listen"); 32 solves of post-key positions; long pauses (8 min
  at the start, 6 min at 19:44, 2-3 min twice) come before structural changes, small edits happen on the
  board. Toggles the key piece to read both phases (queen b3<->c3 six times each, king b7<->c6) and probes
  with try-and-revert (29 returns to a position within three edits). Recycles a small set of stoppers (bPb5
  six times, wPe2 and bBb1 four times). Transforms: three rotations to orient the scheme, then shift down
  (19:53, already sound with 1.Qc2), back up for eight minutes of attempts in the old geometry, down again
  (20:01) for the final version.
* Studied with the must/can't lens: his own reciprocal (Problemesis 2005, 8+4) is the same mechanism with one
  bishop line doing both jobs; Kovalic's three-phase Lacny is a Latin square of three gates (d4/d5/d6).
* Attempt: #2 with two changes (his request, no other requirement), 22:21-22:31, log in
  knowledge/timelog_s29_two_changes.tsv. Requirement table first: Kd4, bSf4 (Sd3/Sd5 self-blocks), white Se1 and
  Se7 whose two mates differ only on e3/e5 (Sc2 e3, Sf3 e5; Sf5 e3, Sc6 e5); a queen on h6 covers e3 through
  the vacated f4, on h2 covers e5, so 1.Qh2 switches both pairs (set Sf3/Sc6, after the key Sc2/Sf5).
  Confirmed on a sketch with illegal force. Obstacle: e4. Every line to e4 runs through a mating or
  self-block square, and the two usable ones (a8-e4 via d5, b1-e4 via d3) need two light bishops. Evolve
  (7 min x2, CHANGED=1) found nothing with changes.
* Session 30 (9 Oct): he worked from my two-changes sketch (bench mv0mvey7, 07:17-07:35, 10 notes) to
  2Q1N3/8/3PPpP1/1B1knn1R/8/K3p3/4N1PB/8: bSf5 random S~ 2.Qc4#, corrections Sxd6/Sd4 change from set
  2.Sxf6#/2.Sc3# to 2.Sc7#/2.Sf4# after 1.Qc2! (zugzwang). "The solution is way too cluttered for me to figure."
  New chesscomp/thematic.py (and the same table at the top of the short report and of the bench, v22):
  thematic rows only, phase columns, everything else folded; same-mate "changes" (Qc4#->Qc4#) dropped; tries
  that change nothing or only keep the set play folded into one line per refutation.
  His notes this morning, in order: my sketch's d3/d5 were guarded (no self-block, so no differentiation);
  a threat for two specific knight moves is too hard, so drop it; "prioritizing things according to the
  logical challenge" (d5 first, then e3: "noticing the squares I just cannot guard as part of the mechanism,
  to fail early"); "get something sound at least before pushing for better content"; switched to zugzwang.
  Bench v23: theme box + since-last-solve diff.
* Bench sitting mv2hz0tu (10 Oct, 222 steps, 37 solves, 71 find-key lines, 7 notes): five defences without a White
  queen ("just to prove a point"). Random position with all mates visible (8/2R4p/4p3/1BBkp3/4N3/3PP3/8/7K), Rd7#
  chosen as the threat ("rather easy to defend"), defenders added so each mate follows a defence; first sound
  3n4/2R5/4p2r/1BBkp1N1/8/r6p/1n1N3K/8 (1.Sge4!) at step 70. Then shift right, new defenders (bQ, bB, bS), 3 knights
  for a while (promoted force flagged), trimmed to 1K2n3/pp1R2pb/4N1p1/2Bpk1P1/r3P1B1/4nP2/4N3/1q6, 1.S6f4! (2.Re7#)
  with five defences and five mates, gate PASS. His verdict: not the best mechanism
  to construct a problem, but it shows the general idea of handling cooks and creating some variety. Bug he found: find-key and critique called a protected key piece
  next to the king 'attacked'; now only a legal Black capture counts (critique.black_captures, analysis.js, keyfind
  'sacrifice'; bench v29; tests in test_regression.py).
* Two rooks on one square, by reasoning (10 Oct): post-key mechanism first (Rc3, Rf7 to c7 against 2.Qe5#; mates d3 and Sf6 by
  the line each rook leaves), errors caught by solves: a threat line through the king, Sg3 covering f5 itself, a knight on e8
  checking from d6. I declared 'no key' too early; E. Bourd: iterate the cooks and block them. Three steps: bPd5, Qa8, bPe6 ->
  sound 1.Qb8!. Tool gaps found and fixed: the gate did not flag a double threat; trim treated a changed threat as the same play.
* Two rooks v2 (10 Oct, E. Bourd: reuse pieces, better key; post-key first, then features, then key). Key knight arriving to
  guard e5: g4 failed to fxg4 (feature I should have seen), e5 start failed (all knight moves keep guarding e5; Sxf7),
  f4 start cooked by 1.d3+ Rxd3 2.exd3#, f8 out of play; e7 works with bPb7 against 1.Sc6: 1Q4N1/1p2Nr2/8/3p1pp1/4k3/2r1P3/3PPK2/8,
  1.Sg6!, tries 1.d4? Rc7!, 1.Sc6? bxc6!. Gate PASS. One FEN typo (no black king) cost a solve: check legality first.
* Two rooks v3 (his asks: kill 1...Re7, add a second try refuted only by Rc7): bPe6 kills Re7. Proven by reasoning: no try
  refuted only by Rfc7 exists while R2's mate is Sf6 (no knight reaching f6 can also guard e5; a bishop on f6 is taken by Rxf6);
  an f-pawn mate (f3#) instead brings back 1...Rf5 (R2 can always stop on f5 and guard e5). Second try refuted by Rcc7 needs a
  second e3 guard that can move to guard e5: f2-f4 fails to gxf3 e.p. (with bPg4), Bg1-h2 fails to 1...f4 as well. Current:
  1Q4N1/1p2Nr2/4p3/3p1pp1/4k3/2r1P3/3PP1K1/6B1, 1.Sg6!, gate PASS; 1.Bh2? Rc7!/f4! not yet pure.
* Two rooks, bench sitting mv2kniqz (10 Oct, 17:00-17:02, E. Bourd): the second try is the bishop on f6 (1.Bf6? with 2.Qe5#),
  refuted ONLY by 1...Rfc7! because it takes the f6 square from 2.Sf6#; the first try stays 1.d4? (Rcc7 only). Key 1.Bf4!
  (bishop guards e5 from f4). Checked: gate PASS, two single-refutation tries, three distinct mates. My earlier searches
  never tried a bishop on f6 as a try: the lesson is to test the thematic tries the user names before searching.
* Theme 'two rooks capture a white knight' (10 Oct, alone, his instruction: full process, come back when ready). First
  scheme (knight guards d4, queen threat) failed at the post-key table: f3 uncovered, e5 a flight. Rebuilt: the knight is the
  threat (2.Sc3#), the rooks capture it on b1 and each loses the line that guarded a mate square of the h5 knight. Solver
  corrections: diagram flight e3 (key protected it, so the diagram did not), 1.Sd2# mate in one once f2 protected e3,
  out-of-play 1.Sa3-b1 (fatal) with a cook 1.Sb5, the double threat Sc3#/d3# created by Bd4 protecting e3 (cured by bSf2
  attacking d3, which adds 1...Sd1 2.d3#), and 'e5 via the bishop' was redundant (f4 covered it). Final
  8/8/1r6/5p1N/2P1kPpK/2B1P2P/3PPn2/1N4r1, 1.Bd4!, gate PASS, trim-minimal, 16 units. 9 solves, 0 searches.
* Theme 'black knight closes the same white line twice, different mates' (10 Oct, alone). Rank line a5-e5 cut by a c7 knight
  failed: a queen behind the knight restores e5 after any knight move, queens nearer gave mates in one or Qe5/Re5 double threats.
  d-file version: Rd8 guards d4 through d7/d5, Sb6 cuts on d7 (2.Rb4#, b-file opened, knight cannot return) and d5 (2.Bxd5#).
  Corrections: Bxd5 re-blocks the rook's line, so the key must guard d4 itself (1.Sf3, threat Sg5 vacates f3); bare position
  cooked by 1.c3/1.e3 (pawn guards d4, then Re8/Rd4 threats) until bPe5 guarded d4 and blocked the e-file; bishop a2/e6 had a
  mate in one along its other diagonal (Bb1#, Bf5#) because the rook covers d5: wKc2 blocks it; 1.Rxb6 cooked once bPe7 gave
  Black tempo (bPa7 answers it). Final 1R1R4/p3p3/1n6/4p3/4kPP1/6P1/B1KPP3/6N1, 1.Sf3!, three mates, gate PASS, trim-minimal,
  15 units. About 12 solves after the restart, no searches. Not for the blog (dailies only).
* Process (E. Bourd, 10 Oct): an hour with no visible progress was a chained 3x5-minute solver command plus an output cutoff.
  New rules in CLAUDE.md: 5-minute cap on every search, one solve per command, a progress line before each.
* Same theme, his scheme (10 Oct): a threat through f4 with the knight closing b8-f4 on d6 and e5. About 25 solves, no
  searches. Dead ends: rank mate after Sd6 interposed by Sd6-c4; Bg6# interposed by Sd6-f5; Sxd6 capture-mate duplicates
  Sd6# after random moves; a pinned Be7 guards nothing (Sc5 mate in one); the black line piece behind d6 closes the line
  itself (Bd6/Rd6); a key knight from e5 protects e5 from every square (Re5 dual); a rook on e5 checks the king. Result:
  1B6/7p/B7/3p3R/2n1k3/2P5/4K3/6N1, 1.Sh3! (2.Sf2#) Sd6 2.Bd3#, Se5 2.Rxe5#, gate PASS, 10 units, but random knight moves
  allow three mates (threat, Bd3, Re5) and the critique did not report it (hidden under 'further moves allow the threat').
* Theme 'two black defences by the same bishop open a white line, with different mates' (11 Oct, E. Bourd's request).
  Paper first: the opened line as the queen's path, with the mates on two squares beyond the vacated one, chosen by where the
  bishop lands. Three schemes died. (1) Ke6, Bd3, Qd1 (Be4 guards d5 -> Qd7, Bb5 guards d7 -> Qd5, both guard c6 against
  Rc6): sound post-key (postsearch gave 10 hits), but the lone bishop is unprotected, so 1.Qxd3/1.Sxd3, and every waiting
  move works. (2) A Ra5-Sd5 battery opened by Bc5-d4/d6 (each cutting a rank rook): every battery check is interposed by the
  bishop returning to c5. (3) Ke5, Bd4 protected by its king, Qd1, Bc1 guarding f4 through e3: 1...Bc5 2.Qd5# (Bxd6 kills
  Qd6), 1...Be3 2.Qd6# (Kf4 kills Qd5); threat Re7 (Bc5 takes, Be3 opens f4). This mechanism held. postsearch READY=1
  (seed 12) found a post-key with black Pe2/Pf5/Sg1 restraints; without its Pd7 it was sound,
  4N1B1/8/6P1/4kp2/3bP3/5P2/4p2R/2BQ2nK, 1.Rh7! with fxe4 2.Rh5# as well, but the critique called Rh2 out of play (fatal).
  About 15 solves chasing a better key (rook from h3-h6, Bf7-g8 clearance with Pc4, Sg3, Sf2, Sh3, Rb4) went in circles.
  The way out was to drop the h-file. The rook stands on c6 guarding e6 (replacing the Bg8 cook-stopper), so 1.Rc7! gives the
  flight and threatens Re7, with Pf6 protecting e7 so that 1...Ke6 2.Re7#. Black pawns g5+h6 kill 1.Qd3/1.Qd2 and f7 kills
  1.Sc7/Sg7 + Re6. Final 4N2K/5p2/2R2P1p/4k1p1/3bP3/5P2/4p3/2BQ4, gate PASS, trim-minimal, 8+6. Flaws: static key, mixed
  defence and dual-avoidance motives, random bishop moves allow three mates, four black pawn plugs. About 30 solves, 2 searches.
  His verdict: a nice flight-giving key, worth the static play unless a nicer scheme is found; unity preferable; 'a problem
  can push more'. He disliked the black e2 pawn attacking the queen. v2: 4N3/5p2/2R2P1p/4k1p1/3bP3/5P2/p5K1/2BQ4 (black a2 +
  white king g2 replace black e2), gate PASS, trim-minimal, 5 solves.
* Theme 'a bishop and a knight defend by unpinning a black piece' (11 Oct, E. Bourd; he set aside the bishop-line
  problem: 'would be hard adding the effect here'). Mechanism: Bb2 pins Sd4 (Ke5), threat Sf3#, Bb4-c3 and Sd5/Se2-c3
  unpin on one square, the departures unguard d6 and f4/f6 (one dual-avoidance motive). Post-keys sound by postsearch.
  No acceptable key after about 15 solves and 5 searches: the pinning bishop is idle or cooks f4, and threat-knight keys
  bring f4+ or queen cooks. A new diagram search (key fixed, solver-scored) found sound diagrams, but each had an idle
  key piece. Open; reported to him.
* Bench sitting mv3ukaxu (11 Oct, E. Bourd, 142 steps, 25 solves, 30 find-key lines, 5 notes): from my post-key sketch
  3Q4/8/2R5/3nkp2/1b1n4/3P2P1/1B3P2/6NK. He moved both mates to the queen (a6 along the 6th rank: Qd6/Qf6), dropped the
  f2 pawn and the Bd6 extra, added a black rook a4 and found the key 1.Bf5-d3 (shields f3 from Ra3); first sound
  6bK/5p2/Q6R/3nkB2/rbPn3N/6P1/1B6/8, final 2N5/3p1K1p/Q7/3nkB2/rbPn3N/6P1/1B6/8, 1.Bd3!. A third mate on e6 failed (the
  e6 square is not tied to the pin). 'Can improve much more, but the scheme works.'
* Theme 'two black knights capture the same pawn' (11 Oct, E. Bourd): the mechanism came from postsearch in one run
  (Kd5, Pe5, Sd3/Sf3; Sfxe5 Rd4#, Sdxe5 Ra5#, Kxe5 Qe6#; threat Qd6#). A new diagram search, keysearch.py
  (solver + critique scored), found 1.Qe3-b6 as the only key, but with a c6 flight in the diagram. Covering c6 brings
  knight-capture and check cooks. Reported to him with the post-key sketch.
* He asked for 'two knights unpinning a pawn on the same square' and I built captures (misread 'uping'); he asked
  'where is the unpin'. Redone: Bb2 pins Pd4, threat Re3#, Sbc3 Qd6#, Sec3 f4# (post-key 3QN3/5R2/8/1n2k1N1/3p4/7R/1B2nP2/K7,
  extras Sd6 Qxd6#, Sg3 f4#). Key not found yet (1.Ra6-f6 is unique but takes a diagram flight).
  Continued 'till finished or giving up': rank-pin rebuild (Ra5 pins Pd5, threat Bc3#, S7c5 Qh8#, S3c5 Qf4#), clean
  post-key 8/3n4/2R1P1B1/R2pk3/7Q/3n4/3B2b1/K7. No fatal-free key in about 12 searches and solves; gave up for now.
  New tool chesscomp/compose/diagsearch.py.
* Bench sitting mv41atcg (11 Oct, E. Bourd, 39 steps, 9 solves): finished the two-knights pawn unpin from my sketch:
  8/3n4/R2p4/3pkPQN/4p3/3nP3/b2B4/K7, 1.Ra5! (2.Bc3#) S7c5 Qf6#, S3c5 Qf4#. 'Not sure why you gave up... you are pretty
  weak at transforming, or finding softening of a position'. Lessons recorded (softening order); compose skill updated.
* Theme 'two black rook defences unpin a black knight', same square (11 Oct, E. Bourd). Restructured three times:
  rooks b8/b2 with queen mates on h8/h2 (too many guards), rooks b7/b3 with Qg7/Qg3, then the pinner as the mating
  queen: Qa5 pins Sc5, rooks b6/b4 shut her diagonals, R6b5 Qc7#, R4b5 Qc3#. A free-threat search found the post-key
  (threat Re6#). Keys tried: 1.Qa4-a5 (sound, changed set mate Qd4#->Qc3#, queen out of play), 1.Sd5-e7 unmasking
  (four tries, but a diagram flight), 1.Bb5-d3 (Rxc4 hole). Finished: 6K1/1p6/1rp4R/Q1nBk3/1rp1Pp2/3n1P2/4N3/8,
  1.Bf7! (2.Re6#) R6b5 Qc7#, R4b5 Qc3#; try Bxc4? Rxc4!. Gate PASS; flaws: static key, attacked key piece. New tool
  chesscomp/compose/unmask_search.py.
* E. Bourd on 1.Bf7: 'not bad... the static key is acceptable here, it's a bit predictable... the key pins'; asked for
  tries where a knight makes the key and blocks the queen mates. A knight mask on d5 failed (Kxd5 flight, or 1.Qxc5 when
  d5 is protected). The mask on b5, the interposition square, works: 8/p4B1K/1rp4R/QNn1k3/1rP2pP1/3n1P2/4N3/8,
  1.Sa3! (2.Re6#) R6b5 Qc7#, R4b5 Qc3#, Rxc4 Sxc4#; tries Sc7?/Sd6? R6b5!, Sc3? R4b5!, Sd4? R4b5!/Rxc4!, Sxa7? Rxc4!.
  Gate PASS, trim-minimal. unmask_search got an optional TRIES requirement.
* E. Bourd on 1.Sa3!: acceptable, real tries, too symmetrical by design; publish tries as a pair; and 'compose a good
  problem around the theme, not the simplest' (recorded in CLAUDE.md, compose 6b, judge checklist).
* Theme 'two bishop defences by different bishops blocking a white line' (11 Oct). First mechanism (Qd6/Rd5 with a2 and
  d-file lines) was impure: Bc4 also guarded the threat square d3. Rebuilt on the queen's two lines: Qb4 rank and
  diagonal, Be6-c4 / Be3-c5, mates Qd6#/Qf4#. Stage 1 sound: 7K/4Np2/4b2R/4kP2/1Q4P1/4bPP1/7N/5r2, 1.g5! (2.Sg4#).
  Key still weak (pawn clearance, static); thematic 1.Bh7-f5 cooked so far. freethreat.py got a PURE check (defender must
  not guard the threat square after its move).
* E. Bourd on stage 1: errors not unified (line opening vs unguard), threat knight out of play, by-play = thematic mate
  (big flaw); 'the thematic request was in a sense the same line'. Rebuilt: the threat is the line (Qc-file to c7),
  both bishops cut it; unguard errors everywhere. Post-key 8/4N1K1/1p5R/3bkBB1/7R/1N2b3/3P4/2Q5: Bc4 Re4#, Bc6 Re6#,
  Bc5 Bf4#, no by-play duplicates, pure. No key: the diagram allows deflection sacrifices (Re6+, Re4+, Bf4+) and
  long-diagonal checks (Qc3+, Qb2+, d4+). Earlier c2-queen versions (Qe4#/f4#) had the same cook family.
* E. Bourd: Bc5 also guarded d6 (impure); the threats I pick use long lines and pieces outside the play; his bench
  sketch (session mv4dvvuh) 8/8/3P3R/3k4/8/2bb4/8/8: Rh6 on the 6th rank, Bf6/Bg6 block, bishops free along their
  diagonals. Finished the mechanism on it: post-key 8/1NQ5/3B3R/3kb3/3p4/1P1b1P1N/8/K7, 2.Qc5# threat, Bf6 Sf4#,
  Bg6 Qc4#, Bxd6 Qxd6#; key 1.Qg7-c7 unique but a c6 flight in the diagram (fatal). Asked him about c6.
* E. Bourd composed the two-bishops theme himself on the bench to show the process (session mv4dvvuh, 103 steps):
  scheme 8/8/3P3R/3k4/8/2bb4/8/8 spread (line and cut squares away from the king); my Be5 was 'way too much
  interfering'. Post-key with a knight threat; holes fixed unit by unit; the only key was 1.Rh4+ (check), then a pawn
  killed it; he moved K and Q, removed Sa4, bQb1, bPb2, and turned the board a quarter (the c2/c3/c4 pawn chain that
  checked Kb3 and promoted became a static b6/c6/d6 chain, the mates' targets). Three changes to a hole-free post-key;
  findkey gave five unique keys, he chose the one with a try. Final 5N2/2KQ1p2/1ppp3n/1bbkBPp1/8/2R2P2/8/4R3,
  1.Sg6! (2.Se7#) Be2 Qxc6#, Be3 Qxd6#, fxg6 Qe6#, Sxf5/Sg8 Qxf7#; try Sh7? Be2!. Re-solved: sound, gate PASS,
  trim-minimal. New tool chesscomp/compose/transform.py (shifts, rotations, rank all placements) with
  tests/test_transform.py; compose skill got 'Spread the scheme' and 'Shifts and rotations'.
* E. Bourd's second demonstration (bench mv4gmdxo, 48 steps): scheme Rh6, Pe6, Bd7, Kd5, Bc3/Bc2; threat square e6
  (moved from d6 along the line), error mates on b4/b3 away from the cut squares. Post-key Qb5 solved twice, findkey:
  only key 1.Qf1-b5 (sound 10+4, no set play); he chose 1.Qe2-b5 (gives up the e-file guard of e6, set play, change
  Bg6 Qa2# -> Qb3#) with g5 against Rh5+; a black rook gave an unprovided check and went. Final
  nK6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8, 1.Qb5! Bf6 Sb4#, Bg6 Qb3#. Re-solved: sound, gate PASS, trim-minimal.
  Improving it as he invited: replacements for Sa8 (470 tried) -> only Se8 also works and adds 1...Sf6 2.Sc7# (third
  cut of the line, unguard error); g5 has no better replacement; the king is passive on every working square; no queen
  try (only Qb5 makes Bc6# a threat). New tool chesscomp/compose/restop.py with tests/test_restop.py.

## Session 11 Oct 2026 (evening): his published record, PDB and WCCT
* He downloaded his PDB entries (query A='Bourd', 246 problems, LaTeX). 60 were already in Problemesis; the
  other 186 are now the `pdb_bourd` collection (tools/pdb_tex.py, raw export in knowledge/sources/).
  PDB stops in 2018 and lacks two of ours (Variantim 2015 #2635, Novice TT 2002).
* "Are all my WCCT problems there?" PDB has 19 placed entries (8th-10th WCCT). Two agents read his mail
  (read-only): no entry in the 11th or 12th WCCT (he selected for the team in 2021); in the 10th he gave the
  captain 8 problems and PDB has 7 as entries; mail before 2010 is gone, so the 8th cannot be checked.
  Summary and table: knowledge/bourd_record.md. All 19 shown with diagrams (docs/blog/cards/wcct-*.png) and
  translated solutions.
* Solver check (5-minute cap, resumable): 56 of the direct and self mates checked, 44 ok, 4 with no printed
  key, 8 timeouts (moremovers and s#), no cook and no mismatch.
* Process failure: the first notation conversion dropped origin squares, and the check reported a false
  mismatch (Sc3 for Sbc3); fixed by converting the first move to SAN from the diagram.
* Open: the sixth joint 10th-WCCT candidate (in "Israeli problems for WCCT.pdf", mail 15-17 Apr 2016); the
  truncated "problem from wcct not sent" (7 Dec 2013); whether to add his later problems to PDB.
* Studies of published #2s (11 Oct, E. Bourd: "go over existing #2, starting with simple ones, understanding how the
  mechanism works"). New `chesscomp/anatomy.py`: the king's field after each mate, field change of each first move,
  why each try's threat fails after its refutation, essential pins, role table with idle units flagged; 4 tests in
  tests/test_anatomy.py. Ten sound problems from the database (5-12 units) read in `knowledge/studies.md`: Bourd and
  Labai turn out to be one Le Grand engine (contact/distant cross-geometry); Kazimov (two-job key); Milewski x2
  (black correction; Boros with Bh2 whose only job is pinning self-pinned defenders: first tool version called it
  idle, fixed by adding pins); Marin (focal at a crossing point); Velimirovic (black Albino); Slesarenko-Gvozdjak
  (Dombrovskis by side effects); Rice (unpin key from a no-move position; stalemate tries were silent, fixed);
  Velikÿ (focal rook, masked bishops behind mating knights). Tool bugs found on the way: 'K' marker collided with
  the white king's name; variations by different units were merged in one drawing. Four problems carry a
  try-only or plug unit, Bourd's own Pg2 among them: asked him how his 7 Oct rule weighs that.
* His answers on the studies (11 Oct): the try-only unit is a drawback, not fatal (gate, checklist, CLAUDE.md,
  tests changed: 'try-only unit' is now a warning the post must name; 'superfluous piece' stays fatal).
  Miniatures are too simple, even with changes; he mainly composed complex problems. Next studies: complex #2s,
  starting with his own WCCT entries (collection pdb_bourd).
* Merged origin/main (anatomy tool, PDB record, studies); main's lessons.jsonl carried committed conflict markers, removed.
  E. Bourd on 1.Qb5!: the two mating units hold c5 for each other (connected play). The anatomy confirms it (key: c5
  Sa6 -> Qb5,Sa6; Bf6 Sb4#: Qb5 alone; Bg6 Qb3#: Sa6 alone). anatomy.py got a LINKS section (reciprocal guards and
  mating units working in other mates) with a test; judge and compose skills point to it.
* 12 Oct: merged to main on E. Bourd's request; CLAUDE.md "Everything is ours" (improve any tool; work reaches main;
  anatomy while composing). Theme 'the same black knight has defences, in each it closes a different line'. Skeletons
  by enumeration (new chesscomp/compose/line_skeletons.py): T d4 / Se3 -> c2,f5 (rook threat, no key: too many
  White mates) and T e3 / Se1 -> c2,g2 (local knight threat). Post-keys by the free-threat search (promoted to
  chesscomp/compose/freethreat.py with a test). Queen keys failed structurally (an added guard is a flight or the
  threat already mates); pawn d3 gave sacrifice cooks; the try pair by blocking needed 8+10. Result, by the fixed-key
  search: 4Q3/6p1/8/2Pk4/2R5/1Pp3K1/3N4/1Nr1n2b, 1.Sf1! (2.Se3#) Sg2 Qe4#, Sc2 Sxc3#, 7+6, gate PASS, trim-minimal;
  flaws: static key, attacked key piece, passive king. Side result: 8/3KR3/1Bp5/3kp2r/7Q/3P4/1N6/1nr1n2b, 1.Sd1!
  with try 1.Sc4? Sc2! (by-play Rxd1 Qc4# repeats a thematic mate, second black knight).
* Studies, complex round (12 Oct; his WCCT entries are #3+, so his honoured orthodox #2s instead): StrateGems 2007
  2HM (each rook defence cuts the support of the other queen mate), Sredba 2003-05 1HM (Bf5 plugs two black rook
  lines at their crossing: Le Grand without flights), Wola Gulowska 2015 5HM (two masked batteries: pin while the
  mask stands, double check once it moves). Anatomy improved (any session's tool, all ours): a White unit on a
  flight is credited ('on f6'), and a removal test per mate finds plugs/protectors (Pb4 blocking Qa3-d6) that the
  guard map missed; the idle flag now uses it ('needed in no mate'). Tests added.
* His answers (12 Oct): Pc4 (StrateGems 2007) was a cook/dual stopper; Wola Gulowska 2015 shows reciprocal changes
  and started from the geometric scheme (both lines, knight mates). I had called it pseudo Le Grand; the theme he
  names is the reciprocal change. Recorded in studies, principles, lessons.

## Session: blind tourney judging (12 Oct 2026, branch claude/tournament-2-judgment-experiment-3str0l)
* E. Bourd: "judge all problems of the tournament, then compare with the actual judgement, not biased by placement".
  Protocol: FENs only, shuffled labels, judge subagents, award sealed (sha256 / sealed JSON); our verdict committed first.
* Problemesis 2003 #2 (P. Robert): 25 of 35 entries (D60-D69 are stored as "Inédit" in the database, so the field
  missed them). Nine of the 35 entries are E. Bourd's. We placed 13, he placed 8. My aggregation overrode a judge's
  named fatal dual (D53).
* MK2 2016 (Spearman 0.69, same 1st Prize) and Moscow Ch. 2012 (thematic 0.61 without the theme; published 0.07), from
  his PDFs (selivanov.world). Lessons: count phases, not variations; tabulate tries x defences; name multi-phase
  themes; our fatal list is our standard, not an award predictor. Into the judge checklist, lessons and knowledge/experiments/.
* (12 Oct) E. Bourd: flaw tolerance grows with content; judge checklist got a light/medium/rich scale anchored on his problems; CLAUDE.md and judge skill point to it.
* 12 Oct: E. Bourd on 1.Sf1!: 'the knights and queen are somewhat off... the key from a more central square'.
  line_skeletons got --knights (mates by knight checks on the closed line) and --central; chose T d4, Se3 -> c2/f5,
  Rc1 and Rf-file rook, the same White knight mating on c3 or f4. Post-key by postsearch (threat Qb6d4 fixed), key
  by unmask_search (KSQ e2 FSQ d4, tries required; now penalising by-play repeats). Hand cleaning: Sd8 -> Bd7,
  Kc8 -> Ka5, Qb6 -> Qa7 with bPa4 instead of Ba4 (clean try 1.Sb5? Sf5!). Result 8/Q1BB4/2P2r2/K2k4/p1pNp3/4n3/8/2r5,
  1.Se2! (2.Qd4#) Sf5 Sf4#, Sc2 Sc3#; set R~ Be6#, Rxc6 Bxc6#. Open flaw: 1...Rd1 2.Sc3# (by-play repeat); the d2
  plug that stops it fails the gate (superfluous) and a 480-unit scan found no unit that stops it and plays.
* Problemesis 2004 #2 (judge M. Mladenovic), full field D70-D122 (53), judged blind with the calibrated checklist: his 1st
  Prize (Bourd D88) is our 2nd; 4 of his 6 in our 15; AUC 0.80. His filter: "rude refutations, flight-taking tries and keys";
  our top unplaced picks (Bourd D74, D75) had them. Missing names: Somov, Albino (Albino added to themes.json).
  Organiser fixes made blind: multi-solution stipulations (D96 4 solutions, D81 2 solutions) are in the record's `play` field, not the FEN.
* 12 Oct: E. Bourd: 1...Rd1 is fatal (it also refutes the partner try 1.Se6?; one try of a pair gives bad taste).
  New chesscomp/compose/knight_pair_skeletons.py classifies the line pieces' escapes (self-blockable or not); chose
  T e5, Sf6 -> d7/g4, rooks b7 (not c7: it attacked the try square c6) and h4, key Se5-g6, tries Sd3/Sc6. postsearch
  (threat Qc3e5) then unmask_search with the try pair required found 8/1r6/1p1PRn2/1KpkNB2/2p1p2r/2Q5/b2P4/8:
  1.Sg6! Sd7 Se7#, Sg4 Sf4#; tries 1.Sd3? Sg4 Sf4# but Sd7!, 1.Sc6? Sd7 Se7# but Sg4!. Gate PASS, 7+9.
* 12 Oct: E. Bourd: "a black knight and a bishop self-block diagonally to the black king in 2 variations", then "on the
  same square". Kd5/c4 attempts failed: a threat checking through c4 is met by the blockers interposing; a White line
  through c4 guards it; the K/S/B sacrifice form is Strebkovs 2003. Found the masked-line motive (Rc1 behind Sc5: the
  threat Sb7 unmasks c7/c8, the block on c7 cuts c8) and moved the king to the edge (Kd8, square c7). Keys by search
  (unmask_search KSQ f6 FSQ d5) and by hand (start on e8, not d5). Result n2kNB2/8/B6p/2N3nQ/8/3K2b1/1R6/2R5:
  1.Sf6! (2.Sb7#) Sc7 2.Rb8#, Bc7 2.Qe8#, Kc7 2.Se6#. Gate PASS, 8+5; flaws: no tries, Ng5/Ph6 cook-stoppers, Kd3.
  Tools (ours, all sessions): postsearch and unmask_search take SELFBLOCK=1; postsearch rejects promoted black units.
* Problemesis 1999-2002 #2 (judge J. Morice), full field D1-D34, blind: 5 of his 7 in our 8, our three Prizes all placed,
  AUC 0.86 (best of five). Our 1st Prize (Kapros D15, four-phase queen tries) was his last placed; he paid for line strategy
  (bivalence, masked lines, anti-Lewmann, Franco-Latvian, equipollent moves). Lessons and checklist line added.
* The Problemist #2 (2014 Rossomakho, 2015 half-years), field from yacpdb (the only strong source reachable; PDB needs a
  login, wfcc/schwalbe/problemist/variantim are blocked). AUC 0.69 / 0.66. Biggest misses: white correction with tertiary
  threat correction (Bruch, 1st Prize, our 50th) and thematic multiple threats (English Novotny, Fleck) read as fatal.
  Themes "White correction" and "English Novotny" added to themes.json; checklist lines added.
* StrateGems 2015 #2 (judge H. Gockel; yacpdb), judges given the published solution and theme keywords: AUC 0.70, his
  1st/3rd/4th Prizes our 3rd/6th/8th, 7 of our 11 placed are his. Misses: role-exchange changed play (king batteries,
  2nd Prize) and threat corrections sunk by our "rude moves" filter. Checklist softened: weigh rude moves, do not filter.
* The Problemist 2010 #2 (Wiedenhoff; yacpdb, solutions given): AUC 0.67. 1st Prize (black correction over five phases)
  our 13th; half-battery 3rd HM our last. tools/blind_tourney.py added (build/compare). Conclusion over eight runs: complete
  short awards 0.80-0.86, strong long awards 0.66-0.70 (judge's taste inside a competent field).
* 12 Oct: E. Bourd on 1.Sf6! (same-square self-blocks): "mega complicated, and you made it"; the flight-giving key is nice,
  the position generally ok; flaw: Rb2 active in only one variation. He will post easier constructions of the idea on
  the bench with his reasoning (read them with the `bench` skill when he comes back).
* 12 Oct, bench sitting mv59m754 (672 steps: 99 solves, 184 find-key calls, 27 notes): E. Bourd built five schemes for the
  same-square self-blocks, after my 1.Sf6!. His order: which mates can come on a self-block, the separation, why Black
  defends there. Capture of a White unit on the square (1.Qd6! Bxd3 Qe6#, Sxd3 Qc6#; 1.Bf4! Sxd5 Re6#, Bxd5 Bh7#), a pin
  as separation (1.Bf6! Sxe6 Se3#, Bxe6 Rd1#), stopping a double check (1.Qd3! threat Rc7 unmasking Bf8 through d6;
  Sd6 Qxe3#, Bd6 Qc3#), zugzwang (1.Re8! Bc7 Re6#, Sc7 Rd8#). All five re-solved sound with the Python solver (by-play
  and set duals noted). My mistake recorded: the capture motive is not anticipated by a sacrifice-key problem.
* 12 Oct: E. Bourd: "try problem selfblock by rook and knight on diagonal square". Followed his bench order (mates on the
  block, separation, motive) and his capture motive: Ke4, the threat knight on d3 captured by Rd1/Nb2, Qc3 protects d3
  and mates on c6 (the rook on d3 would interpose on d5) or e5 (the knight on d3 guards it). Result
  8/K7/4B3/2B5/p3kP2/2QN4/1nn2R2/3r4, 1.Bb6! (2.Sc5#) Sxd3 2.Qc6#, Rxd3 2.Qe5#; gate PASS, 7+5; three cook-stoppers,
  no tries. Tool fix (all sessions): self_block_needed now requires the king to be able to step onto the emptied square.
* 12 Oct: E. Bourd: "rook and bishop selfblock on a square adjacent to the king orthogonally". freethreat (SELFBLOCK=1,
  WANT Q* for both captures) found the motive in one round: Pd4 protects the threat square e5, Qb6 protects d4. keyfind
  --patch: 5R2/4p3/1Q6/3N4/r2PkNK1/8/5b2/8, 1.Rf5! (2.Re5#) Rxd4 2.Qe6#, Bxd4 2.Qb1#; gate PASS, 6+4, trim-minimal.
* 12 Oct: E. Bourd: extend the rook+bishop problem ("tries or changes or some other extending motive"). separate showed
  every changed pair needs the queen as the key piece; a rook threat ready in the diagram is a mate in one; the queen star
  (Qf6/Qg7/Qh8 protecting d4 through e5, Ra5 behind Bc5 for the A-mate) stalls on 1...Bd6 and on the diagram square.
  unmask_search with the try 1.Re6 required found instead 8/8/1Q3R2/3N4/r2PkN2/8/5bK1/8: 1.Rf5! sacrifice, Kxf5 Qg6#,
  Rxd4 Qe6#, Bxd4 Qb1#; 6+3, no cook-stopper. 1.Re6? is refuted only by Kf5.
* 12 Oct: E. Bourd: "the composing entity should push for a bit more now than the basic requested theme" (recorded in
  CLAUDE.md and lessons); theme "two black pieces unpin a black pawn on the same square". Our collection already had it
  (his 1.Ra5!, two knights). Second layer chosen: a Grimshaw on the unpinning square. Free-threat searches with
  departure-unguard schemes failed; the crossing geometry by hand (Rc1 below guarding c6, Ba7 guarding d4 through c5);
  postsearch (threat Rh4e4) then keyfind --patch: 3N4/b3BK2/6p1/3pk3/R6R/N2P1p1B/4P3/2r5, 1.Ra5! Bc5 Sc6#, Rc5 d4#,
  Rc4 Sxc4#; gate PASS, 15 units; the solver names the Grimshaw. No thematic tries yet.
* Variantim 2019 Israel Ring #2 (Kopyl; yacpdb, solutions): AUC 0.76 on 18 orthodox; his Prizes our 3rd/5th. Two fairy
  entries (neutral pieces) slipped through; tools/blind_tourney.py now filters them. Open questions for E. Bourd collected in
  knowledge/experiments/questions_for_bourd.md.
* The Problemist 2011 #2 (yacpdb, solutions): AUC 0.64; his Prizes 1-3 our 11th/8th/3rd. Tasks and named schemes (battery
  task Special HM, Burmistrov Comm) scored "mechanical" by us: checklist line and lesson added.
* WCCI 8 section A winners (uploaded by E. Bourd), 15 problems, blind with solutions: Spearman -0.32 against the WCCI points.
  The 10/10 (Burmistrov + Zagoruiko, Dyachuk) our 13th; the cleanest (8.5) our 2nd. wfcc.ch allowed: 661 PDF links saved in
  knowledge/experiments/wfcc_pdf_links.txt; WCCT 10/11 section A entries and reports downloaded for the next blind runs.
* 12 Oct: E. Bourd: "add tries ... the pin in the initial position ... by the same piece that moves away to open a line
  or to guard a square". Try piece: a knight on the threat square e4 (every move opens Rh4-e4 and guards e4). Tool
  (all sessions): unmask_search takes THREAT=<mate id> to fix the threat. Searches (36 runs, 280 s each) found a
  pure Rc5-try (1.Sf2?) or pure Bc5-tries, never a clean pair: the Bc5 mate is a knight check (2.Bc7+? Bd6), so its
  lever is the flight Se7 gives up (f5), held only by Sg3/Sd6; a pure pair needs a heavy line through f6 and came
  out at 21+ units with queen cooks. Result, slimmed from z3 by hand: 6b1/b3N2p/3ppP1K/R2pk1P1/3pN2R/8/7P/2r1n1B1,
  1.Sg3! (2.Re4#) Bc5 2.Sc6#, Rc5 2.Bxd4#; 1.Sd2? Bc5!; 1.Sf2? Bc5!/Rc5!. Gate PASS, 19 units (bBg8 only kills
  1.Sxd6? Kxd6!).
* WCCT 11 section A (wfcc.ch, 86 entries, 79 scored, theme given, eight blind judges): Spearman 0.63 against the total, like a
  sixth judging country (the countries with each other 0.34-0.72). 1st place (Kovačević, Zagoruiko 4x2) our 2nd. Misses: double
  threats paid for by a record (A01 3rd-4th our 21st) and a new task arrangement (A35 6th our 46th). Checklist line, lesson,
  question 7 extended. knowledge/experiments/blind_wcct11_A.md.
* 12 Oct: E. Bourd on 1.Sg3! (one pure try): "without a pure pair, its almost not worth having 1 pair ... the effect of
  guarding f5 looks too limiting"; "with only 1 real try it just seems unfinished problem of 2 tries ... its always
  worth going further, and then look back". Tried a diagonal pin (Ke5, Pd4, Bb2, Grimshaw on c3: both mates on lines,
  tries Be2?/Bd5? by a Bf3; fails on 1...Bd2 guarding e3 and 1...Re1) and Ke4/Pd4/Ra4 with a Grimshaw on b4 (Raxd4 and
  queen cooks). Back to the knight wheel: rebuilt t1 by hand, one stopper per solve: 3N2b1/b2P3p/3pP2R/1Q1pk1K1/
  3pN2R/8/1n1PP1PP/2r3B1, 1.Sg3! (2.Re4#) Bc5 2.Sc6#, Rc5 2.Bxd4#; 1.Sf2? Rc5!, 1.Sf6? Bc5! (pure pair), 1.Sc3?
  Rxc3!, 1.Sc5? dxc5!; gate PASS, 22 units. New tool (all sessions): compose.trypair enumerates one or two stoppers
  around a kernel for a key with named single-refutation tries (tests/test_trypair.py).
* 12 Oct: E. Bourd on 1.Sg3! (pure pair, 22 units): "its ok imo, pretty complex. it does feel a bit heavy and probably
  can improved, but its decent"; the e6 double protection: "a good mechanism achieving the goal".
  Economy pass (all 28 pairs of stoppers removed, one unit added, compose.trypair functions): the only sound 21-unit
  hit was bPg3 for wPg2+wPh2, with the key 1.Sxg3 (a capture: fatal). The 22-unit version stands. Tool fix (all
  sessions): trypair rejects a capturing key.
* 12 Oct: E. Bourd: "black half pin of a bishop and a rook. each doing at least 1 thematic variation". Scheme: Bh7
  pins Rg6/Bf5 to Ke4, threat Rxe5# along the e-file, both units block on e6 (Re6 covers f6, Be6 covers g4). Path:
  postsearch gave non-pin mates (Be6 Sd6#, Re6 Bxf5#); a queen threat had no key; the inherent cook 1.Sf6+ Rxf6 2.Rg4#
  set the key as the mask's own move Se7-g8. Position A (4R3/2p1N1NB/6rp/3ppb2/3Bk2n/4Pp2/3K1P2/6R1) was cooked by
  1.Sexf5; no single unit cured it (compose.trypair). bRh5 for bNh4 did (it retakes on f5 and guards e5), turning the
  bishop's defence into B~; bPg4 removed the Bg4 dual; wPc3 removed 1.Sxd5? Kxd5!; trim removed bPh6; wPe2 replaced
  bPf3+wPf2. Result: 4R3/4N1NB/6r1/3ppb1r/3Bk1p1/2P1P3/4P3/3K2R1, 1.Sg8! (2.Rxe5#) Re6 2.Rxg4#, B~ 2.Sf6#; try 1.Sc8?
  B~ 2.Sd6# (changed), but 1...Bxc8!. Gate PASS, 17 units. No pure pair: no knight landing spoils Rxg4#. Theme note
  added to themes/references/half_pin_king_key.md.
* 13 Oct: E. Bourd on claude-halfpin-br-sg8: too many impurities (B~ defences from bRh5), no extension; heavy is fine.
  Looked for a pure pair. Finding: one-knight tries need both mates to be knight checks, only possible with a file pin
  (Ke4, Be5, Re6, Re8) - Kapros, Problemesis 2002 (psis-0dd597ba62) has it, with unpin motives. New tool (all sessions):
  compose.halfpin_pair (SPEC env: knight key, two try squares, one defence per half-pinned unit, free threat);
  12 runs on origins e3/f4/d4/c7, no sound hit. Hand schemes (Be7 mask with Qd8-h4, Rd7 cut) cooked (1.Rd4+). Asked
  E. Bourd which direction: knight wheel near Kapros, the pure e6 double block extended otherwise, or tries by two pieces.

## Daily run No. 8 (13 Oct 2026, routine): Self-pin
Added the direct self-pin detector (motives.mate_motives, motives.detect_self_pin, Patterns 'Self-pin', evolve
PATTERN=Self-pin) and the blog's 'attempts' list. Composed B7/2N5/2Pp4/1P2p1B1/RK1nk2N/1PR5/2P5/1Q1n4, 1.Rg3!: two
self-pinning knight captures with check against a royal battery, the pinned knight choosing the king's square. Dead ends:
two loaded knight batteries, immobile pawn blockers (recapture mates only), a bishop matrix that was Avner & Retter's
reflected. The detector lives in motives.py (Python only, like the Grimshaw and half-pin detectors); docs/analysis.js has
no motive layer to mirror.
* 13 Oct: E. Bourd composed on the bench (sittings mv5v1wnn, mv6klxrm) from claude-halfpin-br-sg8: wB on f4 masking Rf1,
  threat Rf4# with Pe5 pinned on the e-file, Re6/Be6 unpin it; pure pair 1.Bg3? Re6!, 1.Bxe3? Be6!; key 1.Bxh6!. Three
  white rooks on the bench; Qe8 for Re8 verified sound with the same play. Quiet key 1.Bh6 needs bPh6 gone, then 1.Bg5
  also solves; no one-unit stopper (trypair). Recorded as bourd-halfpin-e6-bf4.
* 13 Oct: E. Bourd went on (sitting mv6klxrm, steps 37-80): Qe8, then shifted left, Qd7 pinning Pd5, wBe4 masking Re1
  (threat Re4#), 1.Bc2! Rd6 Rxf4#, Bd6 Se6#; tries 1.B~? Bd6! (d3 unguarded once Sc5 leaves), 1.Bf5!? Rd6! (closes
  Rf8-f4): a white correction. Quiet key, 18 units, trim-minimal. Recorded as bourd-halfpin-correction-bc2. I misread the
  four Bd6 tries as a 'same refutation' flaw and offered wPf3 to cut them; he: "almost correction style".
* 13 Oct: E. Bourd: "another half-pin of rook and a bishop on an orthogonal line ... multiple mates might be available".
  Scheme: Ke4, Be5, Re6, Re8. Mates that use the pin: after a rook move Sc3#, Sg3# (f4 empty), Rd4#/Qd4#, 4th-rank
  checks; after a bishop move Sd6#, Sf6#, Qc6#/Bb7#/Qa8# (d6 empty), Qg6#/Bh7# (f6 empty). Sound base, recorded as draft
  claude-halfpin-file-sf7: 4R3/3p4/3pr2N/3Rb2p/2K1kp1N/8/3B4/8, 1.Sf7! (2.Sg5#) Rg6 2.Rd4#, Bf6 2.Sxd6#, set R~ Rd4#;
  only Rg6 and Bf6 defend. No thematic try: the threat has one creating move. Dead end: Zagoruiko 2x2 by Se7-d5/f5
  (search and hand analysis, lesson). New tool (all sessions): compose.halfpin_tries (SPEC env, diagram search scored by
  the solver: one defence per half-pinned unit, pin-using mates, pure tries; it finds Kapros's pair on his diagram).
  Twelve runs from five seeds found no pure pair yet; halfpin_pair on a b6-d5 knight wheel did not reach a sound post-key.
* 13 Oct: WCCT 10 section A (wfcc.ch, 93 entries all marked, theme "anticipatory unpin of a white piece", nine blind judges with
  the checklist calibrated after WCCT 11): Spearman 0.73 against the points (countries with each other 0.62-0.78). 2nd-3rd place
  (Shanshin) our 5th, 1st (Witt/Bruch, logical white correction) our 14th, 2nd-3rd (Bykov/Belchikov, theme in a try) our 41st.
  Checklist lines: read the set theme literally (a thematic try is full fulfilment), score the logic of a multistage try sequence,
  weigh white units idle after the key heavier. knowledge/experiments/blind_wcct10_A.md.
* 13 Oct: E. Bourd on the bench (sitting mv6ykgg4, 330 steps, 97 solves) from claude-halfpin-file-sf7: kept the
  Sf7/Sg5 threat for a while (the Bd4/Rd4 holes, a zugzwang try, a queen for the bishop), then rotated three times and
  shifted, ending on a rank half-pin Qa4: Rb4, Bc4 to Kd4 with the threat Sc6#: 1.Bxc2! Rb6 2.Rd3#, Bb5 2.Sb3#;
  1.B~? Bb5!, 1.Bd3? Rb6! (the white correction again). "bit ugly i made it work kinda". Recorded as
  bourd-halfpin-rank-bxc2. Checked: the capture key is forced (bPa5 for bpc2 leaves Bc2 and Bb1 both, no one-unit
  separator); the stopper cascade starts at Bd6 (Be5# after Bb5). Critique fix (all sessions): tries by the key piece that
  fail to one refutation while another try fails to a different one are a 'white correction' plus, not 'same
  refutation' (E. Bourd's reading of 12 Oct); test in test_regression.py; checklist line updated.
* 13 Oct: E. Bourd: c5 is the issue, and "the resolving using d5 pawn is a bit chaotic". Restructure sketch (not sound):
  the key bishop starts on the threat square c6 and goes to g2 (guards d5 and e4 along the long diagonal), so no d5 pawn,
  no Rg5, and Bd6 no longer mates on e5; 1.Be4? Bb5! pure. Left open: 1...Bd5 (guards c6) has no mate of its own;
  Rd3# repeats the rook's mate and the extra c4 guard (Rc1) brings 1.Rd3+ as a cook. Lesson in lessons.jsonl.
* 13 Oct: E. Bourd went on (steps 331-500): moved the knight off c5 ("it made it a bit easier to manouver"), a rank-5
  version with 1.Bc3! (tries Be5? Bb6!, Bd4? Rb7!/Rxb3!), then "the correction on the diagonal": back on rank 4,
  8/4N3/8/2pP1BR1/Qrbk1P1n/npR5/1K1N1P2/8, 1.Bb1! (2.Sc6#) Bb5 Sxb3#, Rb6 Rd3#; 1.Bh7/Bg6? Sf5!, 1.Be4? Bb5!,
  1.Bd3? Rb6!. 17 units, gate PASS, recorded as bourd-halfpin-diagonal-bb1. Left: 1...Bxd5 2.Rxd5#/Rd3#; cause found
  (Sd2 is the only guard of c4 after 2.Rd3); Sa1 kills the dual but loses Sf3# against 1...Sf5 and the e4 guard.
* 13 Oct: E. Bourd asked for a taste verdict on 1.Bb1! and said I am too harsh on pawn captures ("minor flaws"). Fatal-flaw
  line in CLAUDE.md now reads 'captures a piece'; judge skill, checklist and critique wording updated (all sessions).
* 13 Oct: compared claude-halfpin-file-sf7 (13 units, no tries) with bourd-halfpin-diagonal-bb1 (17 units, correction
  with a pure pair). E. Bourd: "it's incomparable for me. The additional content is almost always worth it". Added to
  CLAUDE.md (the theme is the floor) and lessons.jsonl.
* 13 Oct: new theme from E. Bourd: black half-pin of a rook and a knight. Findings so far: a knight's new squares never
  guard what it guarded before (colour parity), so the rook's pin mate is spoiled after S~ only by occupation (then the
  mating piece usually captures with check: dual) or by the knight landing on the mating line of a distant piece. Two
  sketches failed on that (h4 pin, threat Sc6; e8 pin, threat Sc3). Anticipation: Dyachuk, Probleemblad 2002, 1st Prize
  (psis-c1154197a2, pure pair with reversal) and Barnes, StrateGems 2002, 1st Prize (psis-25e8021eff, both defences on e6).
  compose.halfpin_tries now detects diagonal pinners (any two half-pinned units).

### 13 Oct 2026 - rook-and-knight half-pin, basic scheme (session 0be7e202)
- Basic scheme first, as E. Bourd asked: claude-halfpin-rs-qg8, 7Q/3NN3/3p3B/8/1p2k3/3n2K1/2rP4/1B6, 1.Qg8! (2.Qd5#)
  Sf4 2.Qc4#, Rc5 2.Qg4#, key gives d4. Gate PASS, 7+5. Light: no tries, three soundness units (bPb4, bPd6, Bh6).
- How it came: four freethreat runs from near-empty seeds gave nothing; reasoning by knight colour (see lessons) and nine
  hand solves did. The queen does the threat and both mates (one line each: a2-g8 diagonal, g-file).
- Next layer tried: the pure try pair by the queen (1.Qg5? Sf4!, a Qg8/Qf7 try refuted by Rc5), queen on g7 in the
  diagram; 1.Qf7 then also solves (Rc5 2.Qf4#) and 1.Bxc2 cooks. halfpin_tries runs from both diagrams.
- Second layer done: claude-halfpin-rs-qf7, 8/4N1Q1/3p3B/R7/1p2k3/3n2K1/2rP4/1B6, 1.Qf7! Sf4 2.Qc4#, Rc5 2.Qf4#;
  pure pair 1.Qg8? Rc5! and 1.Qg5? Sf4!. compose.halfpin_tries (rng 1) found it in under 280 s from the hand diagram with
  the queen on g7: Sd7 -> Ra5, so that 1...Rc5 also cuts the 5th-rank guard of e5 (the refutation of 1.Qg8). The hand
  idea (bPh5 against Qg4) failed to knight checks on Kg2. The basic scheme took ~9 hand solves; the try layer one search.
- E. Bourd's bench sitting mv73p0wa (146 steps, 57 solves), from claude-halfpin-rs-qf7: bourd-halfpin-rs-qf7,
  8/6Q1/6N1/8/1p2k2K/3nNp2/2rP1P2/1Bnb4, 1.Qf7! Sf4 2.Qc4#, Rc5 2.Qf4#; tries 1.Qg8? Rc5!, 1.Qd7? (Rc5 2.Qg4#) Sf4!.
  Path: first fought the double threat of my 1.Qg5 try (steps 8-22, pawn on f5, no solution), tried a shifted
  orientation with Kd4 (steps 25-48) and dropped it, then rebuilt the guards around a white knight on e3 (d5/f5, c4/g4)
  and Sg6 (e5/f4, closing the g-file), moved the queen through d7/f7/g8/g5/g7, and cleaned with bSc1 (d3), bPf3, Kh4,
  bBd1 (Bxc2). Whole-side restructuring again: my Ra5/Se7/Bh6/Kg3/bPd6 all went.
- Co-author step on his version (he: "you are my co-author. always welcome to try more"): one black knight e1 guards c2
  and d3, so it replaces bSc1 (d3) and bBd1 (c2); with Kh4 it checks from g2, so a scan of every king square
  (scratch kscan.py) found f1/g1/h2/g3/h6; g3 chosen (takes part). bourd-halfpin-rs-qf7-se1, 8/6Q1/6N1/8/1p2k3/3nNpK1/2rP1P2/1B2n3, 7+6.
- Half-pin of two knights (E. Bourd: "lets go next, half-pin of two knights"): the basic scheme is the rook-and-knight
  problem with Rc2 -> Sc2, sound in one solve (claude-halfpin-ss-qf7, 8/4N1Q1/3p4/R7/1p2k3/3n2K1/2nP4/1B6, 1.Qf7! Sf4
  2.Qc4#, Se3 2.Qf4#; tries Qg8? Se3!, Qg5? Sf4!). Knight-specific layer tried: both knights to b4, separated by the
  departure (d3 flight / c-file opened to a black Rc1). Post-key found by freethreat, 1...Sf4 repeating, no key. Published
  two-knight half-pins in the base: Loshinsky (psis-c3c45b84fb, both to d2, pinner takes the other knight) and Ivanov
  (psis-95d7a43c46, The Problemist 2000).
- Two-knight half-pin, new mechanism without a flight (E. Bourd: "something without king flight, its a bit limiting"):
  claude-halfpin-ss-qh5, 7Q/4N3/6N1/6B1/r3k2K/2Pn4/r1n3P1/1B6, 1.Qh5! (2.Qf3#) Se5/Sde1 2.Qe2#, Sd4/Sce1 2.Qg4#;
  set Sd4/Sce1 2.Qe5#. Four NOFLIGHT freethreat runs (e-file from both ends) found no threat from bare seeds; the hand
  design came from the knights' common guard square (e5 and d4 both guard f3) and one queen diagonal h5-g4-f3-e2; four
  hand solves to a clean post-key (Sg6 against Qg6/Qh7, Bg5 closing the 5th rank, Kh4 against Qh4, bRa2 for the e1 pair),
  keyfind --patch for the key (+bRa4). freethreat got NOFLIGHT=1.
- Orthogonal two-knight half-pin, separation by arrival (E. Bourd: the dual avoidance must not come from the d3 flight):
  e-file pin Ke4/Se3/Se2/Re1. (1) Rank checks from both sides, each knight's arrival blocking the other side (Se3-g4,
  Se2-d4; threat Qf3 from h5): rank mates cover little, so every field square needs a static guard and then every
  white check mates (four threats). (2) Both knights interfering on the f-file with a Qf3 threat: the queen on the
  f-file also reaches f5, and with f5 guarded Qf5 mates whenever a knight is frozen. (3) King on the edge (Kh4, h-file
  pin): an arrival covers the partner's colour, so it spoils the partner's mate only by blocking. Twelve freethreat
  runs (NOFLIGHT) from bare seeds found threats but no defences; from the hand structure the best was the post-key
  8/8/3Q1R2/6K1/2p1k3/2P1np1B/4n3/4RNb1 (Sg4 2.Rf4#, Sd4 2.Qxd4#, Sd5 2.Bf5#, threats Sd2 and Re6).
- E. Bourd's bench sitting mv7bwm99 (13-14 Oct, 238 steps, 77 solves) from my orthogonal sketch: bourd-halfpin-ss-bh7,
  8/3QKp2/2N5/5B2/3p1kpP/3P1npP/5nb1/3N1R2 (his Pe5 removed, verified), 1.Bh7! (2.Qf5#) Sxh4 2.Qxg4#, Sxd1 2.Qxd4#;
  tries 1.Bxg4? Sxh4!, 1.Be4? Sxd1!, 1.Bg6? fxg6!. The turning point was a masking bishop on the threat line (step 188):
  its landing squares gave the try pair at once. The last step, a one-file shift, used the board edge to kill Bg7/Bh8.
- E. Bourd's bench sitting mv7emm2t (14 Oct, 128 steps, 19 solves): cleared his f-file problem down to the half-pin core,
  shifted it up and left, rotated twice and rebuilt a new scheme on the d-file above the king (post-key, no key yet):
  3B1b2/3R4/2Qn2B1/r2n4/3kP3/2pN2N1/2P2P2/1R4K1 (Black to move), threat Se2#; 1...S5f4 2.Rb4# (Bf6+? Re5!: the
  departure opens the 5th rank to bRa5); 1...S6f5 2.Bf6# (Rb4+? Bxb4!: the departure opens f8-b4 to bBf8); by-play
  1...Rc5 2.Qxc5#. No flight, no black check, 17 units. White to move also mates by Bf6+, Bb6+, Rb4+; keyfind (48
  retractions, 1070 one-unit patches) found no key.
- Key hunt for his d-file scheme (3B1b2/3R4/2Qn2B1/r2n4/3kP3/2pN2N1/2P2P2/1R4K1): in the diagram Se2# is already mate,
  and the stray checks Bf6+/Bb6+/Rb4+ lead by force to the same pin mates, so the key must add something every pin
  mate needs; the only square that is not a diagram flight is d5 (occupied until a knight leaves), and the threat Se2
  does not need it. diagsearch: 1.Qc2 unique on a lighter version but by taking the flight Kxd3 (diagram flight);
  unmask_search: 1.Sd3 (from b2) unique with diagram flight Ke5; 1.Sg3 (from h1) with bPc7 leaves 1.Bf6+ as a cook.
- His rebuilt version on the 5th rank, bourd-halfpin-ss-bd8, b3R1N1/Q1B5/5Ppp/R2nnkN1/6pP/1K1P2P1/1P6/4r3, 1.Bd8!
  Sf7 2.Qf2#, Se7 2.Qd7#: sound, gate PASS; my improvement searches found nothing better (see its note).
* 14 Oct: WCCT 9 section A (booklet on wfcc.ch, the 27 entries printed with a diagram, three blind judges): Spearman 0.16 against the
  total, while the five countries agree with each other at 0.08; the 1st place (Murashev, Slesarenko, Feoktistov) is our 1st. Lesson:
  effects the theme produces by itself are the floor (textbook Hannelius + Dombrovskis placed 20th-27th). README conclusion 16:
  full fields measure judging (0.63-0.73), top fields measure taste. knowledge/experiments/blind_wcct9_A.md.
- E. Bourd on bourd-halfpin-ss-bd8: "key is slightly less flawed here, as we have a set mate, and the bishop seems to
  guard e5 as well". Verified: Bc7 is the only guard of e5 in the set 1...R~ 2.Rxe5# (seven rook moves) and doubles e5/f4
  in the set 1...Sf7 2.Qf2#; c7 is the only free square guarding e5 and reaching d8, so the attack by Sd5 follows from
  the set job; 1...Sxc7 is the one capture left without a set mate. The critique's 'attacked key piece' finding now
  names the set mates that need the key piece on its diagram square and the unprovided captures of it
  (chesscomp/critique.py, tests/test_critique_key_role.py).
- Changed mates, E. Bourd's bench sitting mv88wzbb (14 Oct, 54 steps, notes only, one solve): three types of 2x2 changed
  mates (see lessons). Type 1 composed: claude-changed-type1-qg8, 8/3BB3/5NQ1/4k1Pp/2pn4/2n1P3/8/7K, set Sd4~ 2.Qf5#,
  Sc3~ 2.Qe4#; 1.Qg8! (2.Qb8#) Sd4 defences 2.Qe6#/Qxe6#, Sc3 defences 2.Qd5#/Qxd5#. Path: evolve on bare cores (8 jobs)
  found no key; the hand design needed the diagonal threat (knights interpose on lines), Sf6/Bd7 guarding each knight's
  pair, then one cure per solve: Pc4/bPc5 (Se4 refutation, Qd3), restructure to Qg6/Sf6/Be7/Bd7/Pg5 (cooks Qg6/Qh6),
  bPc4+bPd3 (Qd3), bPh5 (Sg4 dual); trim removed bPd3. Gate PASS, 7+5.
* 14 Oct: WCCT 8 section A (book on wfcc.ch, 28 entries decoded from a Type-3 chess font, three blind judges): Spearman 0.30 against
  the place (countries with each other 0.22). 2nd place (Gvozdják) our 2nd, 1st (Kovačević) our 9th. The WCCT 9 checklist line
  overcorrected (discounted a Zagoruiko the theme does not force): rewritten as "what the theme's wording logically entails", plus a
  line on real black correction. A judge's FEN copy error (two pawns dropped) was caught by re-solving before freezing.
  knowledge/experiments/blind_wcct8_A.md.
- E. Bourd on claude-changed-type1-qg8: not 6 changes, all knight moves are the same; make each knight's defence unique.
  claude-changed-type1-unique-qg8, 8/2pK2nQ/5N2/4k1P1/7p/2nBP3/2r1p3/8: set Se6 Qf5#, Se4 Qxe4#; 1.Qg8! (2.Sg4#) Se6 Qxe6#,
  Se4 Qd5#; tries 1.Be4? Rd2+!, 1.Qxg7? Se4!, 1.Qxh4? Se6!. Hand mechanism (threat Sg4 by the d5/e4 guard itself, guards cut
  by Se6/Se4) then cooks Qf7 (twin), Be4, Qe8+, Bc5/Bd8 (Be7), Qh7-h2; new evolve flag UNIQUE=1 (unique_defence.py, tested)
  found the version with the black knight on g7; trim removed bPa2, bBa5 replaced by bPc7. Gate PASS, 6+7.
* 14 Oct: WCCT 7 section A (scanned book, 27 entries read from the images, three blind judges, out of sample): Spearman 0.22 against
  the place, countries with each other 0.00. 4th and 6th places ours exactly; 1st our 14th, 2nd (Stolev, "best key of the tourney")
  our 12th. Checklist: a blend is judged by its weakest group; the key weighs most in a single-phase problem. README conclusion 18.
  knowledge/experiments/blind_wcct7_A.md.
- E. Bourd: replace one defending knight of claude-changed-type1-unique-qg8 by another piece. 12 evolve UNIQUE runs (bishop on
  b7/c6/g2/c8, rook on d4/f6) and hand designs (Bg2-h3 vs 2.Sd7#, Rb6 guarding e6): no sound version. Reason recorded in
  lessons (a bishop guards the pair along its own line and keeps an on-line defence against any knight check; a rook keeps one
  guard on every move). Near-miss 2b5/4Br1Q/5N2/4k1N1/8/2nBP3/7K/2R5: 1.Qxf7 (2.Sf3#) Bb7 Qe6#, Se4 Qd5#, but Bg4, Rxh7+.
- E. Bourd's bench sitting mv8f1ugp (14 Oct, 60 steps, 18 solves): our unique-defence problem with Sc3 replaced by a black bishop
  on b7; bPf3 blocks the bishop's diagonal so its only defence is Bc8 (guards g4 along c8-h3). His last position had a second key
  1.Ba2; finished as bourd-changed-type1-bishop (wPb3, 9+9, try 1.Be4? Bc8!) and bourd-changed-type1-bishop-light
  (1n5b/1bp3nQ/5N2/2P1k1P1/3N3p/K2PPp2/8/8, wPd3 for Bb1+Pb3, bPg4 removed, 8+8). Both gate PASS, nothing removable.
- E. Bourd's bench sitting mv8ffb5c (14 Oct, 18 steps, notes): type-1 with the queen switching from the b1-h7 diagonal (g6) to
  the 5th rank (g5), defenders bRe1 (e4/e5) and bSb4 (d3/d5), batteries Bh7/Rh5, threat 2.Bc3#. Asked to finish it: six evolve
  runs; best 8/7B/5PQ1/2P4R/1n1k2P1/1K1p2r1/1P1B4/1R2r3 (1.Qg5! unique key, four defences) fails on the thematic dual
  1...Rc1 2.Qe5#/Qf4#, inherent (see lessons). Not shown as a problem.
- He finished his diagonal->rank scheme himself while I reported it stuck (mv8ffb5c steps 19-196): same Rc1 duals at first,
  rotations, then a quarter turn and a new threat: bourd-changed-diag-file-qc7, B1RK3b/1Q1Pp3/1P6/7r/2pkpB2/8/3nP3/3N4,
  1.Qc7! (2.Be3#) Rh3 Qc5#, Sf1 Qxc4# (set Qd5#, Qxe4#). Gate PASS, 9+7. Lesson recorded on what I should have done.
- E. Bourd on bourd-changed-diag-file-qc7: guard-only defences are pure single moves, not a flaw; he avoided defences on the
  thematic squares because he dislikes the queen recapturing there. Critique: guard/unguard flag now only without changed
  mates (note 'pure guard defences' otherwise), new minor 'mate captures defender'; judge checklist updated; tested.
- E. Bourd: compose another type-1 problem, maybe with other pieces than knights defending. Geometry first
  (chesscomp.compose.type1_geometry, tested): a rook and a bishop cannot share two queen lines; they need queen posts with
  different reach. One-step pairs Qg3-g2 and Qc7-b7 failed on the set flight being mated (1.Sb3+ Ke4 2.Qd3#, 1.Sc2+ Kd5
  2.Qc6#); Qa3-a8 works because Sb3 blocks the queen's rank. claude-changed-type1-rook-bishop,
  1K6/7b/1N1B4/1p5r/3k1pp1/Q7/nPpNBP2/2r5: set Bg8 Qd3#, Rh3 Qc5#; 1.Qa8! (2.Sb3#) Bg8 Qe4#, Rh3 Qd5#; set Grimshaw f5
  (Bf5 Qc5#, Rf5 Qd3#). Gate PASS, 8+9, heavy: six black cook-stoppers. evolve gained a type-1 mode (DEFSQ/TKEY/QMATE) and a
  candidate-list mutation (CANDS); 40 search jobs on bare or kernel cores found nothing, the hand guard table did.
- E. Bourd on claude-changed-type1-rook-bishop: the corner key is nice and sets the changes; Rd5 a small flaw; the set Grimshaw
  is fake (never fulfilled after the key, so it does not exist); "nice construction". Recorded as a principle and a checklist line.
- E. Bourd: type 1 on two orthogonal lines (three mating squares each), then his non-adjacent scheme (bench mv8ffb5c steps
  197-208: Ke4, Qa5->a6, black Bg8 and Qg3 defending, Rh5, pawns marking d5/e5 and c4/d3). Orthogonal first:
  claude-changed-type1-ranks, 8/3K4/2p1p3/7Q/N2k1PP1/8/1N3PB1/2r1r3: set Rcd1 Qc5#, Red1 Qe5#; 1.Qh3! (2.Qd3#) Rcd1 Qc3#,
  Red1 Qe3#. Seven solves by hand: Pd2 blocked the d1 defence, Kh7 let Rh1 pin the queen, Bb4/Bh6/Sb4 mated on c3/c5/e3/c2,
  Ba6's guard was cut by Rc4, 1.d7 promoted. Gate PASS, 8+5.
- E. Bourd: less symmetric, different pieces. claude-changed-type1-files-pawn-rook, 2Q2K2/1B1N1P2/3p3p/1p6/1n1k4/1P5r/3P1N2/8:
  set d5 Qc5#, Rh4 Qc3#; 1.Qe8! (2.Qe4#) d5 Qe5#, Rh4 Qe3#. Pawn d6 (c5/e5) and rook h3 (c3/e3); six solves; gate PASS, 8+6;
  five cook-stoppers (Kf8, Pf7, bPh6, bSb4, bPb5).
* 14 Oct: blind PREDICTION for WCCT 12 section A (63 entries, theme Double Mate Correction, six blind judges), frozen before the
  award: knowledge/experiments/predict_wcct12_A.md + .json (entry codes, FENs, our scores). Our top: A44 (DMC as a full Zagoruiko 3x3, flight key), A47
  (DMC + a Dombrovskis try on all three defences), A54, A42, A52, A46. Compare when the award is published (README row).
- E. Bourd's bench sitting mv8ktz5s (14 Oct, 35 steps, 8 solves): from claude-changed-type1-files-pawn-rook he replaced the rook
  by bPd3 + bBc1 + wRg3: 1...d2 makes two errors (opens Rg3 to c3, closes Bc1 to e3), the queen's line chooses. Sound at step
  34; trimmed (-Pb6 -ph6 -pg7) to bourd-changed-type1-pawn-errors, 8+8, gate PASS. Recorded his principle: type 1 by two errors
  in one defence, many combinations. His first scheme (step 20): 1...Sb1-d2 unguards bPc3 + closes Bc1-e3, cooked by 1.Qc6.
- E. Bourd: "try to do the first problem of the type, and change the errors of the defenses". Wrote
  chesscomp.compose.errors (which part of a defence, departure or arrival, makes each mate; tested). Enumerated two-error
  defences around K e5: the side the queen comes from (f5/e6) has none without a diagram flight, the far side three
  (Sf2-d3, Sb6-c4, d5-d4); his bench scheme has the same split. Eight evolve runs on two-error cores found nothing; by hand,
  keeping the first problem's threat 2.Qb8#: claude-changed-type1-qg8-two-errors, 8/3BB1nQ/1nP2N2/p3k1Pp/r7/p2KP1P1/8/8,
  set Sc4 Qe4#, Sf5 Qxf5#, Se8 Qf5#; 1.Qg8! Sb6~ Qd5#, Sf5/Se8 Qe6#, Se6 Qxe6#. 1...Sc4: arrival closes Ra4-e4 (set),
  departure unguards d5 (solution). Gate PASS, 9+7, nothing trimmable; heavy, six cook-stoppers.
- E. Bourd: "lets try to duplicate the closing of line maybe, and just 1 thematic move. big jump yes". One defence closing two
  Black lines: for K e5 and the queen h7 -> g8 the only crossing for e4/d5 is d4 (Ra4 and Rd1). Eight evolve runs found nothing;
  by hand (threat knight Sd8 freed by the queen taking e6, threat 2.Sc6#, the d4 knight guarding c6):
  claude-changed-type1-double-closing, K2N4/4B1nQ/3p1P2/p1p1k3/r7/1n2P1N1/6B1/3r4, set Sd4 Qe4#; 1.Qg8! Sd4 Qd5#, the only
  defence. Gate PASS, 8+8. Fixes on the way: check-first cook 1.Sc6+ Ke6 2.Qg8# (free d7), 1.Qxg7# (Pf6), by-play dual
  1...Se6 2.Qxe6#/Sf7# (Bb7 -> Bg2), rook paths to c6 (bPa5, bPc5, bPd6).
- E. Bourd (15 Oct): "maybe you can finish this - idea Qg7-f7, Sd3 Se6", after bench sittings mv8r4h2h/mv8v9fm2 (K d4, bPc4/e4/e5,
  bRe8 for e5, bBe2 for c4 through d3, knights b4/g5, his Qb7 with Ba8 behind). Read as the mirrored battery Qg7+Bh8: set Se6 Qxe5#;
  1.Qf7: Sd3 Qxc4#, Se6 Bxe5#. Not finished; three structural findings (lessons.jsonl, 15 Oct): the Qg7/Bh8 battery cooks by
  1.Qxe5+ Rxe5 2.Bxe5# unless the bishop's protector is masked by the knight's origin (bSc5 in front of wRa5); a threat through
  e6 is refuted by 1...Re6, a threat stopped by the d3 cut also by 1...Bd3; far/near mates on one check line (K e4, Qg2 -> Qf3)
  cook by 1.Qg2+ Rf3 2.Qxf3#. Evolve (8 runs x 270 s) moved the key to 1.Qc7 (2.Qxc5#, Black correction S~ Rd5#, Sd3 Qxc4#,
  Se6 Bxe5#), still refuted by Bd3 and Rc8. Asked him which mates he meant.
- E. Bourd: "lets practice the other types of transfers" (his types 2 and 3). Type 2 on his rook scheme (Rf6/Rd4, knights
  guarding one square of each rook's pair): a bishop selects the rook (c6 protects d5/e4, d7 protects e6/f5). Mutate; the set
  needs a hole. claude-type2-rooks-light, 8/2n5/2B2RK1/4k3/3R4/4P1n1/8/8 (evolve 6+3, then -Pc3): set Sg3~ Re4#; 1.Bd7! Sg3~ Rf5#,
  Sc7~ Re6#. claude-type2-rooks-full, b7/1pn5/1PB2R2/4k1P1/3R2P1/3K2n1/8/8 (by hand, 7+5): both changes, hole 1...bxc6, tries
  1.Bxb7? Bxb7!, 1.bxc7? bxc6!. Both gate PASS. Fixed chesscomp.compose.trim for zugzwang keys (it never trimmed a block).
- E. Bourd: "lets try something more complicated, we need to increase complexity, the gate of passing needs to slightly
  increase" (after the type-2 mutates). Raised the gate ('simple block' fatal; zugzwang, random defences, symmetric play
  flagged; CLAUDE.md rule: a working mechanism is a scheme). Then a real Grimshaw with changed mates, Velimirovic 2000 as the
  model. Basic scheme, sound: claude-grimshaw-e6-scheme, 2N1r1b1/8/3p4/1Bk5/2P5/K6n/5n2/1RQR4, 1.Qh6! (2.Qxd6#) Re6 Rd5#,
  Be6 Qe3# (postsearch + keyfind, gate PASS) - our verdict: a scheme. Did not stop; tried (all failed so far, reasons in
  lessons.jsonl 15 Oct and grimshaw.md): knight on the threat square as selector; queen posts f6/g6/h6 on the threat line
  (six different mates, but the queen's diagram square g7 gives 1.Qd4#, h7 is attacked by Bg8); d4 left unguarded (key
  1.Qf6!, tries Qg6?/Qh6? Re6!, Be6 mated three ways; open: 1.Qc3+ Bc4 2.Qxc4#, 1.Qg1+ Re3 2.Qxe3#); a masking rook as
  selector (one pair split); set play vs solution with the queen h2 -> h6 (out of play). New tool
  chesscomp.compose.trychange (tested): the fast pre-filter that found the posts.
- E. Bourd: "arrange changes in the diagram ... after Qg6, Qh6 maybe ... Qf6 seems hard due to the d4 square". Added
  MODE=set (set play vs key, check cooks) and MODE=posts (one key, the other posts as tries) to
  chesscomp.compose.trychange. Search found the c6 knight guarding d4: 4r1b1/3R2Q1/ppn5/1pk5/1R6/KP4N1/8/8, three keys
  (Qf6/Qg6/Qh6, Re6 Qc3#/Qc2#/Qc1#, set Qc3#, Be6 always Se4#). He: "this works, not the best key, but the play generally
  works"; he will look for another scheme. He asked to be told whether a search is by tools or by reasoning (lessons).
- E. Bourd's bench sitting mv9trlcf (15 Oct, 158 steps, 36 solves): from our e6 Grimshaw (steps 2-39, no solve) two quarter
  turns to K g4 / Grimshaw e3 (first sound at step 76, 1.Qf7!), then K f4 / Grimshaw d3: bourd-grimshaw-d3-changed-set,
  B3K3/3N4/6pN/6p1/5k2/Qp2b2R/4Pr2/1b1r4, set Rd3 Qf8#, Bd3 Qd6#; 1.Qxb3! Rd3 Qf7#, Bd3 Qb8#. The queen starts on one post
  masked by bPb3; the capture key opens the line. He: "this works, not the best key"; he will look for another scheme.
- E. Bourd's scheme "Qd5/c6/b7, Re4/Be4 close the line to f3, mates along the diagonals": tried as threat Qf3# through e4
  (hand geometry, then chesscomp.compose.trychange MODE=posts with THREAT=* and TARGET, both added and tested). K f4: the
  queen checks from five squares; shifted to K h4 / Grimshaw g4 / Qh3#: Rg4 mates change (Qh5#, Qh6#), Bg4 mates do not
  (Bf2#); best 5nr1/5Q1n/8/8/3BNN1k/2K5/1P2b1RP/8 cooked by 1.Qxg8. Not finished (lessons.jsonl).
- E. Bourd's bench sitting mv9wf7y9 (15 Oct, 221 steps): his own e4/f3 scheme set on d4/c3: bourd-grimshaw-d4-three-phases,
  8/qp6/1b2Q1p1/3P2B1/rr5p/pPPk4/3NN3/3K4, 1.Qe5! (2.Sc1#) Bd4 Qe4#, Rd4 Qe3#; tries 1.Qf6? (Qxg6#/Qf3#) Rf4!, 1.Bf6?
  (Qe4#/Qh3#) Re4!. Our verdict given in chat: rich (Zagoruiko 2x2 + a third phase, refutations by the 4th-rank rook shutting
  each guard of e3); flaws: set duals, Pd5 and the a7 queen as plugs; trim: -pb7.
- E. Bourd continued on the bench: bourd-grimshaw-d5-queen-posts, q7/2p1Q1p1/2b5/r1r4p/p1Pk4/3NNP2/3K4/8, 1.Qe6! (2.Sc2#)
  Bd5 Qe5#, Rd5 Qe4#; try 1.Qf7? Bd5 Qxg7#, Rd5 Qf4#, Bxf3!. 6+9, nothing trimmable. His principle recorded: pieces behind
  the Grimshaw units stop the cooks on the thematic lines. Our verdict: weakest point the capturing, unthematic refutation.
- E. Bourd: "how would you find that improvement, its not just trimming". Wrote chesscomp.compose.rerefute (tested): re-guard
  the square a try lacks with a line piece crossing a thematic unit's line; on his Pf3 version it finds -Pf3 +Bg6 (1.Qf7? Rf5!)
  as the only hit in 13 s. Compose skill step 6c added.
- E. Bourd: "i improved a bit more!? noticing that the black queen might not be needed": bourd-grimshaw-d5-7x7,
  8/2p1Q1p1/2b3B1/r1r5/p1Pk2P1/3NN3/3K4/8, 7+7 (-bQa8 -bPh5 +wPg4). Added rerefute.lighten (trim with replacement, tested):
  finds his step as the only hit; no lighter version of the new position.
- Our verdict on bourd-grimshaw-d5-7x7 (judge skill): medium content, clean; the changes are unified (each pair uses the
  square the Grimshaw cuts: the queen lands on e5/e4 in the key, mates through it in the try - Qxg7, Qf4), the refutation
  1...Rf5 is the Grimshaw rook on its own line; flaws: wPg4 plug, only two phases (Grimshaw + try/key change is a known
  combination), 1...Rxc4 Qxc4# constant, random bishop duals, Kd2 passive. Expected commendation level; publish try + key.
- E. Bourd: "a different type of changes ... 2 pieces ... other effect which makes only 1 of the 2 mates possible; simple
  first, then unity". Scan of problemesis (#2 with a try, same defence, different mating units, same key piece): 121
  problems; model Ahues 1997 (Sc5?/Sc7! selecting fxe3#/Qxe3#). Random searches (scratch type2.py) failed (cooks, fake
  changes). Hand construction (stated as such in chat) of a knight that masks the queen's file and guards e3, ~15 inspected
  steps, then chesscomp.compose.keysel (new, tested) for the key's reason: claude-type2-d4-scheme,
  3Q1R2/1r6/8/2pNN3/4kP2/2P5/8/3RK3, set 1...c4 2.Rd4#, 1.Sc7! (2.Qd3#) c4 2.Qd4#, 1.Se7? Rd7!. Extended with a try:
  claude-type2-d4-try, 3Q4/1r3R2/1p6/2pNN3/4kP2/2P5/4P1K1/3R1B2, 1.e3? (2.Bd3#) c4 2.Rd4#, Rd7!; gate PASS. One-unit
  try search (scratch addtry.py) found nothing; the two-unit try (Bf1 masked by e2) came by hand, then g2 and b2 cooks
  fixed (Kg2, bPb6). Verdict: medium, thin (one thematic defence); Bf1 try-only, heavy White. Shown with diagrams.
- 16 Oct: E. Bourd's bench sitting mva0262a (114 steps, 23 solves, three quarter turns each way) doubled our scheme:
  bourd-type2-doubled, 8/8/2PQ1Br1/2KNP3/4k1P1/2pppR2/3qn1P1/8, 1.Sb4! (2.Qd5#) Qa2 Qxd3#, Sf4 Qd4# (set Rxe3#, Rxf4#);
  white correction 1.S~? Qa2!, 1.Sf4? Rxg4!. Re-solved: sound, nothing trimmable. Tool fixes: critique necessity counts a
  double-threat stopper (wPc6) as needed; rerefute.lighten checks every first move (it had offered -Rg6, 13 keys).
- 16 Oct, same sitting mva0262a (steps 115-185): bPd7 for wPc6 (8+8, sound). Then the queen defence replaced by a second
  knight to the same square: bourd-type2-two-knights-c3, 8/3p4/3Q1Br1/1PKNP3/2P1k1P1/r2ppR2/4n1P1/3n1b2, 1.Sb4! Sec3 Qd4#,
  Sdc3 Qxd3#, Sf4 Qd4# (set Rf4#, Rxe3#, Rxf4#); Ra3 (cut on c3) and Bf1 (opened by Se2) make the d3 guard play. Sound, 10+9.
  Our search for knight pairs on f4 (scratch keysel2.py) found nothing; his c3 square came from moving the d3 guard to a line.
- 16 Oct: E. Bourd: "just a knight move can swap 2x2 squares of guards. can you try? ... in general". Hand analysis recorded in
  themes/changed_mates.md (knight guard pairs around K e4, colour argument, line conflict needs blocks). Three scratch searches
  (swap2.py) gave single changes or fatal flaws (8/3N1r1n/4B3/1pK5/2pBkp2/1r3R2/4P1N1/8: 1.Sh4! Rxf4# -> Bf5# twice, set Rf5+
  unprovided). No 2x2 yet; next: self-block defences instead of unguards.
- 16 Oct: "go for it" (2x2 knight swap). Database scan (knight keys with two set/key changes, 16 problems) found the pure
  swap in Strebkovs 2003 (psis-c1d0392e2e). Built claude-knight-swap-2x2-scheme (hand reasoning + inspector): the 2x2 change
  works as a block; no threat found (searches keysel2/swap2 failed: the key's own flight f4 needs a 4th-rank check, which
  the f-file rook parries). Shown to him as a scheme, not a problem.
- 16 Oct: he asked "you tried and gave up or just stopped": I had stopped with two untried directions (lesson). Continued:
  Strebkovs principle (static guards removed by the set mates' own interference), threat 2.Qe6# found by hand
  (claude-knight-swap-2x2-qe6), still faults (set dual, Ke3 after Qxf5). Not finished.
- 16 Oct: his bench sitting mva8vaxu (168 steps): bourd-sef2-two-cuts, 8/2pK4/6R1/5kpP/4Np2/3NRB2/4n3/b5r1, 1.Sef2!
  (2.Be4#) Sc3 Re5#, Sg3 Bg4# (set Rf6#, Rxg5#). He reported the bench's "S~ random" for Sd4/Sc3 as a bug: fixed in
  chesscomp/analysis.py and docs/analysis.js (a random mate must work with the piece removed), test added, bench republished.
- 16 Oct: his next step 8/3K4/3B2R1/5kpP/4Np2/4RB2/4n3/b5r1 (Bd6 for Sd3 + c7, 7+6, same play). Bug he reported: the
  bench diff said "was sound, 1.Sef2!, now sound, 1.Sf2!" for the same move; docs/analysis.js now compares keys by from-to
  (solveSummary.keyIds). Bench republished.
- 16 Oct: "go try to compose next theme" (his third way of 2x2 changes: one piece, two mates, one excluded per phase).
  Hand design: Qd1, Ke4, the king d2-e2 exchanges the queen's lines (diagonal shut, file open, threat Qd4#); pairs one Black
  unit can free listed by hand (Sf6: g4+d5, Se1: d3+f3). Scratch type3 searches (jobs 131-184, 280 s each) placed the
  stoppers. Scheme: claude-type3-queen-lines-scheme, 7b/8/5n2/R7/4k3/1p2P3/3K4/1R1Qn1N1 (two random knights). Did not stop:
  Bc8 for Bh8 makes 1...Sd7 the f6 knight's only defence: claude-type3-queen-lines, 2B5/8/2N2n2/8/2P1k3/1p2P3/3K4/1R1Qn1N1,
  1.Ke2! (2.Qd4#) Sd7 Qd5#, Sc2/Sf3 Qd3#, Sd3 Qxd3# (set Qg4#, Qf3#), try 1.Kxe1? Sd7!; sound, gate PASS, untrimmable.
  Failed: a specific e1-knight defence (pins check in the diagram; Sd3 always blocks; no other second unit found by search).
  Tools: chesscomp.compose.type3 (new, tested); critique piece_necessity ranks new key-phase duals first (Sg1 was reported
  set-play-only though it shuts Qh1# after the key).
- 16 Oct, his answer: king -> pawn, swap directions, Rb1 too bad, Sd3 annoying (single defence; a threat off the queen line;
  short queen mates cannot be blocked). Hand: rotated scheme Qh4/Pg4/Ke5, bRf8 (f5/f4), bSc6 (e7/d4), Bh3/Sc5 threat sketch;
  type3 (new options NOQTHR, QUIET; tested) runs 201-244: claude-type3-pawn-g5, 2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8, 1.g5!
  (2.Sd3#) Rxc8 Qf4#, Sb4 Qd4# (set Qg5#, Qe7#), sound 6+6, gate PASS. Failed: the Qh5 direction (no non-queen threat), a
  quiet single rook defence.
- 16 Oct: "insert board rotations a bit more ... to consider how to replace pieces with pawns. But that requires
  restructuring". Scans (scratch pawnify.py, type3 scorer): no one/two-unit pawn swap on claude-type3-pawn-g5; hand analysis
  of pawn directions in the g4-g5 geometry; type3 PAWNY option (tested); runs 251-264: claude-type3-pawn-g5-pe3
  (2B2r2/1N6/2n3p1/2Npk3/6PQ/K3P3/8/8, sound, same play, a trade not a gain); lighter field (Pc5, Sf2) lost the rook's change.
  Rule written into compose (Shifts and rotations: rotate to let pawns work).
- 16 Oct: his bench sitting mva9ts5k (13 steps, 4 solves): bourd-type3-pawn-g4, 1B6/5r2/1N6/1Kn3p1/2Npk3/6PQ/4P3/8, shift down
  + Bb8 turns 1...Rxc8 into 1...Rc7; re-solved, sound 7+5. His next direction (threat due to f3, mates on e3/d3): type3
  THRSQ/KEYSQ options (tested), four runs, nothing; e3 has no single-unit pair with the diagonal squares.
- 16 Oct: "find a scheme with the pawn moving the other way like in the bench": his sitting mvattjff (8 steps: Qg4, Pf4,
  Kd5, f4-f5, two ccw turns, bSb4). Hand: pair list for Qb5/Pc4/Ke4; type3 runs 281-304 (new MUTATE option, PAWNY parse fix,
  tested): claude-type3-c5-flights-scheme (mutate, two flights given, both answered; cooked, 9+3). No threat version.

## Session 16 Oct 2026: the bench on his phone
* E. Bourd on mobile: portrait "annoying because of scrolling", landscape "doesn't work at all" (the board was taller than the
  screen and catches touches, so nothing below it could be reached). docs/bench/index.html: the board is sized by the screen
  height as well as its width (landscape: board left, palette and tools beside it, Solve pane on the right, all on one screen);
  portrait: compact palette (7 per row), icon-only transforms, a Solve button under the board that scrolls to the report.
  Checked with Playwright at 385x700 and 830x310. Bench republished (version 34).
- 16 Oct: his bench sitting mvbgkei9 (38 steps, 6 solves): bourd-type3-c5-threat, 1.c5! (2.Qc4#) Sc6 Qd3#, Be6 Qxe2#, sound
  11+11, gate PASS; judged (medium content, heavy, many plugs; wPg3 removable, verified). Tool fix: trim now refuses a removal
  that adds a defence (it had offered -bPc2, which keeps the knight's defence single), tested.
- 16 Oct: judged his bourd-type3-c5-threat; on his questions: removal table (scratch why.py) -> bourd-type3-c5-threat-18
  (22 -> 18 units, same play, verified); his Qh5 idea completed by type3 QUIET (claude-type3-c5-blackqueen, 7+7, sound); his
  Bh5/Sh4 idea: two runs, nothing. Compose: "Reduce by chains".
- 16 Oct: "try another type ... another 2x2": the knight guard swap (his idea, Strebkovs model). type3 gained MP=any and
  BYMOVE (tested on Strebkovs); run 334 gave a sound 5+4, then bPg3 replaced the black bishop: claude-knight-swap-c2.
- 16 Oct: his scheme mvbifzbn (two rooks, e3/e4 guard selects bishop or knight mates); he wants a threat. Hand: threat c3#,
  key Sg4-f2; type3 runs 341-394 (MP=any, KEYSQ): best claude-two-rooks-c3-scheme (single changed defences Rb3/Rc1, four
  refutations). Not finished. Tool: type3 warns on illegal seeds (three knights cost four rounds).
- 17 Oct: his bench sitting mvbno7uo (26 steps, 2 solves) finished the two-rook scheme with a threat: bPe3 (no fxe3), a rook
  threat needing f4 (his d3 before the rotation), board turned, Ka6/a5/b6 patches: bourd-two-rooks-sg6-bench, 1.Sg6! (2.Rf4#)
  Rh4 Sg5#, Rf1 Sd6# (set Bxf5#, Bd5#), sound 8+7. Judged (medium: one 2x2 change); reduced to bourd-two-rooks-sg6 (8+5):
  -wPe5 (superfluous probe pawn), Ka3+wPa2 for Ka6+a5+b6; gate PASS, trim nothing; separate.py: no third pair.
- 17 Oct: "lets try another type of 2x2 changes": battery key (front knight e6/f3/c6/g6) and flight-giving key (queen
  key, mates by the queen covering the flight; try/key separated by flights). type3 gained KMP, FLIGHT, TRY, MP=key and a
  distinct-mates rule (tests). 28 runs (401-428), no sound 2x2; scans found both basic forms published (Cuppini 2003
  battery, Marandyuk 2005 flight, 12 units). Obstacles and the three-phase flight plan in changed_mates.md.
- 17 Oct: "lets switch to a problem with batteries ... just 2 variations ... then tries". Runs 429-436 (type3 with KMP) found
  nothing; hand design reached claude-battery-fleck-scheme (sound, double threat, thematic mates are the threats).
  Recorded the structural obstacle (adjacent discharges cannot be selected; distance discharges threaten).
- 17 Oct: his bench sitting mvcc8z65 (71 steps, 7 solves): the queen-held battery (bourd-queen-unguard-battery-scheme).
  New tool chesscomp.compose.battery_guards (tested): only a queen, on f5 (Rc2/Sf2) or b5 (Sb2/Re2), does it for Kd4/Sd5/Rd8.
  claude-rook-knight-queen-unguard-scheme has the thematic pair; the threat is still open. His plan for the next batteries
  recorded (lessons.jsonl).
- 17 Oct: "try rotating, changing pieces and more": postsearch gained KMP (named defences mated by the front piece); runs
  501-528 over rotations/mirror; by hand from the 180-degree hit to a clean post-key, claude-queen-unguard-postkey-c4 (single
  threat, two thematic defences, no holes/duals). No key: the threat c4# does not need the rear queen.
- 17 Oct: "go a bit more": the holder may reach the line only at d4 (bPe3), the threat needs Qd1 (Pc5 for Bc5), cooks removed one
  by one: claude-queen-held-battery-qd1, sound, 1.Qd1! (2.c4#) Qxc7 Sb3#, Qxf7 Sf3#, Qf5 Sxf5#; gate FAIL (key from g1, out of
  play). Unmasking 1.Bd3-g6 nearly works (try 1.Bf5? exf5!) but 1.Bh7 and 1.Bc4+ cook.
- 17 Oct: "Go next scheme" (pawn battery Qb1/c2 v Ke4, single/double step): battery_guards with a pawn front (rook d7:
  Ba7/Bf7, Ba7/Se7; rook d6: Bb6/Be6, Se6/Sb6); post-key play found at once (runs 601-602). Key: the holder interposed on
  d3 is pinned, so 2.c3+/c4+ Rd3 + threat cooks every key that leaves the threat; queen-move threats (Qe1/Qh1, rook unpinned
  interposes) need d2 blocked and every blocker failed; a rook pinning c2 (Rg2/Ka2) and a knight holder failed too
  (lessons). unmask_search found 1.Sg1-h3! (2.Sg5#) Rxa7 c3#, Rxf7 c4#: claude-pawn-battery-rook-holder, sound 7+7, gate PASS,
  static key (a scheme). Thematic tries worked out (e3 guarded by Ba7 + key piece; a try blocking c4), not yet built.
  Tools: postsearch EMPTY=, battery_guards knight holder (tested).
- 17 Oct: his bench sitting mvcop42d (311 steps, 72 solves) finished the pawn battery: bourd-pawn-battery-queen-sd2,
  1.Sd2! (2.Bf3#) Qb5 e4#, Qxb8 e3#, tries 1.Sxg5? Qb5!, 1.Sxg3? Qxb8! (the tries' added error: a capture flight on a square
  the thematic guard protected). Holder attacks the rear (Qb3 v Qd1) instead of interposing; key vacates the double-step
  square. 13+13, dual 1...Qb7. "the solution random move again is somewhat bad": both solvers now require the departure to
  defend before calling moves random (test).
- 17 Oct: "the position is illegal, so its a fatal flaw": retro check illegal_position (core, critique, gate, all searches,
  bench), tests/test_legality.py. Then "lets go next scheme anyway": bishop-knight battery.
- 17 Oct: bishop-knight battery: battery_guards how=rear/both (+ post-capture fix, test); runs 801-834. No sound play yet:
  colour forces rook/knight/queen guards; knight holders' advance interposition cuts their guard; the queen that answers it
  makes every discharge a solution (lessons).
- 17 Oct: showed claude-bishop-knight-battery-postkey (scheme, no key). E. Bourd: "a bit too clumsy, but it can work"; he
  continues on the bench (mvculjk2: knight holder on e3, Sxc2 Sb4#, Sxg4 Scd4#), cleaning up, a decent threat, no queen.
- 17 Oct: his bench sitting mvculjk2 (320 steps, ~100 solves) finished the bishop-knight battery: bourd-bishop-knight-battery-bh7,
  1.Bh7! (2.Sg6#) Sb6 Se8#, Sxe3 Sh5#; tries 1.Be8? Sb6!, 1.Bh5? Sxe3! (the key bishop blocks one discharge square each).
  Bench fix: no S~ in the solution line when only the set play has a random move; duals counted among defences only.
- 17 Oct: "lets try bishop knight battery with 1 square from the king": runs 901-934; post-key play found
  (claude-bishop-knight-adjacent-postkey, holder Sf5 to g7, Sd4 Se8#, Sxe3 Sh5#, threat Sc6#); no key yet (lessons).
- 17 Oct: his bench mvcxwk0k (adjacent knight, Bc3/Sd4 v Ke5, holder Sd5 attacking the rear): "try to finish". Runs 941-974 and
  a one-unit addition sweep: draft 8/1p4K1/1R1Pp3/N2nkP2/2BNP3/2B1PP1b/8/8 has keys Be2 and Bd3 (Bf1 kills the other retreats).
- 17 Oct: "try to finish whats in the bench" (he went ahead to compare): his 1.Bd3! version, sound; trimmed to 21 units
  (bourd-bishop-knight-adjacent-bd3, Ka7, -pe7 -ph7); sweeps found no single unit replacing two cook-stoppers.
- 18 Oct: his bench mvcxwk0k end: the adjacent battery shifted a file left (bourd-bishop-knight-adjacent-bc3, 1.Bc3!,
  17 units against 21, no a6 plug, Sa2 with set Se2~ Sc3#). Sound, legal, trim nothing, gate PASS. "geometrically it
  also looks nice ... the knight follows that way"; "lets go next scheme": bishop-rook battery.
- 18 Oct: bishop-rook battery (his order). Tools: setplay_search (battery set play, NODOUBLE; test), freethreat EMPTY=.
  Findings (lessons): four single discharges per field side; knight holders with a shared threat square fail by
  overlap; rank-2 rook holders are cut by Rc2; a1-rook holders never release. Post-key scheme
  claude-bishop-rook-battery-postkey (bBb1 holder: Bg6 Rb6#, Be4 Rb4#, threat Qd6#), no key yet (discharge cooks).
- 18 Oct: his bench mvdxk1kq: weaker pieces, Kd4, battery Bg1/Rf2, holder Sh3 capturing guards (bourd-bishop-rook-battery-postkey,
  10 units, threat Rd5#, Sxf4 Rd2#, Sxg5 Re2#). Key by king mask 1.Kf5-g4! works but check discharges cook (lesson);
  four plugs did not cure it. Next: restructure (holder landing near the king, or interposing holder).
- 18 Oct: bench fix: no threat after a checking first move (analysis.js phaseAfter and dualAvoidance; Python already right);
  bench republished. His bench mvdxk1kq finished the bishop-rook battery: bourd-bishop-rook-battery-ke2, 1.Ke2! (2.c3#)
  Sxc7 Rf5#, Sxd6 Rf4#, Bc4+ Rxc4#; trimmed -bPg5 to 16 units; sound, legal.
- 18 Oct: his bench mve0b8u3 (274 steps): Kc5 version, 1.Bb7! (2.Bb6#) with the thematic try set Bd5? Sxf6!, Be4?/Bf3? Sxe5!
  (bourd-bishop-rook-battery-kc5-bb7); fatal promoted force (Ba5+Bg1 dark), structural (lesson). Repairs tried (Rc6 threat,
  Pa5, Qa5, unmask_search: Sb3 threat with a b6 flight) failed.
- 18 Oct: his Qg1 repair of the Kc5 version (bourd-bishop-rook-battery-kc5-qg1, sound, gate PASS; -wPh2 removes the
  four-fold Qg2+ refutation). Critique fix: a unit the solution needs (plug) that also plays a try is a cook-stopper,
  not 'try-only' (test).
- 18 Oct: his explanation of the Kc5/Qg1 problem (white correction, anticipatory closure, wPh2 for the unique B~ refutation):
  record restored to his FEN with Ph2. Tools: trim --tries (keeps every try and its refutations); critique reports the
  white correction when king tries share the threat, once, and a refutation shared by corrections as minor (test).

## Session: originals portfolio (18 Oct 2026, branch claude/bold-pasteur-2o7mjx)
* E. Bourd asked for all problems he composed in our sessions that could go to magazines as originals.
  knowledge/originals.json lists 52 of his (or joint) #2s from knowledge/problems.json with a tier and a one-line
  verdict: 13 send first, 29 sendable, 4 thin, 5 failing the current gate (useless key piece, out-of-play key,
  simple block), 1 already public (bourd-novotny-b4-bc5, FEN in the 18 Oct blog post). Left out: schemes, post-key
  positions, bench demonstrations he called schemes, illegal/promoted positions, superseded versions. Two verified
  trims used (queen-pin self-pin 17 units, Grimshaw d4 8+8). tools/originals.py re-gates each entry and writes
  docs/originals.html (published as https://claude.ai/artifact/9xKrJSL1xQSixJsG79wAJ6). Anticipation was checked
  as identical position only; yacpdb/PDB search still to do before sending.
* Same session: solutions on the portfolio rewritten album-style by the solver (set play only for defences that recur,
  only the tries the notes name or originals.json lists, key with threat and grouped variations, 'S~' for random
  moves); his notes moved to a separate 'Explanation'. E. Bourd's new rule: a single phase without tries or changes is
  not for publication unless very complicated or pretty. Critique rule 'single phase' (fatal in the gate): no changed
  mate, no thematic-try plus, and no non-checking try refuted by a key defence. New tier 'single' (Be4 three captures,
  Ra5 two-knight unpin, Ke2 battery). Of the published daily posts, 14 Oct (a guard for f6) and 18 Oct (Novotny d6)
  would now fail it. Test test_single_phase_needs_tries_or_changes.
* Same session, his request: portfolio solutions as in a publication, not a computer listing. tools/originals.py now
  prints set play, the named tries and the key with the thematic defences in one fixed order in every phase, by-play in
  brackets after the key's thematic play, and lines 'Changed' (1...X 2.A# (set, 1.Y?) -> 2.B#) and 'Transferred'
  (a mate moving to another thematic defence). Thematic = key defences whose mate changes (a shared dual is no change)
  or that refute a named try; originals.json 'thematic' overrides it for nine problems ('Sf5~' = random moves, 1...S~).
  1...Rxe6 (try) and 1...Re6 (key) count as one defence. Open question for him: whether to keep the by-play brackets.
- 18 Oct: his airy version (bourd-bishop-rook-battery-kc5-airy): no black queen (Bf1, B~ Bg2+), no wPh2/wPc4, c4 free;
  sound, gate PASS, trim --tries nothing.
* Same session: thematic variations lettered [a], [b] (one letter per defence across phases, random group shares one;
  a try refuted by a thematic defence shows its letter) and set in bold; tries that capture are left out of the
  solutions. Cost: 1.Qg2! (two captures on e5) loses its middle phase 1.Qxh1?; thematic capture tries also go from
  1.Bh7! (Bxg4?), 1.Bxh6! (Bxe3?), 1.Kf8! (Kxg6?), 1.Bd8! (Bxe5?), 1.Bc3! (Bxc5?), 1.Ra5! (Rxa2?), 1.Bxe7! (Bxb4?).
* Same session, his correction: random tries do not count for the single-phase rule, only thematic tries or changes.
  The critique no longer takes 'try set' or 'distinct refutations' as a second phase. Three more problems move to the
  'single' tier (1.Bd8! knights half-pin, 1.Rg6! three blocks on b5, 1.Bd3! unpin on c3). The airy Kc5 battery
  (bourd-bishop-rook-battery-kc5-airy, merged from main) replaces the Qg1 version in the portfolio; originals.json
  gains 'skip_tries' and hand-listed tries now lead in their order. Test test_random_tries_are_not_a_second_phase.
- 18 Oct: rook-bishop battery started: geometry and colour analysis (lesson), setplay_search HOLDER mode; no scheme yet;
  proposed crossing discharges (Ke6, Bf4 for d6, Bd4 for f6 through e5).
- 18 Oct: rook-bishop battery, his objection to 1...Sxc5 2.Bxc5# (recapture) met by a black light-bishop holder c6: 1...Bxb5 2.Bc5#, 1...Bxd7 2.Bd4# (scheme claude-rook-bishop-bishop-holder-scheme). Post-key with 2.f8=S# after 1.f7 (claude-rook-bishop-f7-draft) is cooked by the left discharges plus a knight check after 1...Be4; cook-stoppers in progress. Fixed a stuck wait loop (pgrep matched its own command line).
* Same session, his request ("way too verbose"): the main solution is thematic play only - set play when it changes,
  each thematic try once (refuted by a thematic defence, or with a changed mate) showing only its changed mates and the
  refutation, the key's thematic variations, the Changed line. A muted By-play row at the bottom holds repeated tries
  ("1.Bd3?/Bg2?/Bh1? as 1.Bf3?"), tries refuted by non-thematic moves ("1.Bg6? fxg6!") and the key's other variations.
  Capture tries stay hidden but still decide which defences are thematic.
- 18 Oct: first sound rook-bishop problem (claude-rook-bishop-battery-kg8, then -kg8-rd8, gate PASS): 1.Kg8! (2.f8=S#) Bxb5 2.Bc5#, Bxd7 2.Bd4#; tries 1.Ke8? Bxd7+!, 1.Kg7? Bd4+!. Cook-stoppers bBb6, bSb3. Next: a second layer (changed mates by switching which side of the battery is open).
- 18 Oct: E. Bourd turned the rook-bishop scheme into a half-battery problem on the bench (bourd-rook-bishop-halfbattery-bg5, gate PASS): 1.Bg5! (2.Be7#) Bxa5 2.Bb5#, Bxc7 2.Bc4#, Sc6 2.Sc4#, dxe6 2.Sb5#; tries 1.Bb5? Bxc7!, 1.Bc4? Bxa5! (the refutation takes the non-threatening knight).
- 18 Oct: rook-knight battery (next in his series): claude-rook-knight-battery-d7, gate PASS, 1.d7! (2.d8=S#) Sxf6 2.Sc8#, Sxf4 2.Sc4#; tries 1.f7? Sxf4!, 1.Ra7? Sc7!. Scheme found by setplay_search (holder d5, NORECAP); setplay_search fixed (full-board crash) and given NORECAP, with tests.
- 18 Oct: E. Bourd's knight battery with a queen rear (bourd-queen-knight-battery-bg5, gate PASS): 1.Bg5! (2.Bf6#) Sxf5 2.Sc7#, Sxf3 2.Sc3#; tries 1.Qb6? Sxf5!, 1.Qb4? Sxf3! with changed mates Qe3#/Qe4#.
- 18 Oct: E. Bourd's single-threat version (bourd-queen-knight-battery-bg5-b2, gate PASS): bBb2 guards d4, the tries 1.Qb6?/1.Qb4? threaten only 2.Qc5#; cost: the key piece c1 attacked by b2 (no other bishop square works, tested d2/d8/h4).
- 19 Oct: his battery list complete (pawn, B+S, B+R, R+B, R+S/Q+S). Started the royal battery: geometry lesson recorded, holder searches (rank and diagonal) found no single-holder scheme; queen-heavy hits use control of a king square instead.
- 19 Oct: royal battery with control. Scheme claude-royal-battery-control-scheme (1...Sxd2 2.Kd3#, 1...Se1 2.Kc4#); sound diagram claude-royal-battery-bb5, 1.Bb5! (2.Sd3#) Sxd2 2.Kd3#, Se1 2.Kc4#, Bxb5 2.Rxb5#, gate FAIL (useless key piece, single phase: set 1...Sxd2 2.Kc2#/Kxd2# has a dual). Loaded-battery diagrams all cooked by discharge checks; diagsearch on the core found only flight-taking keys.
- 19 Oct: on E. Bourd's suggestion, the holder on f5 (his bench sitting): schemes claude-royal-battery-f5-scheme (Sxe7 Kc4#, Sxg3 Kd3#, 8 units) and claude-royal-battery-f5-scheme-se3 (Sxe7, Se3); freethreat finds 2.f2-f4#, keyfind no key (discharge checks before the key cook every post-key).
- 19 Oct: E. Bourd solved the key on the bench (bourd-royal-battery-sd8): 1.Sd8! (2.Sf7#) Sxe7 2.Kc4#, Sxh4 2.Kd3#, Bd5 2.Sg6#; his bSg7 removed (not needed, attacked the key knight). Looking for an extension: tries by a queen as rear piece (1.Qxh1 there gives Sxe7 2.Qe4#, Sxh4 2.Qd5#), the pin try 1.Rh5? (2.Kd3#).
- 19 Oct: tests split on E. Bourd's request: `python -m pytest -q tests` is the fast run (296 tests, 88 s, all stored keys), `--full` adds the 16 slow tests (7 min) and records its date in knowledge/last_full_tests.txt; the fast run reminds after 2 days (tests/conftest.py).
- 19 Oct: E. Bourd's royal battery with tries (bench, steps 332-540): 1.Rg5! (2.Be5#) Rc5 2.Ke6#, Rc2 2.Kf5#; tries 1.Re6? Rc5!, 1.Rf5? Rc2!. Lightened from 22 units/11 pawns to 19/7 (bourd-royal-battery-rg5, gate PASS): bPb6, bPb7 out, Sb2 for Pb3+Pe2 (adds 1...e2 2.Bf2#). Tested 1.Re7! as key (purer for Rc5, but 1.Rf5? gets two refutations), Sa2 and Sa8 both needed.
- 19 Oct: rook-pawn battery (his choice). setplay_search with Ra2/Pd2 v Ke2 and knight holders found nothing (the geometry: pawn guards never reach the field). Scheme by hand: claude-rook-pawn-battery-scheme, two black bishops as interposers, the step that cuts the remaining one mates (d3 / d4).
- 19 Oct: rook-pawn battery towards a problem: dark-bishop moves off the long diagonal (b8-h2 only) parry nothing; a capture works (1...Bxf4 takes the knight's g2 guard, needed in 2.Sg4# but on the check line in the battery mates). Near miss claude-rook-pawn-battery-postkey, hole 1...Bf1 (the light path through d3 runs on to f1 and cuts the 1st-rank rook).
- 19 Oct: rook-pawn battery, 16 more freethreat runs (light bishop b5/g6, dark capture Bxf4, mirrored Ka2, Kg2 with two captures): best stays the post-key with one hole (claude-rook-pawn-battery-postkey); obstacles recorded as a lesson.
- 19 Oct: rook-pawn battery, three last attempts (his limit): (1) light bishop from the h7 side with new threats: holes or no light defence; (2) Bf1 cured with Rg1+Sh3 and Bg7 (1...Bxh6 2.d3#): sound post-key claude-rook-pawn-battery-postkey-rg1, but no key (1.d3+/1.d4+ then the rook takes the interposer); (3) unmasking key via unmask_search (new EMPTY option): 1.Sf2-h3! unique, flight Kxg1 in the diagram. Given up. Critique fix: the unit making the mating move takes part (wPd2 had been called a cook-stopper), tests/test_critique_battery_front.py.
- 19 Oct: E. Bourd solved the rook-pawn battery on the bench (steps 620-706) where Claude had given up: bourd-rook-pawn-battery-bh2, 1.Bh2! Bg5 2.c4#, Bg4 2.c3#, 1.c3+? Bxa2!, 1.c4+? Bb2!. Claude's lesson 'no key with the battery loaded' corrected. Critique fix: an interference try refuted by a king move is not a thematic try (his 1.Sg3? Kg2! had passed the single-phase gate).
- 19 Oct: his request, the same battery with the king one square closer: claude-rook-pawn-battery-ke2-be4, 1.Be4! (2.Rh2#) Bh4 2.c4#, Bh3 2.c3#, try 1.Rh2? Bh3!; 11 units, gate PASS. With Ke2 the discharge abandons d3 (Pc2's guard), so the pre-key discharges fail to Kd3 and bPa3 is not needed; the key piece takes d3 over. Rook-arrival keys were idle or gave a flight.
- 20 Oct: his request for a different threat and mechanism with room for two unified tries: claude-rook-pawn-battery-fcut-sh3, 1.Sh3! (2.Sg1#) Bf4 2.c4#, Bf3 2.c3# (both bishops cut Rf5's f-file guard of f2); sound, 15 units, single phase, static key. About 12 tool searches (freethreat, unmask_search, keyfind); dead ends in the lesson.
- 20 Oct: 'try a bit more' on the f-file scheme: eight unmask_search/freethreat runs for a try pair (masking knight on f3 with Rf8/Rf5 and threat Sg1 or Sg3, queen on f5); no pair. The f3 knight mates itself on g1, Qe1# comes in, Bf6 cuts on its own line. Lesson: the two mates differ only in the f3 guard and the c3/c4 closures.
- 20 Oct: rook-knight battery with extra play (his request): claude-rook-knight-two-lines-scheme (holder Sd5 holds either the battery or Rd2's e-file, 1.Bc5! with tries 1.Bb4? Sxb4!, 1.Ba3? Sb4!, 1.Bf8? Se7!); not yet a problem (diagram flight Kxd6, discharge duals). freethreat THREAT= option (tests/test_freethreat_threat.py). Dead ends: f5 corrector behind the king (double checks only, one-sided), Black rook h5 random defence (support too heavy).
- 20 Oct: 'try different schemes' for the rook-knight battery: (1) knight-landing pairs (e5: Sc4/Sd7, e7: Sc8/Sd5) checked with separate: no try/key pair; (2) mutate with a key leaving the battery line (Ra7): random block, unprovided checks; (3) claude-rook-knight-selfblock-rooks-scheme: threat Qe6#, 1...Rd6 2.Sg4#, 1...Rf6 2.Sc4# (self-block dual avoidance), holes Rxg8/Rf7 from the queen's square.
- 21 Oct: rook-knight battery with the knight adjacent, no flights (his request): claude-rook-knight-adjacent-holder-e3, post-key with threat 2.cxb8=Q# and four motivated defences (Sxg2 2.Sf6#, Sxf5 2.Sf4#, Sc4 2.Bf4#, Bxc7 2.Re8#); no key yet (loaded battery cooks, threat independent of the battery).
- 21 Oct: his small adjacent-knight scheme (bench mvh329m2, holder Sd3, threat Bf5#) finished as bourd-rook-knight-adjacent-bb5: 1.Bb5! (2.Bc6#) Sxf4 2.Sc6#, Sxf2 2.Sf5#, Se5/Sxb4 2.Sc5#; gate PASS, 15 units. Keys bringing a knight to e7 failed (Sc8/Sg8 mate at once, Sg6: discharge-check cooks); masking knight on c4 mates itself; unmask_search with a bishop on c4 found it.
- 21 Oct: daily No. 16 (Dombrovskis): study post on Manolescu 1984-85 (double Dombrovskis, one sole guard Sd4 of e6 taken by a Grimshaw pair). Own attempts: claude-dombrovskis-bd8-kernel (1.Qg7!, sound, no paradox in ~47,000 one/two-unit neighbours), a two-pawn zugzwang from evolve. Kit: themes/references/dombrovskis.md (first reference, tested by tests/test_dombrovskis_reference.py); evolve no longer defaults DEFS to d6,d5 in the modes that need none (tests/test_evolve.py).
- 21 Oct: his bench tries for the adjacent-knight battery (session mvh329m2, steps 35-83, 'Rf5? Rc6? R-somewhere solution'): step 63 + bRb7 (trypair, one unit) = bourd-rook-knight-rd6-tries, 1.Rd6! (2.Sf6#) Sxf4 2.Sc6#, Sxf2 2.Sf5#; tries 1.Rf5? Sxf2!, 1.Rc6? Sxf4!, 1.Rfxb6? Rxb6!; gate PASS, 21 units, static key. Lighter versions failed (wBb6, Kg6); trim: nothing removable.
- 21 Oct: his 'clumped white pawns' remark on bourd-rook-knight-rd6-tries: wPg3 -> bPh4 (sound, 13+8, gate PASS, record updated). trypair with black-only units (one and two, after each removal; second layer on the h4 version) found nothing for c3, d5, e5, g6; reasons in the lesson.
- 21 Oct: his request to trim with the free white bishop and remove wPd5 (not via bPc6): wBe5 for wPe5+wPc3 (12+8), then wPd5 out with black Ba8 (answers 2.Bd5+), bRb7->b8, Sg8->h7: br6/2p2B1N/1p3RP1/4B1K1/1R1NkP1p/3n1p2/2P2P2/1n6, 1.Rd6!, same tries, 11+9, white pawns 8 -> 4, gate PASS (record bourd-rook-knight-rd6-tries updated). unmask_search: retype mutation, PAWNW, importable, test; compose skill step 6a (trim by reassigning jobs).
- 21 Oct: his verdict on bourd-rook-knight-rd6-tries: a decent clear theme with tries, commendation level in an ordinary tourney; 1.Rfxb6? is not a real try. My verdict (no placing) was too harsh; judge checklist calibration line added.
- 21 Oct: new concept, double-check mates (his request). DB scan: 78 #2s with a double-check mate (Bie 2001, Vasilenko/Shanshin, Barnes). freethreat DOUBLE mode (test). Scheme claude-double-check-two-bishops-scheme: 1.Sf7! (2.Sg5#) Be3 2.Sd2#, Bd5 2.Sd6#, 12 units: bPc5 forces double checks, the mating knights cut white guard lines whose squares the defences self-block. Single phase; a pure try refuted by Bd5 came with Kxf3.
- 21 Oct: bishop-rook double checks (his request): Rc3 v Ke5 cannot separate Rc5/Re3 (dark cut lines); Rd4 v Ke5 with Bc6 and Qc2 gives three double-check mates (Sd6 Re4#, e6 Rd5#, Kf6 Rd6#), claude-bishop-rook-double-checks-scheme, 1.Qa4-c2 unique but flights e6/f6 in the diagram. About 20 freethreat/unmask_search/keyfind runs.
- 21 Oct: his verdict on claude-bishop-rook-double-checks-scheme: 'next tier', the diagram flights worth it (CLAUDE.md fatal list and judge checklist amended with a tier rule). No single unit provides 1...Ke6 in the set.
- 21 Oct: his masked-battery idea (Rc3, black piece on d4): bishop mask selecting Re3/Rc5 by line cuts (claude-masked-bishop-rook-postkey, post-key only); single rook checks cook because the mask is pinned once the rook moves; knight-on-f6 interposer runs found holes. Rook mask, knight mask and free DOUBLE runs gave partial play.
- 22 Oct: his 'continue, reduce the symmetry, replace pieces, rethink the threat' on the masked battery: claude-masked-battery-bb2, 1.Bb2! (2.Re3#, the rook check that pins the mask) Bf2 2.Rc5# (double check), Bxc3 2.Bxc3#, Sf6 2.Qxf6#; gate PASS, 13 units. Four freethreat runs (asymmetric named defences, king flight variants), keyfind --patch.
- 22 Oct: 'two thematic double checks, anything less is not it': masked battery with Bb6->Re3, Bf2->Rc5 and a new threat (Qa6/Rf1 guards, threat Sd7), keys by unmask_search: claude-masked-battery-two-doubles-sf6, 1.Sf6! (19 units; sibling 17 units with the key knight attacked). Both double checks set (single phase). About 12 runs (freethreat DOUBLE/NOQ, unmask_search, keyfind, trim).
- 22 Oct: theory of tries for the masked two-double-check problem (his question): pure tries are white self-interferences on the two guard lines (f-file -> Bb6!, 6th rank -> Bf2!); knight on e4 (Sf6 key, Sd6/Sf2 tries) tested: unique key, but diagram flight Kd5 and impure Sd6 refutations.
- 22 Oct: his bench sitting mvjy8awv (84 steps) on the masked battery turned 180 degrees: asymmetric double checks via x-ray squares (Bxc7 -> Rf4#, Bg3 -> Rd6#), pure bishop tries Bd5?/Bf5?. Claude: legal version with Sb6 (bourd-bench-masked-bd7-v1), still cooked by Bc8/Bc4; rook-on-c8 variant gives 1.Bc4 unique with four tries but threat Qd3 too. Tools: trypair loose, unmask_search LOOSE (holes stay strict), test.
- 22 Oct: his bench steps 85-461 (mvjy8awv): shifted versions sound with 1.Bh4 (knight g8), then the knight on g5 (his step 249, 1.Bg4!, pure tries, three black knights). Claude: removal tests found each knight's jobs; 16 unmask_search runs (LOOSE, THREAT=Ng5e6, TRIES pure) gave bourd-bench-masked-sg5-bg4 (bPe7 for Sc8, bBa4 for Qa4, bRd2; 22 units, two knights, gate FAIL only 'useless key piece') and the side road claude-masked-sg5-qh1-keyline (key with a reason, impure Bd5 try).
- 22 Oct: his bench steps 462-713: knight-g5 schemes with Qc7/Ke8 (cooked), then he loaded claude-masked-sg5-qh1-keyline and made both tries pure with bPh3 + wPf7: bourd-bench-masked-qh1-ph3 (12+9, 1.Bg4!), Rc8 variant with the quiet 1...Bc7 (step 707) also sound. Claude re-solved both, trim, and verified wPh3 for bQh1+bPh3 (13+7, sound, by-play dual Sf4).
- 22 Oct: his bench steps 714-900, the key bishop from e4 (his idea). Claude: 10 unmask_search runs over key squares f3/d3/g6/h1/g2; only h1 sound: bourd-bench-masked-e4-bh1, 1.Bh1! (13+8, gate PASS, pure tries kept, the key bishop now in every mate).
- 22 Oct: his bench steps 901-1174: Pb7 -> white knight, shift left, Qh8/pg7/pg3: bourd-bench-masked-sa7-bg1, 1.Bg1! (11+11), every bishop move refuted by its own move; Bf2 sibling with bPh2. Claude: re-solved, removal test of every unit, trytable, scans for replacing Sb8+pa6 and Pb4 (none).
- 22 Oct: his steps 1175-1247: unshifted knight-b7 version with bQa7 (bourd-bench-masked-sb7-qa7-bh1, 1.Bh1!, 12+10), then back to the shifted 1.Bg1 version; later experiments cooked. Claude's verdict asked ('what do you think?').

- 23 Oct (daily No. 18, routine): changed mates; published claude-knight-swap-c2-kd7 (light knight swap, king a5 -> d7). Tool: evolve CHANGED refuses set duals (set_duals, tested). Failures recorded in themes/references/changed_mates.md and lessons.jsonl.
- 23 Oct: theme 'Black unpins a White piece': read Shire, Pachl, Pilchenko/Shavyrin, Ahues, Lincoln in the database; basic scheme claude-unpin-white-queen-scheme (1.Bd7!, single phase); about 30 freethreat/unmask_search runs over self-pin, unmasking, knight, rook and bishop keys and a four-unpin queen pinner; unmask_search gained ALLOWCHECK (tested).
- 23 Oct: 'unpinning of a white knight': three cores (Sd2 on the 2nd rank, Sd2 with a bishop interposer, Sc5 on the a7-g1 diagonal); 16 freethreat/unmask_search runs; claude-unpin-white-knight-scheme 1.Rfd1! (sound, out-of-play static key).
