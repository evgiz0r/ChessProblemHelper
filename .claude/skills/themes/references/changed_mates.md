# Changed mates

Settings: bourd-changed-mates-3 (8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8), bourd-changed-mates-4
(1K3b2/1P1p1B2/3r2p1/Q3P1RN/R1n1k2p/3p1p2/4nP2/4Nb2), claude-one-knight-change
(5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3), bourd-one-knight-change (8/2K2p2/6pB/3p1nQ1/3Pk1P1/2P5/4P3/5r2),
claude-one-bishop-change-2 (7n/6b1/1Np5/R7/3Pk1K1/2Q5/8/8), bourd-two-captures-three-phase
(KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n), claude-two-captures-e5 (2R5/3n1p2/1B6/1K1kP1Q1/1P4B1/4rP2/8/8,
daily No. 3).

Mechanism: one Black effect that yields several mates; a selector per phase; then the threat. Selectors:
Black pawns guarding the mating squares removed one per phase; the queen's post; the key piece giving the
set mates and switching them off by moving; the key piece that moved giving the other mate itself.
Simplest one-defence change: set 1...Sxd4 2.Qe3#, 1.Qf6! 1...Sxd4 2.Qxd4#.
Two units capturing on one square: the capture square on two battery lines (departure opens one, arrival
self-blocks the other); the queen's post selects which departure mates; three phases for one defence.
Fast start for "two pieces defend on the same square": let them CAPTURE a White unit there
(8/3n4/8/3kP3/8/4r3/8/8), then arrange the mates, then the threat.
Two captures of the threat's guard (daily No. 3): Sd7xe5 and Re3xe5 both remove d6's only guard. Set mates by
the lines the departures open (Rd8#, Qd2# through e3); 1.Qe7 leaves the g5-d2 line and the mates change to the
knight's unguard of c5 (Qc5#) and the rook's self-block of e5 (Qxd7#). Evolve CHANGED=1 seeded with the core
8/3n4/8/3kP3/8/4r3/8/8 found it in ten minutes; bare cores found nothing. Its hits put a unit on the board only
for a set mate (Rg8 for Rd8#): give that mate to a unit that also works after the key where you can.
His answer to No. 3 (bourd-e4-selfpins, 8 Oct): the same two captures, but on e4 under the queen's rank, so in the
set they self-pin (pin-mates Rd7#/Rd1#, the pinned unit cannot block again) and after 1.Qe6 they unguard b5/c3
(Sxb5#/Bc3#). One Black error per phase. The reason came from a one-rank shift, not from a new unit. A flight on e4
was not possible: its mate needed d5, the phase selector (lessons.jsonl, 8 Oct).
Traps: the try threat and the key duals coming from the same resource (2Rn1N2/7K/3P4/3k4/pB1p1P2/3n1P2/1p1Q1p2/8);
a set+solution block cooked by any waiting move; a diagram flight that the change needs (queen on g5/h5).
Dead end: blind enumeration for same-piece changes (5M positions, nothing); the composer's 3-unit scheme
plus ONE named changed defence as the criterion succeeded in one pass.
