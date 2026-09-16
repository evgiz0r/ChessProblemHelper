# Changed mates

Settings: bourd-changed-mates-3 (8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8), bourd-changed-mates-4
(1K3b2/1P1p1B2/3r2p1/Q3P1RN/R1n1k2p/3p1p2/4nP2/4Nb2), claude-one-knight-change
(5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3), bourd-one-knight-change (8/2K2p2/6pB/3p1nQ1/3Pk1P1/2P5/4P3/5r2),
claude-one-bishop-change-2 (7n/6b1/1Np5/R7/3Pk1K1/2Q5/8/8), bourd-two-captures-three-phase
(KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n).

Mechanism: one Black effect that yields several mates; a selector per phase; then the threat. Selectors:
Black pawns guarding the mating squares removed one per phase; the queen's post; the key piece giving the
set mates and switching them off by moving; the key piece that moved giving the other mate itself.
Simplest one-defence change: set 1...Sxd4 2.Qe3#, 1.Qf6! 1...Sxd4 2.Qxd4#.
Two units capturing on one square: the capture square on two battery lines (departure opens one, arrival
self-blocks the other); the queen's post selects which departure mates; three phases for one defence.
Fast start for "two pieces defend on the same square": let them CAPTURE a White unit there
(8/3n4/8/3kP3/8/4r3/8/8), then arrange the mates, then the threat.
Traps: the try threat and the key duals coming from the same resource (2Rn1N2/7K/3P4/3k4/pB1p1P2/3n1P2/1p1Q1p2/8);
a set+solution block cooked by any waiting move; a diagram flight that the change needs (queen on g5/h5).
Dead end: blind enumeration for same-piece changes (5M positions, nothing); the composer's 3-unit scheme
plus ONE named changed defence as the criterion succeeded in one pass.
