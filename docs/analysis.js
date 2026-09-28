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
  function noCheckReason(c, mv) {
    // the move gave no check: if it vacated a square on a White line piece's ray to the Black king and that
    // ray is still blocked, name the blocker (2.Sxg3? after 1...Qxe5: the c4-f4 battery is closed by Bd4)
    const board = c.board();
    let k = null;
    for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) { const p = board[r][f]; if (p && p.type === 'k' && p.color === 'b') k = [r, f]; }
    if (!k) return 'no check';
    const sqName = (r, f) => 'abcdefgh'[f] + (8 - r);
    const from = mv.from;
    const names = { r: 'R', b: 'B', q: 'Q', n: 'S', p: 'P', k: 'K' };
    for (const [dr, df] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]) {
      const diag = dr !== 0 && df !== 0;
      let r = k[0] + dr, f = k[1] + df, passed = false; const blockers = [];
      while (r >= 0 && r < 8 && f >= 0 && f < 8) {
        const p = board[r][f]; const nm = sqName(r, f);
        if (nm === from) passed = true;
        else if (p) {
          if (p.color === 'w' && (p.type === 'q' || (diag ? p.type === 'b' : p.type === 'r'))) {
            if (passed && blockers.length) return `no check (the battery ${names[p.type]}${nm}-${sqName(k[0], k[1])} is still closed by ${blockers.join(', ')})`;
            break;
          }
          blockers.push((p.color === 'w' ? 'w' : 'b') + names[p.type] + nm);
        }
        r += dr; f += df;
      }
    }
    return 'no check';
  }

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
        // no check at all: nothing Black plays is the reason (a battery whose line is still closed)
        const noCheck = !c.isCheck() ? noCheckReason(c, cand) : null;
        for (const e of escapes) {
          let kind;
          if (noCheck) kind = noCheck;
          else if (e.to === cand.to) kind = e.from === d.to ? 'defender retains control' : 'another unit captures the mating unit';
          else if (e.piece === 'k') kind = 'king flight';
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

    const keys = [], tries = [], stales = [];
    for (const w of legal(c)) {
      if (solvesShort(c, w)) { res.keys.push(S(c.move(w).san)); c.undo(); res.cooked = true; continue; }
      c.move(w);
      const ok = blackAllAnswered(c);
      let refCount = 0, stale = false;
      if (!ok) {
        if (c.isStalemate()) stale = true;                 // shown as a try refuted by the stalemate itself
        else for (const b of legal(c)) {                   // zugzwang tries count their refutations like threats do
          c.move(b);
          const dead = c.isGameOver() && !c.isCheckmate();
          const ms = dead ? [] : matesIn1(c);
          c.undo();
          if (!ms.length) refCount++;
          if (refCount > (opts.maxRefutations || 1)) break;
        }
      }
      const givesCheck = c.isCheck();
      c.undo();
      if (ok) keys.push(w);
      else if (stale) { if (!givesCheck) stales.push(w); }
      else if (refCount <= (opts.maxRefutations || 1)) tries.push(w);
    }
    for (const t of stales) { const ph = phaseAfter(c, t, 'try'); ph.stalemate = true; ph.threat = []; ph.variations = []; res.phases.push(ph); }
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


  // E. Bourd s27: random move = the moves of one piece allowing one and the same mate; a correction is a
  // move of that piece after which that mate no longer works and another does. A move with another mate
  // that still allows the random mate is a random move with a dual, not a correction.
  function corrections(ph) {
    const out = [], by = new Map();
    for (const v of ph.variations || []) {
      if (v.refutes || v.threatRepeat || !v.conts || !v.conts.length) continue;
      const s = v.defence || v.san || '';
      if (!'QRBS'.includes(s[0])) continue;
      const k = v.uci.slice(0, 2);
      if (!by.has(k)) by.set(k, []);
      by.get(k).push(v);
    }
    for (const [frm, vs] of by) {
      if (vs.length < 3) continue;
      const count = new Map();
      for (const v of vs) for (const c of v.conts) count.set(c.id, (count.get(c.id) || 0) + 1);
      let rid = null, n = 0;
      for (const [id, c] of count) if (c > n) { rid = id; n = c; }
      if (n < 2) continue;
      const rnd = vs.filter(v => v.conts.some(c => c.id === rid));
      const cor = vs.filter(v => !rnd.includes(v));
      if (!cor.length) continue;
      const rsan = rnd[0].conts.find(c => c.id === rid).san;
      out.push({ piece: (vs[0].defence || vs[0].san)[0] + frm,
                 random: { moves: rnd.map(v => v.defence || v.san), mate: rsan, duals: rnd.filter(v => v.conts.length > 1).map(v => v.defence || v.san) },
                 corrections: cor.map(v => ({ move: v.defence || v.san, mates: v.conts.map(c => c.san) })) });
    }
    return out;
  }
  function correctionLines(ph) {
    return corrections(ph).map(c => `   ${c.piece[0]}~ random ${c.random.moves.join('/')} 2.${c.random.mate}` +
      (c.random.duals.length ? ` (dual after ${c.random.duals.join('/')})` : '') +
      `; corrections ${c.corrections.map(x => `${x.move} 2.${x.mates.join('/')}`).join(', ')}`);
  }
  // Units beyond the original set (E. Bourd: a promoted piece in the diagram is fatal).
  function promotedForce(fen) {
    const rows = fen.split(' ')[0].split('/'), out = [];
    for (const [side, name] of [['w', 'White'], ['b', 'Black']]) {
      let q = 0, r = 0, n = 0, light = 0, dark = 0;
      rows.forEach((row, ri) => { let f = 0; for (const ch of row) { if (/\d/.test(ch)) { f += +ch; continue; }
        const isW = ch === ch.toUpperCase(); if ((side === 'w') === isW) { const u = ch.toUpperCase();
          if (u === 'Q') q++; else if (u === 'R') r++; else if (u === 'N') n++; else if (u === 'B') { if ((f + (7 - ri)) % 2 === 1) light++; else dark++; } }
        f++; } });
      const parts = [];
      if (q > 1) parts.push(q + ' queens'); if (r > 2) parts.push(r + ' rooks'); if (n > 2) parts.push(n + ' knights');
      if (light > 1 || dark > 1) parts.push((light + dark) + ' bishops, ' + Math.max(light, dark) + ' on one colour');
      if (parts.length) out.push(name + ' has ' + parts.join(', '));
    }
    return out;
  }

  // Solution the way a composer reads it (E. Bourd s28): verdict, key with threat, play grouped per piece
  // (random move / corrections), duals on one line, tries one line each, set play only where it differs.
  function phaseCompact(ph, indent) {
    indent = indent === undefined ? '   ' : indent;
    const L = [];
    const real = ph.variations.filter(v => v.conts.length && !v.refutes && !v.threatRepeat);
    const used = new Set();
    for (const c of corrections(ph)) {
      const r = c.random;
      const parts = [`${c.piece[0]}~ ${r.moves.filter(m => !r.duals.includes(m)).join('/')} 2.${r.mate}`];
      for (const x of c.corrections) if (x.mates.length === 1) parts.push(`${x.move} 2.${x.mates[0]}`);
      L.push(indent + parts.join('  |  '));
      r.moves.forEach(m => used.add(m)); c.corrections.forEach(x => used.add(x.move));
    }
    const byMate = new Map(), duals = [];
    for (const v of real) {
      const d = v.defence;
      if (used.has(d) && v.conts.length === 1) continue;
      if (v.conts.length > 1) duals.push(`${d} 2.${v.conts.map(x => x.san).join('/')}`);
      else if (!used.has(d)) { const m = v.conts[0].san; if (!byMate.has(m)) byMate.set(m, []); byMate.get(m).push(d); }
    }
    if (byMate.size) L.push(indent + [...byMate].map(([m, ds]) => `${ds.join('/')} 2.${m}`).join('  |  '));
    if (duals.length) L.push(indent + '[duals] ' + duals.join('  '));
    const hidden = ph.variations.filter(v => v.threatRepeat && !v.refutes).length;
    if (hidden) L.push(indent + `(${hidden} other moves allow the threat)`);
    return L;
  }
  function formatCompact(res) {
    if (res.error) return res.error;
    const L = [];
    for (const line of promotedForce(res.fen || '')) L.push('PROMOTED FORCE: ' + line + '  (fatal)');
    if (res.solutions) { L.push(`${res.solutions.length} solution(s): ` + res.solutions.join(' ; ')); return L.join('\n'); }
    const sp = res.phases.find(p => p.type === 'set');
    const keys = res.phases.filter(p => p.type === 'key'), tries = res.phases.filter(p => p.type === 'try');
    if (!res.keys.length) L.push('No solution.');
    else if (res.cooked) L.push(`COOKED: ${res.keys.length} keys: ${res.keys.join(', ')}`);
    if (sp) { const checks = sp.unprovided.filter(u => u.endsWith('+')); if (checks.length) L.push('UNPROVIDED CHECK in the set play: ' + checks.join(', ') + '  (fatal)'); }
    for (const k of keys) {
      let h = `1.${k.first}!`;
      if (k.threat.length) h += ` (2.${k.threat.map(t => t.san).join('/')})`;
      else h += k.first.endsWith('#') ? ' (mate in one)' : (k.stalemate ? ' (stalemate)' : ' (zugzwang or check)');
      L.push(h); L.push(...phaseCompact(k));
    }
    for (const t of tries) {
      const th = t.threat.length ? ` (2.${t.threat.map(x => x.san).join('/')})` : '';
      const ref = t.stalemate ? 'stalemate!' : t.refutations.map(r => r + '!').join(', ');
      L.push(`Try 1.${t.first}?${th} but ${ref}`);
    }
    const ch = (res.relations.changed || []).filter(c => c.phases[0] === 'set play' && /^key/.test(c.phases[1]));
    if (ch.length) {
      const by = new Map();
      for (const c of ch) { const k = c.from + '->' + c.to; if (!by.has(k)) by.set(k, []); by.get(k).push(c.defence); }
      L.push('Set play differs: ' + [...by].map(([k, ds]) => `${ds.join('/')} ${k}`).join(', '));
    } else if (sp && keys.length && sp.variations.some(v => v.conts.length)) L.push('Set play: same mates as after the key');
    return L.join('\n');
  }
  function formatReport(res) {
    if (res.error) return res.error;
    const L = [];
    for (const line of promotedForce(res.fen || '')) L.push('PROMOTED FORCE: ' + line + '  (fatal)');
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
        else h += ph.stalemate ? ' (stalemate)' : ' (zugzwang or check)';
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
      for (const line of correctionLines(ph)) L.push(line);
      if (ph.type === 'try' && ph.stalemate) L.push('   but stalemate!');
      else if (ph.type === 'try' && ph.refutations.length) L.push('   but ' + ph.refutations.map(r => `1...${r}!`).join(', '));
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
          it.avoided.map(a => /^no check/.test(a.kind) ? `(2.${a.mate}? ${a.kind})` : a.refutation ? `(2.${a.mate}? ${a.refutation}!  ${a.kind})` : `(2.${a.mate}? also mate - DUAL)`).join(' ')));
        const kinds = new Set(marked.map(it => it.avoided[0] && it.avoided[0].kind).filter(Boolean));
        if (kinds.size === 1) L.push(`   [unified avoidance: ${[...kinds][0]}]`);
      }
    }
    L.push(`(${res.ms} ms)`);
    return L.join('\n');
  }

  return { analyse, formatReport, formatCompact, phaseCompact, setPlay, dualAvoidance, corrections, correctionLines, promotedForce };
}));
