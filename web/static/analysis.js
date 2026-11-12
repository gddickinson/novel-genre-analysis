// Analysis results: the output of analysis.analyze_genre_metrics and analyze_genre_characteristics (via /api/analysis),
// plus two consistency checks of the data.
import { route, api, app, esc, list } from './core.js';
import { glink, fmtDate, genreMap } from './ui.js';

const bars = (rows, link = x => esc(x)) => {
  const max = Math.max(...rows.map(r => r[1]), 1);
  return `<table class="bars">${list(rows, ([k, v]) => `<tr><td>${link(k)}</td><td class="mono">${v}</td>
    <td class="bcell"><span class="bar" style="width:${(v / max * 100).toFixed(1)}%"></span></td></tr>`)}</table>`;
};
const tlink = t => `<a href="#/traits?t=${encodeURIComponent(t)}">${esc(t)}</a>`;

route('analysis', async () => {
  const [a, map] = await Promise.all([api('/analysis'), genreMap()]);
  const late = Object.values(map).flatMap(g => g.parents.filter(p => map[p] && map[p].date > g.date).map(p => [g, map[p]]));
  app().innerHTML = `
  <p class="kicker">analysis.py</p><h1>Analysis results</h1>
  <p class="lead">The metrics the command-line tool prints (<code>python main.py</code>), computed by the repository's
  Python code from genre_data.json.</p>
  <div class="tiles">
    <div class="tile"><b>${a.total_genres}</b><span>genres</span></div>
    <div class="tile"><b>${a.avg_parents.toFixed(2)}</b><span>average parents per genre</span></div>
    <div class="tile"><b>${a.hybrid_genres.length}</b><span>hybrid genres (2+ parents)</span></div>
    <div class="tile"><b>${a.dangling_parents.length}</b><span>parent links to missing genres</span></div>
  </div>
  <div class="two">
    <div class="panel"><h3>Most influential (offspring count)</h3>${bars(a.most_influential.slice(0, 15), glink)}
      <p class="small mute">${a.most_influential.length} genres are a parent of at least one other; top 15 shown.</p></div>
    <div class="panel"><h3>Most common traits</h3>${bars(a.most_common, tlink)}
      <h3>Most common traits since 2000</h3>${bars(a.modern_trends, tlink)}
      <p class="small mute">Top 10 each; ties keep the order of genre_data.json, as in the Python.</p></div>
  </div>
  <div class="two">
    <div class="panel"><h3>Genre emergence periods</h3>
      ${bars(a.emergence_periods.map(p => [`${fmtDate(Math.round(p.from))} to ${fmtDate(Math.round(p.to))}`, p.count]))}
      <p class="small mute">First dates cut into five equal-width bins by pandas (<code>pd.cut(bins=5)</code>); empty
      bins are not listed. Most genres fall in the last bin because the data spans 3000 BCE to 2020.</p></div>
    <div class="panel"><h3>Earliest traits</h3>
      <table class="small">${list(a.earliest.slice(0, 15), ([t, d]) => `<tr><td>${tlink(t)}</td><td class="mono">${fmtDate(d)}</td></tr>`)}</table>
      <p class="small mute">Earliest first date of any genre with the trait; 15 of ${a.earliest.length} shown.</p></div>
  </div>
  <h2>Hybrid genres</h2>
  <p>${list(a.hybrid_genres, g => `${glink(g)} <span class="mute small">(${map[g].parents.map(esc).join(' + ')})</span>`, ' · ')}</p>
  <h2>Data checks</h2>
  <div class="panel">
    <p>${a.dangling_parents.length ? `${a.dangling_parents.length} parent links point at genres that are not in the data.`
      : 'Every parent named in genre_data.json is itself a genre in the data (<code>validate_parent_references</code>).'}</p>
    <p>${late.length} genre${late.length === 1 ? ' is' : 's are'} dated earlier than a parent:</p>
    <ul>${list(late, ([g, p]) => `<li>${glink(g.name)} (${fmtDate(g.date)}) has parent ${glink(p.name)} (${fmtDate(p.date)})</li>`)}</ul>
  </div>`;
});
