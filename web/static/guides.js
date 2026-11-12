// Writing guides: the list of guides/*-guide.md and one guide rendered from its Markdown, with a table of contents.
import { route, api, app, esc, list, $ } from './core.js';
import { glink } from './ui.js';
import { render } from './markdown.js';

route('guides', async () => {
  const gs = await api('/guides');
  app().innerHTML = `
  <p class="kicker">guides/</p><h1>Writing guides</h1>
  <p class="lead">${gs.length} guides from the repository on writing in a genre: conventions, structure, characters,
  pacing and market notes. Where a guide shares its name with a genre in the data, it links to that genre.</p>
  <label for="gq">Filter guides</label><input id="gq" type="search" placeholder="e.g. mystery, fantasy">
  <div class="grid" id="glist"></div>`;
  const draw = () => {
    const w = $('#gq').value.trim().toLowerCase();
    $('#glist').innerHTML = list(gs.filter(g => !w || g.title.toLowerCase().includes(w)), g => `
      <a class="card" href="#/guide/${g.slug}"><b>${esc(g.title)}</b><small>${g.sections} sections · ${g.words.toLocaleString('en')} words</small>
      ${g.genres.length ? `<span>Genre: ${g.genres.map(esc).join(', ')}</span>` : ''}</a>`) || '<p class="mute">No guide matches.</p>';
  };
  $('#gq').addEventListener('input', draw);
  draw();
});

route('guide', async ([slug]) => {
  const [g, gs] = await Promise.all([api('/guides/' + slug).catch(() => null), api('/guides')]);
  if (!g) { app().innerHTML = `<h1>No such guide</h1><p><a href="#/guides">All guides</a></p>`; return; }
  const meta = gs.find(x => x.slug === slug);
  const { html, toc } = render(g.markdown);
  const i = gs.indexOf(meta), prev = gs[i - 1], next = gs[i + 1];
  app().innerHTML = `
  <p class="kicker"><a href="#/guides">Writing guides</a>${meta.genres.length ? ` · genre: ${meta.genres.map(glink).join(', ')}` : ''}</p>
  <div class="side guide-side">
    <aside class="panel toc" aria-label="Contents"><h3>Contents</h3>
      ${list(toc.filter(t => t.level === 2 || t.level === 3), t => `<a class="l${t.level}" href="#${t.id}" data-id="${t.id}">${esc(t.text)}</a>`)}
      <p class="small mute">guides/${esc(slug)}-guide.md</p></aside>
    <article class="md">${html}
      <p class="pn">${prev ? `<a class="btn alt" href="#/guide/${prev.slug}">← ${esc(prev.title)}</a>` : ''}
      ${next ? `<a class="btn alt" href="#/guide/${next.slug}">${esc(next.title)} →</a>` : ''}</p></article>
  </div>`;
  // In-page links would change the hash route: scroll instead.
  app().querySelectorAll('.toc a[data-id]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault(); document.getElementById(a.dataset.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }));
});
