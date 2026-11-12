// Interactive tree (SVG dendrogram): analysis.create_phylogenetic_tree via /api/tree (rebuilt in the browser on the
// static site). Click or press Enter on a junction to collapse/expand that clade; search highlights genres; the
// sliders change the distance weights and rebuild the tree.
import { route, app, api, esc, $, download, slider } from './core.js';
import { eraOf, href, legend, genreMap } from './ui.js';
import { leaves, newick, DEFAULT_WEIGHTS } from './genre_engine.js';

const ROW = 16, LABEL = 210, PAD = 14, W = 760;
const ns = 'http://www.w3.org/2000/svg';

function layout(root, collapsed, sqrt) {
  // y: leaves (and collapsed clades) get consecutive rows; x: distance from the root (height decreases to 0 at tips).
  let row = 0;
  const H = root.height || 1, plotW = W - LABEL - PAD * 2;
  const f = sqrt ? Math.sqrt : (v => v);
  const xOf = h => PAD + (f(H) - f(h)) / f(H) * plotW;
  const items = [];
  const place = (n, id) => {
    n._id = id;
    if (!n.children || collapsed.has(id)) { n._y = PAD + row++ * ROW + ROW / 2; n._x = xOf(n.children ? n.height : 0); n._leaf = true; }
    else { n.children.forEach((c, i) => place(c, id + i)); n._y = (n.children[0]._y + n.children[1]._y) / 2; n._x = xOf(n.height); n._leaf = false; }
    items.push(n);
  };
  place(root, 'r');
  return { items, height: PAD * 2 + row * ROW, xOf };
}

function svgTree(root, collapsed, map, hits, sqrt) {
  const { items, height, xOf } = layout(root, collapsed, sqrt);
  const parts = [];
  for (const n of items) {
    if (n._leaf || !n.children) continue;
    const [a, b] = n.children;
    parts.push(`<path class="br" d="M${n._x},${a._y}V${b._y}M${n._x},${a._y}H${a._x}M${n._x},${b._y}H${b._x}"/>`);
  }
  for (const n of items) {
    if (n.children && !n._leaf) {
      const k = leaves(n).length;
      parts.push(`<circle class="jn" cx="${n._x}" cy="${n._y}" r="4" tabindex="0" role="button" data-id="${n._id}"
        aria-label="Collapse clade of ${k} genres at height ${n.height.toFixed(3)}"><title>${k} genres · height ${n.height.toFixed(3)} · click to collapse</title></circle>`);
    } else if (n.children) {
      const names = leaves(n), k = names.length, hit = names.some(x => hits.has(x));
      const tip = xOf(0);
      parts.push(`<g class="clade${hit ? ' hit' : ''}" tabindex="0" role="button" data-id="${n._id}" aria-label="Expand clade of ${k} genres">
        <path d="M${n._x},${n._y}L${tip},${n._y - 6}V${n._y + 6}Z"/><text x="${tip + 6}" y="${n._y + 4}">${k} genres: ${esc(names.slice(0, 2).join(', '))}…</text>
        <title>${esc(names.join(', '))}</title></g>`);
    } else {
      const g = map[n.name], c = eraOf(g.date).color, hit = hits.has(n.name);
      parts.push(`<a href="${href(n.name)}" class="leaf${hit ? ' hit' : ''}" data-name="${esc(n.name)}"><circle cx="${n._x}" cy="${n._y}" r="3.2" fill="${c}"/>
        <text x="${n._x + 7}" y="${n._y + 4}">${esc(n.name)}</text></a>`);
    }
  }
  const ticks = [];
  const H = root.height;
  for (let t = 0; t <= H + 1e-9; t += H > 0.6 ? 0.1 : 0.05) ticks.push(`<g class="tick"><line x1="${xOf(t)}" x2="${xOf(t)}" y1="${PAD}" y2="${height - PAD}"/><text x="${xOf(t)}" y="${height - 2}">${t.toFixed(2)}</text></g>`);
  return `<svg xmlns="${ns}" class="tree" viewBox="0 0 ${W} ${height + 10}" role="group" aria-label="Genre tree dendrogram">${ticks.join('')}${parts.join('')}</svg>`;
}

