// Distances: the three components for a chosen pair of genres, and the full distance heatmap (rows and columns in
// tree leaf order, so clades show as dark blocks). Computed in the browser by genre_engine.js.
import { route, app, api, esc, list, $, go } from './core.js';
import { glink, fmtDate, genreMap } from './ui.js';
import { components, distanceMatrix, leaves, DEFAULT_WEIGHTS } from './genre_engine.js';

// Sequential ramp, dark (near) to light (far).
const RAMP = ['#1b1035', '#3b1d63', '#6a2c8a', '#a2408c', '#d9637a', '#f5965e', '#f9cd6b', '#fbf2c4'];
function ramp(t) {
  const x = Math.max(0, Math.min(1, t)) * (RAMP.length - 1), i = Math.min(RAMP.length - 2, Math.floor(x)), f = x - i;
  const c = k => parseInt(RAMP[k].slice(1), 16);
  const mix = s => Math.round(((c(i) >> s) & 255) * (1 - f) + ((c(i + 1) >> s) & 255) * f);
  return [mix(16), mix(8), mix(0)];
}

route('distance', async (args, q) => {
  const [map, tree] = await Promise.all([genreMap(), api('/tree')]);
  const names = Object.keys(map).sort();
  const a = map[q.a] ? q.a : 'Urban Fantasy', b = map[q.b] ? q.b : 'Contemporary Fantasy';
  const opts = sel => list(names, n => `<option${n === sel ? ' selected' : ''}>${esc(n)}</option>`);
  const c = components(map[a], map[b]);
  const [wt, wp, wc] = DEFAULT_WEIGHTS;
  const parts = [['time', '|Δdate| / 1000', c.time, wt], ['parents', '1 − Jaccard(parents)', c.parent, wp], ['traits', '1 − Jaccard(traits)', c.chars, wc]];
  const sharedP = map[a].parents.filter(p => map[b].parents.includes(p));
  const sharedT = map[a].characteristics.filter(t => map[b].characteristics.includes(t));
  app().innerHTML = `
  <p class="kicker">Phylogeny</p><h1>Distances</h1>
  <p class="lead">How far apart two genres are under the repository's distance (weights ${wt} / ${wp} / ${wc}).</p>
  <div class="row panel">
    <div><label for="da">Genre A</label><select id="da">${opts(a)}</select></div>
    <div><label for="db">Genre B</label><select id="db">${opts(b)}</select></div>
  </div>
  <div class="two">
    <div class="panel">
      <h3>${glink(a)} (${fmtDate(map[a].date)}) vs ${glink(b)} (${fmtDate(map[b].date)})</h3>
      <table><thead><tr><th>Part</th><th>Value</th><th>Weight</th><th>Contribution</th></tr></thead><tbody>
      ${list(parts, ([k, f, v, w]) => `<tr><td>${k}<br><span class="small mute">${f}</span></td><td class="mono">${v.toFixed(3)}</td>
        <td class="mono">${w}</td><td><span class="bar" style="width:${(w * v / Math.max(c.total, 1e-9) * 100).toFixed(1)}%"></span> <span class="mono">${(w * v).toFixed(3)}</span></td></tr>`)}
      <tr><th>Total</th><td></td><td></td><td class="mono"><b>${c.total.toFixed(4)}</b></td></tr></tbody></table>
    </div>
    <div class="panel">
      <h3>Shared parents</h3><p>${list(sharedP, glink, ', ') || `<span class="mute">None${!map[a].parents.length || !map[b].parents.length ? ' (a genre with no parents always scores 1 here)' : ''}.</span>`}</p>
      <h3>Shared traits</h3><p>${list(sharedT, t => `<span class="tag a">${esc(t)}</span>`) || '<span class="mute">None.</span>'}</p>
      <p class="small mute">Parent and trait parts are 1 − shared / union of the two sets.</p>
    </div>
  </div>
  <h2>Distance heatmap</h2>
  <p class="small mute">All ${names.length} × ${names.length} genre pairs, ordered as the leaves of the tree. Colour is the pair's
  percentile among all distances (darker is closer), so the few very distant ancient genres do not wash out the rest.
  Hover to read a pair; click to compare it above.</p>
  <div class="heat"><canvas id="hm" width="${names.length}" height="${names.length}" aria-label="Distance heatmap"></canvas>
    <p id="hm-tip" class="small mono" aria-live="polite">&nbsp;</p></div>`;
  ['#da', '#db'].forEach(s => $(s).addEventListener('change', () =>
    go(`#/distance?a=${encodeURIComponent($('#da').value)}&b=${encodeURIComponent($('#db').value)}&keep=1`)));

  const order = leaves(tree), { names: sorted, D } = distanceMatrix(map);
  const idx = order.map(n => sorted.indexOf(n)), n = order.length;
  const vals = [];
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) vals.push(D[i][j]);
  vals.sort((x, y) => x - y);
  const pct = v => { let lo = 0, hi = vals.length; while (lo < hi) { const m = (lo + hi) >> 1; if (vals[m] < v) lo = m + 1; else hi = m; } return lo / vals.length; };
  const cv = $('#hm'), ctx = cv.getContext('2d'), img = ctx.createImageData(n, n);
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
    const [r, g, bl] = ramp(i === j ? 0 : pct(D[idx[i]][idx[j]])), k = (i * n + j) * 4;
    img.data[k] = r; img.data[k + 1] = g; img.data[k + 2] = bl; img.data[k + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  const cell = e => {
    const r = cv.getBoundingClientRect();
    return [Math.floor((e.clientY - r.top) / r.height * n), Math.floor((e.clientX - r.left) / r.width * n)];
  };
  cv.addEventListener('mousemove', e => {
    const [i, j] = cell(e);
    if (i >= 0 && j >= 0 && i < n && j < n) $('#hm-tip').textContent = `${order[i]} · ${order[j]}: ${D[idx[i]][idx[j]].toFixed(3)}`;
  });
  cv.addEventListener('click', e => {
    const [i, j] = cell(e);
    if (i >= 0 && j >= 0 && i < n && j < n) go(`#/distance?a=${encodeURIComponent(order[i])}&b=${encodeURIComponent(order[j])}`);
  });
});
