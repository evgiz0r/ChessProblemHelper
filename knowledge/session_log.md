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
