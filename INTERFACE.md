# Literary Genre Evolution Analyzer - Interface Map

## Module Overview

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point; loads data, runs analysis, generates visualizations |
| `genre_database.py` | Loads genre data from JSON, validates parent references |
| `genre_data.json` | Genre database: 120+ genres with dates, parents, characteristics |
| `analysis.py` | Distance matrix, UPGMA tree construction, metric analysis |
| `visualization.py` | Timeline graph and phylogenetic tree plotting (networkx + matplotlib) |
| `genre-evolution.py` | Original monolithic file (retained for reference) |
| `test_genre_evolution.py` | Test suite for data loading, distance, tree, and metrics |
| `guides/` | Markdown writing guides (`<slug>-guide.md`), shown by the web app |
| `run_web.py` | Starts the web app on http://127.0.0.1:8170 |
| `web/app.py` | FastAPI app: `/api/info`, `/genres`, `/analysis`, `/tree` (weights as query), `/guides`, `/guides/{slug}`; `STATIC_ENDPOINTS` |
| `web/data.py` | API data from `genre_database`, `analysis` and `guides/` (`genres`, `tree_dict`, `analysis_summary`, `guides`, `guide`, `GUIDE_GENRES` links) |
| `web/static/` | ES-module front end (no build step): `main.js` router setup, `core.js`/`style.css` shared kit, `ui.js` helpers, one module per page (`home`, `genres`, `traits`, `tree`, `distance`, `timeline`, `analysis`, `guides`), `markdown.js` renderer, `static_api.js` (static-site data) |
| `web/static/genre_engine.js` | JS port of `create_distance_matrix` / `create_phylogenetic_tree` (+ `components`, `nearest`, `newick`); tested by `genre_engine.test.mjs` |
| `scripts/build_static.py` | Exports the static GitHub Pages site to `site/` |
| `scripts/screenshots.py` | Browser smoke test and README screenshots (`docs/img/`) |
| `scripts/make_tree_fixture.py` | Writes `tests/fixtures/genre_tree.json` (Python distances/trees for the JS test) |
| `tests/test_web.py` | API, static build, JS (node) tests, fixture-is-current check |
| `.github/workflows/pages.yml` | Builds and publishes the static site on push to main |
| `_archive/` | Previous versions of the code |

## Key Classes and Functions

### genre_database.py
- `load_genre_data(path=None)` - loads genre dict from JSON
- `validate_parent_references(genre_data)` - returns list of dangling parent refs

### analysis.py
- `Node` - tree node class with name, children, branch_length, height
- `DEFAULT_WEIGHTS` - (0.4, 0.3, 0.3): time, parent, characteristic weights
- `create_distance_matrix(genre_data, weights=DEFAULT_WEIGHTS)` - returns (genre_names, numpy_matrix)
- `create_phylogenetic_tree(genre_data, weights=DEFAULT_WEIGHTS)` - UPGMA tree from the genre distances, returns root Node
- `build_upgma_tree(names, matrix)` - UPGMA (size-weighted average linkage) on any square distance matrix
- `analyze_genre_metrics(genre_data)` - total genres, avg parents, hybrid genres, influential
- `analyze_genre_characteristics(genre_data)` - most common, earliest, modern trends

### visualization.py
- `create_timeline_graph(genre_data)` - returns (DiGraph, positions)
- `plot_timeline_graph(G, pos, genre_data)` - renders timeline plot
- `plot_phylogenetic_tree(root, genre_data)` - renders tree plot

## Data Flow
```
genre_data.json -> genre_database.py (load + validate)
                -> analysis.py (metrics + tree)
                -> visualization.py (plots)
                -> main.py (orchestrate all)
                -> web/data.py -> web/app.py (JSON API) -> web/static (browser; genre_engine.js mirrors analysis.py)
```
