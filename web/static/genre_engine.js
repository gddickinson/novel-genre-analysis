// Port of analysis.py (create_distance_matrix, _find_min_pair, _update_matrix, create_phylogenetic_tree) to plain JS,
// so the static site can rebuild the tree in the browser. Same arithmetic in the same order as the Python, checked by
// genre_engine.test.mjs against tests/fixtures/genre_tree.json (written by scripts/make_tree_fixture.py).
// Genres: either the genre_data.json object {name: {date, parents, characteristics}} or the /api/genres list.

export const DEFAULT_WEIGHTS = [0.4, 0.3, 0.3]; // time, parents, characteristics (analysis.DEFAULT_WEIGHTS)

export function asDict(genres) {
  if (!Array.isArray(genres)) return genres;
  return Object.fromEntries(genres.map(g => [g.name, g]));
}

// Python sorted() on str compares code points; identical to JS for the names in genre_data.json (all BMP).
const byCodePoint = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

function jaccardDistance(a, b) {
  // 1 - |A∩B| / |A∪B|; 1.0 if either set is empty (as in analysis.py).
  const A = new Set(a), B = new Set(b);
  if (!A.size || !B.size) return 1.0;
  let shared = 0;
  for (const x of A) if (B.has(x)) shared++;
  const total = new Set([...A, ...B]).size;
  return total > 0 ? 1.0 - shared / total : 1.0;
}

// The three components and the weighted total for one pair of genres.
export function components(g1, g2, weights = DEFAULT_WEIGHTS) {
  const [wt, wp, wc] = weights;
  const time = Math.abs(g1.date - g2.date) / 1000.0;
  const parent = jaccardDistance(g1.parents, g2.parents);
  const chars = jaccardDistance(g1.characteristics, g2.characteristics);
  return { time, parent, chars, total: wt * time + wp * parent + wc * chars };
}

// Returns { names (sorted), D (array of Float64Array rows) }.
export function distanceMatrix(genres, weights = DEFAULT_WEIGHTS) {
  const data = asDict(genres);
  const names = Object.keys(data).sort(byCodePoint);
  const n = names.length;
  const D = Array.from({ length: n }, () => new Float64Array(n));
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const d = components(data[names[i]], data[names[j]], weights).total;
      D[i][j] = d; D[j][i] = d;
    }
  }
  return { names, D };
}

function findMinPair(M) {
  let min = Infinity, mi = -1, mj = -1;
  for (let i = 0; i < M.length; i++) {
    const row = M[i];
    for (let j = i + 1; j < M.length; j++) if (row[j] < min) { min = row[j]; mi = i; mj = j; }
  }
  return [mi, mj, min];
}

// Merge clusters i < j: the merged cluster stays at row i (mean of the two rows), row j is dropped.
function updateMatrix(M, i, j) {
  const n = M.length, keep = [];
  for (let k = 0; k < n; k++) if (k !== j) keep.push(k);
  const N = Array.from({ length: n - 1 }, () => new Float64Array(n - 1));
  for (let a = 0; a < n - 1; a++) {
    for (let b = a + 1; b < n - 1; b++) {
      const oa = keep[a], ob = keep[b];
      let d;
      if (oa === i) d = (M[i][ob] + M[j][ob]) / 2.0;
      else if (ob === i) d = (M[oa][i] + M[oa][j]) / 2.0;
      else d = M[oa][ob];
      N[a][b] = d; N[b][a] = d;
    }
  }
  return N;
}

// The tree as nested { name, branch_length, height, children? } (same shape as /api/tree).
export function buildTree(genres, weights = DEFAULT_WEIGHTS) {
  const { names, D } = distanceMatrix(genres, weights);
  let M = D.map(r => Float64Array.from(r));
  const nodes = names.map(name => ({ name, branch_length: 0.0, height: 0.0 }));
  while (nodes.length > 1) {
    const [i, j, dist] = findMinPair(M);
    const h = dist / 2.0;
    nodes[i].branch_length = h - nodes[i].height;
    nodes[j].branch_length = h - nodes[j].height;
    const node = { name: `Internal_${nodes.length}`, branch_length: 0.0, height: h, children: [nodes[i], nodes[j]] };
    nodes[i] = node;
    nodes.splice(j, 1);
    M = updateMatrix(M, i, j);
  }
  return nodes[0];
}

export function leaves(node, out = []) {
  if (!node.children) out.push(node.name);
  else node.children.forEach(c => leaves(c, out));
  return out;
}

// Newick string (topology + branch lengths), handy for export and for comparing trees.
export function newick(node, digits = 6) {
  const label = node.children ? `(${node.children.map(c => newick(c, digits)).join(',')})` : node.name.replace(/[(),:;\s]/g, '_');
  return `${label}:${node.branch_length.toFixed(digits)}`;
}

// The k genres nearest to `name` under the given weights: [{ name, ...components }].
export function nearest(genres, name, k = 8, weights = DEFAULT_WEIGHTS) {
  const data = asDict(genres), g = data[name];
  return Object.keys(data).filter(n => n !== name)
    .map(n => ({ name: n, ...components(g, data[n], weights) }))
    .sort((a, b) => a.total - b.total || byCodePoint(a.name, b.name)).slice(0, k);
}
