# Session log

## 2026-11-12: web interface and static site (branch `web-interface`)
- Added a FastAPI web app (`run_web.py`, port 8170) and a static GitHub Pages build (`scripts/build_static.py`,
  `.github/workflows/pages.yml`). Pages: home, genres + genre detail, trait matrix, interactive tree (SVG, weight
  sliders, collapse, search, Newick export), distances (pair breakdown + heatmap), lineage timeline (arc diagram),
  analysis results, writing guides (rendered from `guides/`), about.
- Ported `create_distance_matrix` / `create_phylogenetic_tree` to `web/static/genre_engine.js`; node test matches the
  Python output (`tests/fixtures/genre_tree.json`, 3 weight sets + the 4-genre regression case) to 1e-9.
- `analysis.py`: optional `weights` argument (default unchanged, 0.4/0.3/0.3) so the API and the JS can rebuild the
  tree with other weights.
- **Fix:** `create_phylogenetic_tree` appended each merged cluster at the end of the node list while the matrix kept it
  at row i, so from the second merge on clusters were joined using other clusters' distances. Regression test
  `test_merged_cluster_keeps_matrix_row`. `genre_phylogeny.png` was drawn with the old code and is not regenerated.
- **Fix (docs):** README usage/clone URL/layout described a `GenreEvolution` module that no longer exists.
- Open questions for George: the merge step averages the two clusters' rows equally (WPGMA), while the docs say UPGMA
  (size-weighted); duplicate entries Cli-Fi / Climate Fiction and Solar Punk / Solarpunk; Science Fiction (1818),
  Holiday Romance (1940) and Academic Mystery (1930) are dated before one of their parents.
- No LLM is used anywhere in the repo; the guides are committed Markdown and shown as is.
- Tests: `pytest -q` 58 passed (tests/ 44, test_genre_evolution.py 14); node: genre_engine, markdown ok.

## 2026-11-12 (later): follow-ups decided by George / the lead
- **Fix:** tree building is now size-weighted UPGMA as documented (was WPGMA: equal-weight mean of the two merged
  clusters). New `analysis.build_upgma_tree(names, matrix)`; tests: hand-worked 4-taxon example (root at 13/3) and
  merge heights equal to scipy's average linkage on the real data. JS port and fixture updated to match.
- **Fix (data):** merged duplicate genres, keeping the entry with more parents/traits and recording the other name in
  a new optional `aliases` field: Cli-Fi (alias "Climate Fiction"), Solarpunk (alias "Solar Punk"). 124 genres now.
- **Fix (data):** Science Fiction (1818), Holiday Romance (1940) and Academic Mystery (1930) are dated before a parent;
  dates kept as recorded (not invented), flagged with a new optional `date_note` field, shown on the site. Tests:
  `TestDataQuality` (aliases are not entries; date_note exactly on genres dated before a parent).
- Regenerated `genre_phylogeny.png` with the fixed UPGMA and merged data (`plot_phylogenetic_tree`, dpi 300; the
  timeline PNG was left alone because it uses random y positions). The plot's layout (child spacing halves per
  level) crowds the many-leaf clades; not changed.
