// Home (hero, live counts, entry cards) and About.
import { route, api, app, esc, list, isStatic } from './core.js';
import { fmtDate } from './ui.js';

const DOORS = [
  ['#/tree', 'Interactive tree', 'The genre tree from analysis.py, rebuilt in your browser. Collapse clades, search, change the distance weights.'],
  ['#/genres', 'Genres', 'Every genre in genre_data.json with its date, parent genres, offspring and traits.'],
  ['#/traits', 'Trait matrix', 'Which genres share which characteristics: the presence/absence matrix behind the trait distance.'],
  ['#/distance', 'Distances', 'Pick two genres and see the time, parent and trait components of their distance; the full heatmap.'],
  ['#/timeline', 'Lineage timeline', 'Genres placed by first date, with arrows from each parent genre.'],
  ['#/analysis', 'Analysis results', 'Metrics from analysis.py: most influential genres, hybrids, common and modern traits.'],
  ['#/guides', 'Writing guides', 'The repository\'s genre writing guides: structure, characters, pacing and conventions.'],
];

route('home', async () => {
  const s = await api('/info');
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">Genres · Traits · Distances · Tree</p>
    <h1 class="glow">Genre Phylogeny</h1>
    <p class="lead">An evolutionary tree of ${s.genres} novel and literary genres, from myth and oral epic to solarpunk
    and cozy fantasy. Each genre has a first date, parent genres and a set of characteristics; the distances between
    them are clustered into a tree, as in phylogenetics.</p>
    <a class="btn" href="#/tree">Open the tree</a><a class="btn alt" href="#/guides">Writing guides</a>
  </section>
  <div class="tiles">
    <a class="tile" href="#/genres"><b>${s.genres}</b><span>genres</span></a>
    <a class="tile" href="#/traits"><b>${s.traits}</b><span>distinct traits (${s.shared_traits} shared)</span></a>
    <a class="tile" href="#/analysis"><b>${s.hybrids}</b><span>hybrid genres (2+ parents)</span></a>
    <a class="tile" href="#/timeline"><b>${s.roots}</b><span>root genres (no parent)</span></a>
    <a class="tile" href="#/timeline"><b class="sm">${fmtDate(s.earliest)} to ${s.latest}</b><span>span of first dates</span></a>
    <a class="tile" href="#/guides"><b>${s.guides}</b><span>writing guides</span></a>
  </div>
  <div class="grid wide">${list(DOORS, ([h, t, d]) => `<a class="card" href="${h}"><b>${t}</b><span>${d}</span></a>`)}</div>`;
});

route('about', async () => {
  const s = await api('/info');
  app().innerHTML = `
  <p class="kicker">About</p><h1>Literary Genre Evolution Analyzer</h1>
  <p class="lead">A Python tool for analysing and visualising the evolution of literary genres: a database of
  ${s.genres} genres (dates, parent genres, characteristics), a distance-based tree, metrics of influence and
  hybridisation, and a set of genre writing guides. This site presents the repository's data and analysis.</p>
  <h2>Method</h2>
  <p>For each pair of genres, <code>analysis.create_distance_matrix</code> combines three parts:</p>
  <p class="eq">d = 0.4 · |date₁ − date₂| / 1000 + 0.3 · (1 − J(parents)) + 0.3 · (1 − J(traits))</p>
  <p>where J is the Jaccard index (shared / union); a part is 1 when either genre has no parents (or no traits).
  <code>create_phylogenetic_tree</code> then repeatedly joins the closest pair of clusters at half their distance (UPGMA): the
  distance from the joined cluster to every other cluster is the size-weighted mean of its two halves' distances, i.e.
  the average distance over all genre pairs between the clusters. The
  <a href="#/tree">tree page</a> runs a JavaScript port of exactly this code (checked against the Python output in
  the test suite), so you can also try other weights.</p>
  <div class="callout small">Data notes: dates are the first dates recorded in <code>genre_data.json</code>, not
  scholarly claims made by this site. Three genres are dated earlier than one of their parents (see
  <a href="#/analysis">Analysis</a>), and the data has both "Cli-Fi" and "Climate Fiction", and both "Solar Punk" and
  "Solarpunk", as separate entries.</div>
  <h2>Run it</h2>
  <h3>Analysis (command line)</h3>
  <pre>pip install -r requirements.txt
python main.py        # saves genre_timeline.png and genre_phylogeny.png, prints metrics</pre>
  <h3>Web app</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py     # http://127.0.0.1:8170</pre>
  <p class="small mute">${isStatic() ? 'You are on the static site: every page works here; the API answers come from files exported at build time and the tree is rebuilt in your browser.' : 'You are on the local app.'}</p>
  <h2>Credits</h2>
  <p>By George Dickinson (<a href="https://github.com/gddickinson" target="_blank" rel="noopener">@gddickinson</a>),
  in collaboration with Claude (Anthropic) on the analysis and the guides. Plots in the Python tool use NetworkX and
  Matplotlib. MIT licence.</p>`;
});
