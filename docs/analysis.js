/* chesscomp-web: #2 / s#2 / h#2 analysis in the browser.
   Mirrors chesscomp/analysis.py: set play, tries with refutations, key, variations, duals,
   changed / reciprocal mates, and the dual-avoidance motive.
   Depends on chess.js (Chess class). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('chess.js').Chess);
  else root.ChessComp = factory(root.Chess);
}(typeof self !== 'undefined' ? self : this, function (Chess) {

  const S = s => s.replace(/^N/, 'S').replace('=N', '=S').replace('O-O-O', '0-0-0').replace('O-O', '0-0');

  function boardFrom(fen, turn) {
    const parts = fen.trim().split(/\s+/);
    const placement = parts[0];
    const f = `${placement} ${turn} - - 0 1`;
    try { return new Chess(f); } catch (e) { return null; }
  }

  function legal(c) { return c.moves({ verbose: true }); }

  function matesIn1(c) {                       // side to move mates at once
    const out = [];
    for (const m of legal(c)) {
      c.move(m);
      if (c.isCheckmate()) out.push(m);
      c.undo();
    }
    return out;
  }

  // identity of a move: piece + origin + destination, so the same unit is tracked across phases
  const mid = m => `${(m.piece || '').toUpperCase()}${m.from}${m.to}${m.promotion || ''}`;

  /* Does White force mate within n moves? (direct mates only, n = 1 or 2) */
  function whiteMatesIn2(c) {
    for (const w of legal(c)) {
      c.move(w);
      const ok = blackAllAnswered(c);
      c.undo();
      if (ok) return true;
    }
    return false;
  }

  function blackAllAnswered(c) {               // Black to move: is every reply mated next move?
    if (c.isCheckmate()) return true;
    if (c.isStalemate() || c.isInsufficientMaterial()) return false;
    for (const b of legal(c)) {
      c.move(b);
      const dead = c.isGameOver() && !c.isCheckmate();
      const ms = dead ? [] : matesIn1(c);
      c.undo();
      if (!ms.length) return false;
    }
    return true;
  }

  function solvesShort(c, mv) {                // a first move that mates at once cooks a #2
    c.move(mv);
    const short = c.isCheckmate();
    c.undo();
    return short;
  }

  /* Analyse one first move: threat, variations, duals. */
  function phaseAfter(c, first, kind) {
    const sanFirst = S(c.move(first).san);
    const ph = { type: kind, first: sanFirst, firstId: mid(first), from: first.from, to: first.to,
                 threat: [], variations: [], refutations: [] };
    // threat: what White plays if Black does nothing
    const nullFen = c.fen().replace(/ b /, ' w ');
    let nc = null;
    try { nc = new Chess(nullFen); } catch (e) { nc = null; }
    if (nc && !nc.isCheck()) ph.threat = matesIn1(nc).map(m => ({ san: S(m.san), id: mid(m) }));
    const threatIds = new Set(ph.threat.map(t => t.id));
    for (const d of legal(c)) {
      c.move(d);
      const dead = c.isGameOver() && !c.isCheckmate();
      const ms = dead ? [] : matesIn1(c);
      const conts = ms.map(m => ({ san: S(m.san), id: mid(m), from: m.from, to: m.to, uci: m.from + m.to }));
      c.undo();
      const ids = new Set(conts.map(x => x.id));
      const repeats = ph.threat.length > 0 && [...ids].some(x => threatIds.has(x));
      const v = { defence: S(d.san), defFrom: d.from, defTo: d.to, uci: d.from + d.to,
                  conts, dual: conts.length > 1, refutes: conts.length === 0, threatRepeat: repeats };
      ph.variations.push(v);
      if (v.refutes) ph.refutations.push(S(d.san));
    }
    c.undo();
    return ph;
  }

  function setPlay(fen) {
    const c = boardFrom(fen, 'b');
    if (!c || c.isCheck() || c.isGameOver()) return null;
    const ph = { type: 'set', first: null, threat: [], variations: [], unprovided: [] };
    for (const d of legal(c)) {
      c.move(d);
      const dead = c.isGameOver() && !c.isCheckmate();
      const ms = dead ? [] : matesIn1(c);
      const conts = ms.map(m => ({ san: S(m.san), id: mid(m) }));
      c.undo();
      if (!conts.length) ph.unprovided.push(S(d.san));
      else ph.variations.push({ defence: S(d.san), uci: d.from + d.to, conts, dual: conts.length > 1,
                                threatRepeat: false, refutes: false });
    }
    return ph;
  }

  /* changed / reciprocal continuations between phases (real defences only, unique mates) */
  function defMap(ph) {
    const m = {};
    for (const v of ph.variations)
      if (v.conts.length === 1 && !v.threatRepeat) m[v.uci] = { id: v.conts[0].id, san: v.conts[0].san, def: v.defence };
    return m;
  }
  function label(ph) { return ph.type === 'set' ? 'set play' : `${ph.type} ${ph.first}`; }

  function relations(phases) {
    const changed = [], reciprocal = [];
    for (let i = 0; i < phases.length; i++)
      for (let j = i + 1; j < phases.length; j++) {
        const A = defMap(phases[i]), B = defMap(phases[j]);
        const common = Object.keys(A).filter(k => k in B);
        for (const d of common)
          if (A[d].id !== B[d].id)
            changed.push({ defence: A[d].def, from: A[d].san, to: B[d].san, phases: [label(phases[i]), label(phases[j])] });
        for (let x = 0; x < common.length; x++)
          for (let y = x + 1; y < common.length; y++) {
            const d1 = common[x], d2 = common[y];
            if (A[d1].id === B[d2].id && A[d2].id === B[d1].id && A[d1].id !== B[d1].id)
              reciprocal.push({ defences: [A[d1].def, A[d2].def], phases: [label(phases[i]), label(phases[j])] });
          }
      }
    return { changed, reciprocal };
  }

  /* Why does each sibling mate fail after a given defence? (dual-avoidance motive) */
  function dualAvoidance(fen, keyMove) {
    const c = boardFrom(fen, 'w');
    if (!c) return [];
    c.move(keyMove);
    const nullFen = c.fen().replace(/ b /, ' w ');
    let threatIds = new Set();
    try { const nc = new Chess(nullFen); threatIds = new Set(matesIn1(nc).map(mid)); } catch (e) {}
    const defs = [];
    for (const d of legal(c)) {
      c.move(d);
      const ms = matesIn1(c);
      c.undo();
      if (ms.length === 1 && !threatIds.has(mid(ms[0]))) defs.push({ d, m: ms[0] });
    }
    const out = [];
    for (const { d, m } of defs) {
      const item = { defence: S(d.san), mate: S(m.san), avoided: [] };
      for (const other of defs) {
        if (other.m.from === m.from && other.m.to === m.to) continue;
        c.move(d);
        const cand = legal(c).find(x => x.from === other.m.from && x.to === other.m.to && (x.promotion || '') === (other.m.promotion || ''));
        if (!cand) { c.undo(); continue; }
        const osan = S(cand.san);
        c.move(cand);
        if (c.isCheckmate()) { item.avoided.push({ mate: osan, refutation: null, kind: 'DUAL' }); c.undo(); c.undo(); continue; }
        const escapes = legal(c);
        let best = null;
        for (const e of escapes) {
          let kind;
          if (e.to === cand.to) kind = e.from === d.to ? 'defender retains control' : 'another unit captures the mating unit';
          else if (e.piece === 'k') kind = 'king flight';
          else if (!c.isCheck()) kind = 'no check';
          else kind = 'interposition';
          const rank = ['defender retains control', 'another unit captures the mating unit', 'interposition', 'king flight', 'no check'].indexOf(kind);
          if (!best || rank < best.rank) best = { rank, kind, san: S(e.san) };
        }
        if (best) item.avoided.push({ mate: osan, refutation: best.san, kind: best.kind });
        c.undo(); c.undo();
      }
      out.push(item);
    }
    return out;
  }

  /* main entry */
  function analyse(fen, stip, opts) {
    opts = opts || {};
    stip = (stip || '#2').toLowerCase().replace(/\s/g, '');
    const res = { fen: fen.trim().split(/\s+/)[0], stip, phases: [], keys: [], cooked: false, relations: { changed: [], reciprocal: [] } };
    const t0 = Date.now();

    if (stip === 'h#2' || stip === 'h#1.5' || stip === 'h#2.5') {
      const plies = stip === 'h#2' ? 4 : (stip === 'h#1.5' ? 3 : 5);
      res.solutions = helpSolutions(boardFrom(fen, stip.endsWith('.5') ? 'w' : 'b'), plies);
      res.ms = Date.now() - t0;
      return res;
    }

    const c = boardFrom(fen, 'w');
    if (!c) { res.error = 'bad FEN'; return res; }
    if (c.isCheck()) { res.error = 'Black king is in check in the diagram'; return res; }

    const sp = setPlay(fen);
    if (sp && sp.variations.some(v => v.conts.length)) res.phases.push(sp);

    const keys = [], tries = [];
    for (const w of legal(c)) {
      if (solvesShort(c, w)) { res.keys.push(S(c.move(w).san)); c.undo(); res.cooked = true; continue; }
      c.move(w);
      const ok = blackAllAnswered(c);
      let refCount = 0;
      if (!ok) {
        let threat = false;
        const nullFen = c.fen().replace(/ b /, ' w ');
        try { const nc = new Chess(nullFen); threat = !nc.isCheck() && matesIn1(nc).length > 0; } catch (e) {}
        if (threat) {
          for (const b of legal(c)) {
            c.move(b);
            const dead = c.isGameOver() && !c.isCheckmate();
            const ms = dead ? [] : matesIn1(c);
            c.undo();
            if (!ms.length) refCount++;
            if (refCount > (opts.maxRefutations || 1)) break;
          }
        } else refCount = 99;
      }
      c.undo();
      if (ok) keys.push(w);
      else if (refCount <= (opts.maxRefutations || 1)) tries.push(w);
    }
    for (const t of tries) res.phases.push(phaseAfter(c, t, 'try'));
    for (const k of keys) res.phases.push(phaseAfter(c, k, 'key'));
    res.keys = res.keys.concat(keys.map(k => { const s = S(c.move(k).san); c.undo(); return s; }));
    res.cooked = res.cooked || res.keys.length > 1;
    res.relations = relations(res.phases);
    if (keys.length === 1) res.dualAvoidance = dualAvoidance(fen, keys[0]);
    res.ms = Date.now() - t0;
    return res;
  }

  function helpSolutions(c, plies, max) {
    max = max || 30;
    const sols = [], line = [];
    (function rec(p) {
      if (sols.length >= max) return;
      for (const m of legal(c)) {
        c.move(m); line.push(S(m.san));
        if (p === 1) { if (c.isCheckmate()) sols.push(line.slice()); }
        else if (!c.isGameOver()) rec(p - 1);
        c.undo(); line.pop();
      }
    })(plies);
    return sols.map(l => l.map((s, i) => (i % 2 === 0 ? `${i / 2 + 1}.${s}` : s)).join(' '));
  }

  function formatReport(res) {
    if (res.error) return res.error;
    const L = [];
    if (res.solutions) {
      L.push(`${res.solutions.length} solution(s):`);
      res.solutions.forEach(s => L.push('   ' + s));
      return L.join('\n');
    }
    for (const ph of res.phases) {
      if (ph.type === 'set') {
        L.push('Set play:');
      } else {
        let h = `${ph.type === 'key' ? 'Key' : 'Try'}: 1.${ph.first}${ph.type === 'key' ? '!' : '?'}`;
        if (ph.threat.length) h += ` (threat: 2.${ph.threat.map(t => t.san).join('/')})`;
        else h += ' (zugzwang or check)';
        L.push(h);
      }
      const groups = new Map();
      let hidden = 0;
      for (const v of ph.variations) {
        if (v.refutes) continue;
        if (v.threatRepeat) { hidden++; continue; }
        const k = v.uci.slice(0, 2) + '|' + v.conts.map(x => x.san).join('/');
        if (!groups.has(k)) groups.set(k, { defs: [], conts: v.conts, dual: v.dual });
        groups.get(k).defs.push(v.defence);
      }
      for (const g of groups.values())
        L.push(`   1...${g.defs.join('/')} 2.${g.conts.map(x => x.san).join('/')}${g.dual ? '  [DUAL]' : ''}`);
      if (hidden) L.push(`   (${hidden} further moves allow the threat)`);
      if (ph.type === 'try' && ph.refutations.length) L.push('   but ' + ph.refutations.map(r => `1...${r}!`).join(', '));
      if (ph.type === 'set' && ph.unprovided.length) L.push('   unprovided: ' + ph.unprovided.slice(0, 12).join(', '));
    }
    if (!res.keys.length) L.push('No solution found.');
    else if (res.cooked) L.push(`COOKED: ${res.keys.length} keys: ${res.keys.join(', ')}`);
    if (res.relations.changed.length) {
      L.push('Changed continuations:');
      res.relations.changed.forEach(c => L.push(`   1...${c.defence}: ${c.from} -> ${c.to}   [${c.phases[0]} vs ${c.phases[1]}]`));
    }
    if (res.relations.reciprocal.length) {
      L.push('Reciprocal changes:');
      res.relations.reciprocal.forEach(r => L.push(`   ${r.defences.join(' / ')}   [${r.phases[0]} vs ${r.phases[1]}]`));
    }
    if (res.dualAvoidance && res.dualAvoidance.length) {
      const marked = res.dualAvoidance.filter(x => x.avoided.length);
      if (marked.length) {
        L.push('Dual avoidance:');
        marked.forEach(it => L.push(`   1...${it.defence} 2.${it.mate}  ` +
          it.avoided.map(a => a.refutation ? `(2.${a.mate}? ${a.refutation}!  ${a.kind})` : `(2.${a.mate}? also mate - DUAL)`).join(' ')));
        const kinds = new Set(marked.map(it => it.avoided[0] && it.avoided[0].kind).filter(Boolean));
        if (kinds.size === 1) L.push(`   [unified avoidance: ${[...kinds][0]}]`);
      }
    }
    L.push(`(${res.ms} ms)`);
    return L.join('\n');
  }

  return { analyse, formatReport, setPlay, dualAvoidance };
}));
