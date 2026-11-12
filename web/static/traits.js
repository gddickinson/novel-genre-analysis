// Trait explorer: the genre x trait presence matrix (traits shared by 2+ genres) and an index of every trait.
import { route, app, esc, list, $ } from './core.js';
import { glink, swatch, fmtDate, href, genreList } from './ui.js';

route('traits', async (args, q) => {
  const all = await genreList();
  const by = new Map();
  for (const g of all) for (const c of g.characteristics) { if (!by.has(c)) by.set(c, []); by.get(c).push(g); }
  const traits = [...by.keys()].sort((a, b) => by.get(b).length - by.get(a).length || a.localeCompare(b));
  const shared = traits.filter(t => by.get(t).length > 1);
  const rows = all.filter(g => g.characteristics.some(c => by.get(c).length > 1)).sort((a, b) => a.date - b.date || a.name.localeCompare(b.name));
  const sel = q.t && by.has(q.t) ? q.t : null;
  app().innerHTML = `
  <p class="kicker">Characteristics</p><h1>Trait matrix</h1>
  <p class="lead">The trait part of the distance compares genres' characteristic sets. Of ${traits.length} distinct
  traits in the data, ${shared.length} are shared by two or more genres; the rest belong to a single genre, so most
  genre pairs have a trait distance of 1.</p>
  <div class="panel" id="pick"></div>
  <h2>Shared traits × genres</h2>
  <p class="small mute">${rows.length} genres (oldest first) that have at least one shared trait. Hover or focus a cell for
  details; click a column heading to select that trait.</p>
  <div class="scroll matrix-wrap"><table class="matrix" aria-label="Genre by trait presence matrix">
    <thead><tr><th class="corner">Genre</th>${list(shared, t => `<th class="vt${t === sel ? ' on' : ''}"><a href="#/traits?t=${encodeURIComponent(t)}&keep=1" title="${esc(t)}"><span>${esc(t)}</span></a></th>`)}</tr></thead>
    <tbody>${list(rows, g => `<tr><th>${swatch(g.date)}<a href="${href(g.name)}">${esc(g.name)}</a></th>${list(shared, t =>
      g.characteristics.includes(t) ? `<td class="hit${t === sel ? ' on' : ''}" title="${esc(g.name)}: ${esc(t)}" tabindex="0">●</td>` : `<td class="${t === sel ? 'on' : ''}"></td>`)}</tr>`)}</tbody>
  </table></div>
  <h2>Every trait</h2>
  <label for="t-q">Filter traits</label><input id="t-q" type="search" placeholder="e.g. horror, setting, magic">
  <div id="tlist" class="tcloud"></div>`;
  const pick = $('#pick');
  pick.innerHTML = sel
    ? `<h3>${esc(sel)}</h3><p>${by.get(sel).length} genre${by.get(sel).length > 1 ? 's' : ''}:
       ${list(by.get(sel), g => `${swatch(g.date)}${glink(g.name)} <span class="mute small">${fmtDate(g.date)}</span>`, ' · ')}</p>
       <p class="small"><a href="#/traits">Clear selection</a></p>`
    : '<p class="mute">Select a trait (a column heading or one below) to list the genres that have it.</p>';
  const drawList = () => {
    const w = $('#t-q').value.trim().toLowerCase();
    const ts = traits.filter(t => !w || t.toLowerCase().includes(w));
    $('#tlist').innerHTML = list(ts, t => `<a class="tag ${by.get(t).length > 1 ? 'a' : ''}${t === sel ? ' sel' : ''}" href="#/traits?t=${encodeURIComponent(t)}">${esc(t)} <b>${by.get(t).length}</b></a>`)
      || '<p class="mute">No trait matches.</p>';
  };
  $('#t-q').addEventListener('input', drawList);
  drawList();
});