route('tree', async (args, q) => {
  const map = await genreMap();
  let weights = [...DEFAULT_WEIGHTS], root = await api('/tree');
  const collapsed = new Set();
  let sqrt = false;
  const focus = q.focus && map[q.focus] ? q.focus : '';
  app().innerHTML = `
  <p class="kicker">Phylogeny</p><h1>Interactive tree</h1>
  <p class="lead">Genres joined closest-first by the combined date / parent / trait distance (the repository's
  <code>create_phylogenetic_tree</code>). Horizontal position is the joining height (half the distance at which two
  clusters merge); leaves are coloured by first date.</p>
  <div class="side tree-side">
    <div class="panel">
      <label for="tq">Find genres</label><input id="tq" type="search" value="${esc(focus)}" placeholder="name or trait">
      <p id="tq-n" class="small mute" aria-live="polite"></p>
      <h3>Horizontal scale</h3><div class="seg" role="group" aria-label="Horizontal scale"><button id="sx-lin" class="on" aria-pressed="true">Linear</button><button id="sx-sqrt" aria-pressed="false">Square root</button></div>
      <h3>Distance weights</h3><div id="wts"></div>
      <p class="small mute" id="wsum"></p>
      <button id="wreset" class="alt">Repo weights</button><button id="expand" class="alt">Expand all</button>
      <button id="nwk" class="alt">Newick</button>
      ${legend()}
      <div id="clade" class="small"></div>
    </div>
    <div class="stage tree-stage" id="stage"></div>
  </div>`;
  const hitsFor = w => new Set(w ? Object.values(map).filter(g => g.name.toLowerCase().includes(w) || g.characteristics.some(c => c.toLowerCase().includes(w))).map(g => g.name) : []);
  let hits = hitsFor(focus.toLowerCase());
  const nodeById = id => { let n = root; for (const ch of id.slice(1)) n = n.children[+ch]; return n; };
  const draw = () => {
    $('#stage').innerHTML = svgTree(root, collapsed, map, hits, sqrt);
    $('#tq-n').textContent = hits.size ? `${hits.size} genre${hits.size > 1 ? 's' : ''} highlighted` : '';
    $('#wsum').textContent = `d = ${weights[0]} · time + ${weights[1]} · parents + ${weights[2]} · traits; tree height ${root.height.toFixed(3)}`;
    const toggle = el => {
      const id = el.dataset.id, n = nodeById(id);
      if (collapsed.has(id)) collapsed.delete(id); else collapsed.add(id);
      $('#clade').innerHTML = `<h3>Clade</h3><p>${leaves(n).length} genres joined at height ${n.height.toFixed(3)}:
        ${leaves(n).map(x => `<a href="${href(x)}">${esc(x)}</a>`).join(', ')}</p>`;
      draw();
      $(`#stage [data-id="${id}"]`)?.focus();
    };
    $('#stage').querySelectorAll('[data-id]').forEach(el => {
      el.addEventListener('click', () => toggle(el));
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(el); } });
    });
  };
  const rebuild = async () => {
    root = await api(`/tree?w_time=${weights[0]}&w_parent=${weights[1]}&w_char=${weights[2]}`);
    collapsed.clear(); draw();
  };
  const sliders = ['time (|Δdate| / 1000)', 'parents (1 − Jaccard)', 'traits (1 − Jaccard)'].map((label, i) =>
    slider($('#wts'), { id: 'w' + i, label, min: 0, max: 1, step: 0.05, value: weights[i], fmt: v => v.toFixed(2) }, v => {
      weights[i] = +v.toFixed(2); clearTimeout(rebuild.t); rebuild.t = setTimeout(rebuild, 150);
    }));
  $('#wreset').addEventListener('click', () => {
    weights = [...DEFAULT_WEIGHTS];
    sliders.forEach((s, i) => { s.value = weights[i]; s.dispatchEvent(new Event('input')); });
  });
  [['#sx-lin', false], ['#sx-sqrt', true]].forEach(([id, v]) => $(id).addEventListener('click', () => {
    sqrt = v; $('#sx-lin').classList.toggle('on', !v); $('#sx-sqrt').classList.toggle('on', v);
    $('#sx-lin').setAttribute('aria-pressed', String(!v)); $('#sx-sqrt').setAttribute('aria-pressed', String(v)); draw();
  }));
  $('#expand').addEventListener('click', () => { collapsed.clear(); draw(); });
  $('#nwk').addEventListener('click', () => download('genre_tree.nwk', newick(root) + ';\n'));
  $('#tq').addEventListener('input', e => { hits = hitsFor(e.target.value.trim().toLowerCase()); draw(); });
  draw();
  const st = $('#stage'); st.scrollLeft = st.scrollWidth; // narrow screens: start at the labelled tips
  if (focus) $(`#stage .leaf[data-name="${CSS.escape(focus)}"]`)?.scrollIntoView({ block: 'center' });
});

