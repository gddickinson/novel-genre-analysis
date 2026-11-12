// Genres list (search and filters) and one genre's page (parents, offspring, traits, nearest genres).
import { route, app, esc, list, $, go } from './core.js';
import { ERAS, eraOf, fmtDate, glink, swatch, legend, genreList, genreMap } from './ui.js';
import { nearest } from './genre_engine.js';

const tlink = t => `<a class="tag a" href="#/traits?t=${encodeURIComponent(t)}">${esc(t)}</a>`;

route('genres', async (args, q) => {
  const all = await genreList();
  app().innerHTML = `
  <p class="kicker">genre_data.json</p><h1>Genres</h1>
  <p class="lead">${all.length} genres with their first date, parent genres and characteristics. Search by name or
  trait; click a genre for its lineage and nearest neighbours.</p>
  <div class="filters panel">
    <div class="fq"><label for="f-q">Name or trait</label><input id="f-q" type="search" value="${esc(q.q || '')}" placeholder="e.g. noir, magic, space"></div>
    <div><label for="f-era">First date</label><select id="f-era"><option value="">Any</option>${list(ERAS, e => `<option value="${e.key}">${e.label}</option>`)}</select></div>
    <div><label for="f-kind">Kind</label><select id="f-kind"><option value="">All</option><option value="hybrid">Hybrid (2+ parents)</option>
      <option value="root">Root (no parent)</option><option value="guide">Has a writing guide</option></select></div>
  </div>
  ${legend()}
  <p id="count" class="small mute" aria-live="polite"></p>
  <div class="scroll"><table class="gtable"><thead><tr><th>Genre</th><th>Date</th><th>Parents</th><th>Traits</th></tr></thead><tbody id="rows"></tbody></table></div>`;
  const draw = () => {
    const words = $('#f-q').value.trim().toLowerCase(), era = $('#f-era').value, kind = $('#f-kind').value;
    const rows = all.filter(g => (!words || [g.name, ...g.aliases].some(x => x.toLowerCase().includes(words)) || g.characteristics.some(c => c.toLowerCase().includes(words)))
      && (!era || eraOf(g.date).key === era)
      && (!kind || (kind === 'hybrid' ? g.parents.length > 1 : kind === 'root' ? !g.parents.length : !!g.guide)));
    $('#count').textContent = `${rows.length} of ${all.length} genres`;
    $('#rows').innerHTML = list(rows, g => `<tr><td>${swatch(g.date)}${glink(g.name)}${g.aliases.length ? ` <span class="small mute">(${g.aliases.map(esc).join(', ')})</span>` : ''}${g.guide ? ' <span class="tag c">guide</span>' : ''}</td>
      <td class="mono">${fmtDate(g.date)}${g.date_note ? ' <span class="tag b" title="' + esc(g.date_note) + '">date note</span>' : ''}</td><td>${list(g.parents, glink, ', ') || '<span class="mute">none</span>'}</td>
      <td>${list(g.characteristics, c => `<span class="tag">${esc(c)}</span>`)}</td></tr>`);
  };
  ['#f-q', '#f-era', '#f-kind'].forEach(s => $(s).addEventListener('input', draw));
  draw();
});

route('genre', async ([name]) => {
  const map = await genreMap(), g = map[name];
  if (!g) { app().innerHTML = `<h1>Unknown genre</h1><p>${esc(name)} is not in genre_data.json. <a href="#/genres">All genres</a></p>`; return; }
  // Ancestors: walk parent links upward (the data has no cycles; guard anyway).
  const anc = [], seen = new Set([g.name]);
  const walk = n => (map[n]?.parents || []).forEach(p => { if (!seen.has(p)) { seen.add(p); anc.push(p); walk(p); } });
  walk(g.name);
  const near = nearest(map, g.name, 8);
  const sharers = Object.values(map).filter(o => o.name !== g.name && o.characteristics.some(c => g.characteristics.includes(c)));
  app().innerHTML = `
  <p class="kicker"><a href="#/genres">Genres</a> / ${esc(eraOf(g.date).label)}</p>
  <h1 class="glow">${esc(g.name)}</h1>
  ${g.aliases.length ? `<p class="mute">Also called: ${g.aliases.map(esc).join(', ')}</p>` : ''}
  ${g.date_note ? `<div class="callout"><b>Date note:</b> ${esc(g.date_note)}.</div>` : ''}
  <div class="kv">
    <div><b>${fmtDate(g.date)}</b><span>first date</span></div>
    <div><b>${g.parents.length}</b><span>parent genre${g.parents.length === 1 ? '' : 's'}</span></div>
    <div><b>${g.children.length}</b><span>direct offspring</span></div>
    <div><b>${anc.length}</b><span>ancestors in the data</span></div>
  </div>
  <div class="two">
    <div class="panel"><h3>Characteristics</h3><p>${list(g.characteristics, tlink)}</p>
      <h3>Parents</h3><p>${list(g.parents, p => `${swatch(map[p].date)}${glink(p)} <span class="mute small">${fmtDate(map[p].date)}</span>`, '<br>') || '<span class="mute">None: a root genre.</span>'}</p>
      <h3>Offspring</h3><p>${list(g.children, c => `${swatch(map[c].date)}${glink(c)}`, ', ') || '<span class="mute">None in the data.</span>'}</p>
      <h3>All ancestors</h3><p>${list(anc, glink, ', ') || '<span class="mute">None.</span>'}</p>
      <p><a class="btn" href="#/tree?focus=${encodeURIComponent(g.name)}">Show in the tree</a>
      ${g.guide ? `<a class="btn alt" href="#/guide/${g.guide}">Writing guide</a>` : ''}</p></div>
    <div class="panel"><h3>Nearest genres (default weights)</h3>
      <table class="small"><thead><tr><th>Genre</th><th>d</th><th>time</th><th>parents</th><th>traits</th></tr></thead><tbody>
      ${list(near, n => `<tr class="click" data-b="${esc(n.name)}"><td>${glink(n.name)}</td><td class="mono">${n.total.toFixed(3)}</td>
        <td class="mono">${n.time.toFixed(3)}</td><td class="mono">${n.parent.toFixed(2)}</td><td class="mono">${n.chars.toFixed(2)}</td></tr>`)}
      </tbody></table>
      <p class="small mute">Components before weighting (time in millennia; parents and traits are 1 − Jaccard). Click a row to compare.</p>
      <h3>Genres sharing a trait</h3><p>${list(sharers, o => glink(o.name), ', ') || '<span class="mute">No other genre shares any of these traits.</span>'}</p></div>
  </div>`;
  app().querySelectorAll('tr[data-b]').forEach(tr => tr.addEventListener('click', e => {
    if (e.target.closest('a')) return;
    go(`#/distance?a=${encodeURIComponent(g.name)}&b=${encodeURIComponent(tr.dataset.b)}`);
  }));
});
