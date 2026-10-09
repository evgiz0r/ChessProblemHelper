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
    // chess.js already marks a mating move with '#' in its SAN (it plays every move to write the SAN),
    // so playing each move again to test for mate doubled the cost of every solve
    return legal(c).filter(m => m.san.endsWith('#'));
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

  // Find the key (E. Bourd s30: "given a post-key play that works, find a move getting to that position where
  // it is the only key; mention the moves that are close"). retractions(): every non-capturing White move that
  // could have produced this position (Black to move); keysOf(): the keys of a diagram, stopping past `limit`.
  function retractions(postFen) {
    const post = postFen.trim().split(/\s+/)[0], out = [];
    let pb; try { pb = new Chess(post + ' b - - 0 1'); } catch (e) { return out; }
    const files = 'abcdefgh';
    const squares = []; for (let r = 1; r <= 8; r++) for (const f of files) squares.push(f + r);
    for (const sq of squares) {
      const pc = pb.get(sq); if (!pc || pc.color !== 'w') continue;
      for (const frm of squares) {
        if (pb.get(frm)) continue;
        if (pc.type === 'p' && /[18]$/.test(frm)) continue;
        let g; try { g = new Chess(post + ' w - - 0 1'); } catch (e) { continue; }
        g.remove(sq); if (!g.put({ type: pc.type, color: 'w' }, frm)) continue;
        let fen = g.fen().split(' ')[0], pre;
        try { pre = new Chess(fen + ' w - - 0 1'); } catch (e) { continue; }
        if (pre.isCheck()) continue;                                   // White may not stand in check
        let bl; try { bl = new Chess(fen + ' b - - 0 1'); if (bl.isCheck()) continue; } catch (e) { continue; }
        const mv = pre.moves({ verbose: true }).find(m => m.from === frm && m.to === sq && !m.captured && !m.promotion);
        if (!mv) continue;
        pre.move(mv);
        if (pre.fen().split(' ')[0] !== post) continue;
        const letter = { k: 'K', q: 'Q', r: 'R', b: 'B', n: 'S', p: '' }[pc.type];
        out.push({ san: S(mv.san), fen, check: mv.san.includes('+'), from: frm, to: sq,
                   long: letter + frm + '-' + sq + (mv.san.includes('+') ? '+' : '') });
      }
    }
    return out;
  }
  function keysOf(fen, limit) {
    const c = boardFrom(fen, 'w'); if (!c) return null;
    const keys = [];
    for (const w of legal(c)) {
      let ok;
      if (solvesShort(c, w)) ok = true;
      else { c.move(w); ok = blackAllAnswered(c); c.undo(); }
      if (ok) { keys.push(S(w.san)); if (keys.length > limit) break; }
    }
    return keys;
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
  // Thematic table (E. Bourd s29: "the solution is so cluttered it's hard to figure if the thematic play is
  // there"): one row per thematic defence, one column per phase (set, tries that change the theme, key).
  // Mirrors chesscomp/thematic.py.
  function thematicTable(res, defs, asData) {
    if (!res.phases) return null;
    const key = res.phases.find(p => p.type === 'key'); if (!key || res.cooked) return null;
    const sp = res.phases.find(p => p.type === 'set');
    const cellsOf = ph => { const m = new Map(); for (const v of ph.variations || []) {
      if (v.refutes) continue;
      const ms = (v.conts || []).map(c => c.san);
      m.set(v.defence, v.threatRepeat ? 'threat' : (ms.length ? ms.join('/') + (ms.length > 1 ? ' DUAL' : '') : '-')); } return m; };
    const C = new Map(res.phases.filter(p => p.type !== 'try' || (p.refutations || []).length === 1).map(p => [p, cellsOf(p)]));
    const real = c => c !== undefined && c !== '-' && c !== 'threat' && !c.includes('DUAL');
    const groups = corrections(key).length ? corrections(key) : (sp ? corrections(sp) : []);
    const grouped = new Set(groups.flatMap(g => [...g.random.moves, ...g.corrections.map(x => x.move)]));
    const kc = C.get(key);
    const cand = [...C.keys()].filter(p => p !== key);
    const pinned = (defs || []).filter(Boolean);
    const rows = pinned.length ? pinned
      : [...kc.keys()].filter(d => !grouped.has(d) && real(kc.get(d)) && cand.some(p => real(C.get(p).get(d)) && C.get(p).get(d) !== kc.get(d)));
    const ts = pinned.length ? rows : [...rows, ...groups.flatMap(g => [g.random.moves[0], ...g.corrections.map(x => x.move)])];
    const tries = cand.filter(p => p.type === 'try' && ts.every(d => C.get(p).has(d))
      && ts.some(d => real(C.get(p).get(d)) && C.get(p).get(d) !== kc.get(d))
      && !(sp && ts.every(d => !real(C.get(p).get(d)) || C.get(p).get(d) === C.get(sp).get(d)))).slice(0, 3);
    const cols = [...(sp ? [['set', sp]] : []), ...tries.map(t => [`1.${t.first}? ${t.refutations[0]}!`, t]), [`1.${key.first}!`, key]];
    if (!rows.length && !groups.length) return null;
    if (pinned.length) cols.forEach(([, p]) => { for (const d of pinned) if (!C.get(p).has(d)) C.get(p).set(d, 'not legal'); });
    if (asData) return { cols, C, groups: pinned.length ? [] : groups, rows, key };
    const grid = [['', ...cols.map(([n, p]) => n + (p.type === 'set' ? '' : (p.threat.length ? ` (${p.threat.map(t => t.san).join('/')})` : ' (zz)')))]];
    const shown = new Set();
    const row = (label, d) => { const vals = cols.map(([, p]) => C.get(p).get(d) || '?');
      const changed = new Set(vals.filter(v => !['-', '?', 'threat'].includes(v))).size > 1;
      grid.push([label + (changed ? '  *' : ''), ...vals]); shown.add(d); };
    for (const g of (pinned.length ? [] : groups)) { row(`${g.piece[0]}~ (${g.random.moves.length})`, g.random.moves[0]); g.random.moves.forEach(m => shown.add(m));
      for (const x of g.corrections) row('  ' + x.move, x.move); }
    const merged = new Map();
    for (const d of rows) if (!shown.has(d)) { const k = cols.map(([, p]) => C.get(p).get(d) || '?').join('|'); if (!merged.has(k)) merged.set(k, []); merged.get(k).push(d); }
    for (const ds of merged.values()) { row(ds.join('/'), ds[0]); ds.forEach(d => shown.add(d)); }
    const w = grid[0].map((_, i) => Math.max(...grid.map(r => r[i].length)));
    const L = [(pinned.length ? 'Thematic play (your theme' : 'Thematic play (guessed') + '; * = mate changes):', ...grid.map(r => '   ' + r.map((x, i) => x.padEnd(w[i])).join('  ').trimEnd())];
    const rest = [...kc.keys()].filter(d => !shown.has(d));
    const duals = rest.filter(d => (kc.get(d) || '').includes('DUAL')), holes = rest.filter(d => kc.get(d) === '-');
    let s = `   other Black play after the key: ${rest.length} moves`;
    if (duals.length) s += `; duals after ${duals.join(', ')}`;
    if (holes.length) s += `; NO MATE after ${holes.join(', ')}`;
    L.push(s);
    return L.join('\n');
  }
  // FIDE Album style (E. Bourd s30): "Set: 1...S~ 2.Qc4#, 1...Sxd6! [a] 2.Sxf6#, ..." - corrections carry '!',
  // thematic defences a letter, other play on an "Also" line, duals on their own line.
  function albumNotation(res, defs) {
    const d = thematicTable(res, defs, true); if (!d) return null;
    const { cols, C, groups, rows, key } = d;
    const items = [], corr = new Set();
    for (const g of groups) { items.push({ label: g.piece[0] + '~', san: g.random.moves[0], rnd: true });
      for (const x of g.corrections) { items.push({ label: x.move, san: x.move }); corr.add(x.move); } }
    const merged = new Map();
    for (const r of rows) { if (items.some(i => i.san === r)) continue;
      const k = cols.map(([, p]) => C.get(p).get(r) || '?').join('|'); if (!merged.has(k)) merged.set(k, []); merged.get(k).push(r); }
    for (const sans of merged.values()) items.push({ label: sans.join('/'), san: sans[0], all: sans });
    let n = 0; for (const i of items) if (!i.rnd) i.letter = 'abcdefghij'[n++];
    const cell = (p, s) => { const c = C.get(p).get(s); if (c === undefined) return null;
      if (c === '-') return 'no mate'; if (c === 'threat') return '2.threat';
      return '2.' + (c.endsWith(' DUAL') ? c.slice(0, -5) + ' (dual)' : c); };
    const line = p => items.map(i => { const c = cell(p, i.san); if (c === null) return null;
      return i.rnd ? `1...${i.label} ${c}` : `1...${i.label}${corr.has(i.san) ? '!' : ''} [${i.letter}] ${c}`; }).filter(Boolean).join(', ');
    const L = [];
    for (const [, p] of cols) {
      const head = p.type === 'set' ? '' : (p.threat.length ? `(2.${p.threat.map(t => t.san).join('/')})` : 'zz');
      if (p.type === 'set') L.push('Set: ' + line(p));
      else if (p.type === 'try') L.push(`Try: 1.${p.first}? ${head}, ${line(p)}, but 1...${p.refutations[0]}!`);
      else L.push(`Solution: 1.${p.first}! ${head}, ${line(p)}`);
    }
    const shown = new Set(items.flatMap(i => i.all || [i.san]));
    for (const g of groups) g.random.moves.forEach(m => shown.add(m));
    const kc = C.get(key), by = new Map(), duals = [];
    for (const [s, c] of kc) { if (shown.has(s) || c === 'threat') continue;
      if (c.endsWith(' DUAL')) duals.push(`1...${s} 2.${c.slice(0, -5)}`);
      else if (c === '-') duals.push(`1...${s} NO MATE`);
      else { if (!by.has(c)) by.set(c, []); by.get(c).push(s); } }
    if (by.size) L.push('Also: ' + [...by].map(([c, ss]) => `1...${ss.join('/')} 2.${c}`).join(', '));
    if (duals.length) L.push('Duals: ' + duals.join(', '));
    return L.join('\n');
  }
  // What one edit did (E. Bourd s30: "incrementally realize what we want to see, as I'm iterating"): a small
  // summary of a solve, and the difference to the previous solve of the same session.
  function solveSummary(res, defs) {
    const out = { keys: (res.keys || []).slice(), cooked: !!res.cooked, theme: {}, holes: [], duals: [] };
    const key = (res.phases || []).find(p => p.type === 'key');
    const sp = (res.phases || []).find(p => p.type === 'set');
    const cell = v => !v ? 'not legal' : v.threatRepeat ? 'threat' : (v.conts.length ? v.conts.map(c => c.san).join('/') + (v.conts.length > 1 ? ' DUAL' : '') : 'no mate');
    const pick = ph => new Map((ph ? ph.variations : []).filter(v => !v.refutes).map(v => [v.defence, v]));
    if (key && !res.cooked) {
      const km = pick(key), sm = pick(sp);
      for (const d of defs || []) out.theme[d] = { set: sp ? cell(sm.get(d)) : '', key: cell(km.get(d)) };
      for (const v of key.variations) { if (v.refutes) continue;
        if (!v.threatRepeat && !v.conts.length) out.holes.push(v.defence);
        if (v.conts.length > 1) out.duals.push(v.defence); }
    }
    return out;
  }
  function diffSummary(prev, cur) {
    if (!prev) return [];
    const L = [], gone = prev.keys.filter(k => !cur.keys.includes(k)), came = cur.keys.filter(k => !prev.keys.includes(k));
    if (prev.cooked !== cur.cooked || gone.length || came.length) {
      const v = s => s.keys.length === 0 ? 'no solution' : s.cooked ? `cooked (${s.keys.length} keys)` : `sound, 1.${s.keys[0]}!`;
      L.push(`was ${v(prev)}, now ${v(cur)}` + (gone.length ? `; gone: ${gone.join(', ')}` : '') + (came.length ? `; new: ${came.join(', ')}` : ''));
    }
    for (const d of Object.keys(cur.theme)) { const a = prev.theme[d], b = cur.theme[d];
      if (a && (a.key !== b.key || a.set !== b.set)) L.push(`${d}: set ${a.set || '-'} -> ${b.set || '-'}, key ${a.key} -> ${b.key}`); }
    const plus = (a, b) => b.filter(x => !a.includes(x)), minus = (a, b) => a.filter(x => !b.includes(x));
    if (plus(prev.holes, cur.holes).length) L.push('new holes: ' + plus(prev.holes, cur.holes).join(', '));
    if (minus(prev.holes, cur.holes).length) L.push('holes closed: ' + minus(prev.holes, cur.holes).join(', '));
    if (plus(prev.duals, cur.duals).length) L.push('new duals: ' + plus(prev.duals, cur.duals).join(', '));
    if (minus(prev.duals, cur.duals).length) L.push('duals gone: ' + minus(prev.duals, cur.duals).join(', '));
    return L.length ? ['Since the last solve: ' + L[0], ...L.slice(1).map(l => '   ' + l)] : ['Since the last solve: no change in verdict, theme, holes or duals'];
  }
  function formatCompact(res, opts) {
    if (res.error) return res.error;
    const L = [];
    for (const line of promotedForce(res.fen || '')) L.push('PROMOTED FORCE: ' + line + '  (fatal)');
    if (res.solutions) { L.push(`${res.solutions.length} solution(s): ` + res.solutions.join(' ; ')); return L.join('\n'); }
    const sp = res.phases.find(p => p.type === 'set');
    const al = albumNotation(res, opts && opts.theme);
    if (al) { L.push(al); L.push(''); }
    const tt = thematicTable(res, opts && opts.theme);
    if (tt) L.push(tt);
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
    // E. Bourd (s29): the changes are the content, so the short solution shows them under each try
    const changes = lab => [...new Set((res.relations.changed || []).filter(c => c.phases[0] === lab && /^key/.test(c.phases[1]) && c.from !== c.to)
      .map(c => `${c.defence} ${c.from}->${c.to}`))].join(', ');
    const folded = new Map();   // tries that change nothing: one line per refutation (E. Bourd s29: clutter)
    for (const t of tries) {
      const th = t.threat.length ? ` (2.${t.threat.map(x => x.san).join('/')})` : '';
      const ref = t.stalemate ? 'stalemate!' : t.refutations.map(r => r + '!').join(', ');
      const chg = changes(`try ${t.first}`);
      const setChg = new Set(changes('set play').split(', ').filter(Boolean));
      const onlySet = chg && chg.split(', ').every(x => setChg.has(x));   // the try just keeps the set play
      if ((!chg || onlySet) && !t.threat.length) { if (!folded.has(ref)) folded.set(ref, []); folded.get(ref).push(`1.${t.first}?`); continue; }
      L.push(`Try 1.${t.first}?${th} but ${ref}`);
      if (chg) L.push('   changed: ' + chg);
    }
    for (const [ref, ts] of folded) L.push(`${ts.length > 1 ? 'Tries' : 'Try'} ${ts.join(' ')} but ${ref}`);
    const ch = (res.relations.changed || []).filter(c => c.phases[0] === 'set play' && /^key/.test(c.phases[1]) && c.from !== c.to);
    if (ch.length) L.push('Set play differs: ' + changes('set play'));
    if (sp && keys.length && sp.variations.some(v => v.conts.length)) {
      const km = new Map(keys[0].variations.filter(v => v.conts.length && !v.threatRepeat).map(v => [v.defence, v.conts.map(c => c.san).join('/')]));
      const chDefs = new Set(ch.map(c => c.defence));
      const other = sp.variations.filter(v => v.conts.length && !chDefs.has(v.defence) && km.has(v.defence) && km.get(v.defence) !== v.conts.map(c => c.san).join('/'))
        .map(v => `${v.defence} 2.${v.conts.map(c => c.san).join('/')}` + (v.conts.length > 1 ? ' [dual]' : ''));
      if (other.length) L.push('Set play also: ' + other.join('  '));
      else if (!ch.length && sp.variations.filter(v => v.conts.length).every(v => km.get(v.defence) === v.conts.map(c => c.san).join('/')))
        L.push('Set play: same mates as after the key');
    }
    const rec = res.relations.reciprocal || [];
    if (rec.length) L.push('Reciprocal: ' + [...new Set(rec.map(r => `${r.defences.join('/')} [${r.phases.join(' vs ')}]`))].join('; '));
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

  /* Key readiness (E. Bourd, 8 Oct 2026: "most of the part is just finding the key"). With White to move in a
     post-key position, every first move that forces mate in two (mates in one included) except the threat would
     cook any key that leaves it alone; a key piece must be needed by all of them. Returns
     { solutions: [san], units: [{unit, left: [san]}] } where `left` is what still solves without that unit. */
  function solutionsOf(c) {
    const out = [];
    for (const w of legal(c)) {
      c.move(w);
      const ok = c.isCheckmate() || blackAllAnswered(c);
      c.undo();
      if (ok) out.push(S(w.san));
    }
    return out;
  }
  // E. Bourd (8 Oct 2026): a move that leaves the threat standing solves in any sound post-key position
  // (Kg8 as a waiting move) - that is the solution, not a cook. Keep only moves after which the threat no
  // longer mates, and drop the threat itself.
  function realSolutions(c) {
    const threat = new Set(matesIn1(c).map(mid));
    return solutionsOf(c).filter(san => {
      const m = c.move(san.replace(/^S/, 'N').replace('=S', '=N'));
      let keeps = false;
      if (!threat.has(mid(m)) && !c.isCheck()) {
        const nc = new Chess(c.fen().replace(' b ', ' w '));
        keeps = matesIn1(nc).some(x => threat.has(mid(x)));
      }
      c.undo();
      return !threat.has(mid(m)) && !keeps;
    });
  }
  function keyReadiness(fen, withUnits) {
    const c = boardFrom(fen, 'w');
    if (!c || c.isCheck()) return null;
    const res = { solutions: realSolutions(c), units: [] };
    if (!withUnits) return res;
    for (const sq of c.board().flat().filter(p => p && p.color === 'w' && p.type !== 'k').map(p => p.square)) {
      const d = boardFrom(fen, 'w'); d.remove(sq);
      const name = (c.get(sq).type === 'n' ? 'S' : c.get(sq).type.toUpperCase()) + sq;
      if (d.isCheck()) continue;
      // a removal that opens a flight for the Black king kills every mate for the wrong reason: flag it
      const bl = boardFrom(d.fen().split(' ')[0], 'b');
      const flight = !!bl && bl.moves({ verbose: true }).some(m => m.piece === 'k');
      res.units.push({ unit: name, left: solutionsOf(d).filter(x => res.solutions.includes(x)), flight });
    }
    return res;
  }

  return { analyse, keyReadiness, formatReport, formatCompact, thematicTable, albumNotation, retractions, keysOf, solveSummary, diffSummary, phaseCompact, setPlay, dualAvoidance, corrections, correctionLines, promotedForce };
}));
