"""Unique thematic defences (E. Bourd, 14 Oct 2026, on claude-changed-type1-qg8: "I wouldn't call it 6 changed mates.
Realistically all knight moves are the same ... Let's try to make the black knight defense unique").

A named defence is unique when no other move of the same Black unit defends against the threat in that phase: every
other move of it lets the threat mate (the solver marks those variations `threat_repeat`).

    from chesscomp.compose.unique_defence import extra_defences
    extra_defences(phase, ['Se6', 'Se4'])      # -> {'Se6': [...other defending moves of that knight], 'Se4': [...]}
"""
from __future__ import annotations


def extra_defences(phase: dict, defs: list[str]) -> dict[str, list[str]]:
    """For each named defence (SAN, as the solver prints it) found in `phase` (a key or try phase of
    chesscomp.analysis.analyse), the other moves of the same unit that also defend (do not allow the threat)."""
    by_san = {v['defence']['san'].rstrip('+#'): v for v in phase.get('variations', [])}
    out = {}
    for d in defs:
        v = by_san.get(d)
        if v is None:
            continue
        sq = v['defence']['uci'][:2]
        out[d] = [w['defence']['san'] for w in phase['variations']
                  if w is not v and w['defence']['uci'][:2] == sq and not w.get('threat_repeat')]
    return out
