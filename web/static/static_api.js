// Static-site data layer: answers api(path) from the JSON files exported by scripts/build_static.py.
// /tree with non-default weights is rebuilt in the browser by genre_engine.js (the node-tested port of analysis.py).
import { buildTree, DEFAULT_WEIGHTS } from './genre_engine.js';

const files = new Map();
function file(rel) {
  if (!files.has(rel)) {
    files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  }
  return files.get(rel);
}

export async function staticApi(path, body) {
  if (body) throw new Error('This action needs the local app (Python server).');
  const [p, qs] = path.split('?');
  const clean = p.replace(/^\/+|\/+$/g, '');
  if (clean === 'tree' && qs) {
    const q = new URLSearchParams(qs);
    const w = ['w_time', 'w_parent', 'w_char'].map((k, i) => (q.has(k) ? +q.get(k) : DEFAULT_WEIGHTS[i]));
    if (w.some((v, i) => v !== DEFAULT_WEIGHTS[i])) return buildTree(await file('genres'), w);
  }
  return file(clean);
}
