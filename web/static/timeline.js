// Lineage timeline: genres in order of first date, one per row, with an arc from each parent to its offspring
// (an arc diagram of the parent links in genre_data.json). Select a genre to highlight its own links.
import { route, app, esc, $ } from './core.js';
import { eraOf, fmtDate, href, legend, genreList } from './ui.js';

const ROW = 17, BASE = 380, TOP = 12, W = 900;

route('timeline', async () => {
  const all = (await genreList()).slice().sort((a, b) => a.date - b.date || a.name.localeCompare(b.name));
  const y = new Map(all.map((g, i) => [g.name, TOP + i * ROW + ROW / 2]));
  const late = all.flatMap(g => g.parents.filter(p => all.find(o => o.name === p).date > g.date).map(p => [g.name, p]));
  const arcs = all.flatMap(g => g.parents.map(p => {
    const y1 = y.get(p), y2 = y.get(g.name), dy = Math.abs(y2 - y1), rx = Math.min(dy / 2, BASE - 20);
    return `<path class="arc" data-a="${esc(p)}" data-b="${esc(g.name)}" stroke="${eraOf(g.date).color}"
      d="M${BASE},${y1}A${rx},${dy / 2} 0 0 ${y2 > y1 ? 0 : 1} ${BASE},${y2}"/>`;
  }));
  const rows = all.map(g => `<g class="row" data-n="${esc(g.name)}" tabindex="0" role="button" aria-label="${esc(g.name)}, ${fmtDate(g.date)}">
    <rect class="hb" x="${BASE - 8}" y="${y.get(g.name) - ROW / 2}" width="${W - BASE + 8}" height="${ROW}"/>
    <circle cx="${BASE}" cy="${y.get(g.name)}" r="3.5" fill="${eraOf(g.date).color}"/>
    <text class="dt" x="${BASE + 10}" y="${y.get(g.name) + 4}">${fmtDate(g.date)}</text>
    <text x="${BASE + 82}" y="${y.get(g.name) + 4}">${esc(g.name)}</text></g>`);
  const H = TOP * 2 + all.length * ROW;
  app().innerHTML = `
  <p class="kicker">Phylogeny</p><h1>Lineage timeline</h1>
  <p class="lead">All ${all.length} genres in order of first date (rows are evenly spaced, not to scale), with an arc
  from each parent genre to each offspring, coloured by the offspring's date. Select a genre to highlight its parents
  and offspring.</p>
  ${legend()}
  <p id="sel" class="small" aria-live="polite">${late.length ? `${late.length} links run upward because the data dates the offspring before its parent.` : ''}</p>
  <div class="stage tl-stage"><svg class="timeline" viewBox="0 0 ${W} ${H}" role="group" aria-label="Arc diagram of parent links">
    <g class="arcs">${arcs.join('')}</g>${rows.join('')}</svg></div>`;
  const svg = $('.timeline');
  const pick = name => {
    svg.classList.toggle('focus', !!name);
    svg.querySelectorAll('.arc').forEach(a => a.classList.toggle('on', a.dataset.a === name || a.dataset.b === name));
    svg.querySelectorAll('.row').forEach(r => r.classList.toggle('on', r.dataset.n === name));
    const g = all.find(o => o.name === name);
    $('#sel').innerHTML = g ? `<a href="${href(g.name)}"><b>${esc(g.name)}</b></a> (${fmtDate(g.date)}): parents
      ${g.parents.map(esc).join(', ') || 'none'}; offspring ${g.children.map(esc).join(', ') || 'none'}.` : '';
  };
  let cur = '';
  svg.querySelectorAll('.row').forEach(r => {
    const act = () => { cur = cur === r.dataset.n ? '' : r.dataset.n; pick(cur); };
    r.addEventListener('click', act);
    r.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); act(); } });
  });
});
