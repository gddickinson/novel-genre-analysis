// node genre_engine.test.mjs: the JS port reproduces analysis.py's distance matrix and trees (fixture written by
// scripts/make_tree_fixture.py from the Python code) on the real genre_data.json.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { distanceMatrix, buildTree, leaves, components, nearest, DEFAULT_WEIGHTS } from './genre_engine.js';

const read = rel => JSON.parse(readFileSync(new URL(rel, import.meta.url), 'utf8'));
const data = read('../../genre_data.json');
const fx = read('../../tests/fixtures/genre_tree.json');
const close = (a, b, msg) => assert.ok(Math.abs(a - b) <= 1e-12 + 1e-9 * Math.abs(b), `${msg}: ${a} vs ${b}`);

// Distance matrix: same names, same values.
const { names, D } = distanceMatrix(data);
assert.deepEqual(names, fx.names);
let k = 0;
for (let i = 0; i < names.length; i++) for (let j = i + 1; j < names.length; j++) close(D[i][j], fx.condensed[k++], `D ${names[i]}|${names[j]}`);
assert.equal(k, fx.condensed.length);
for (let i = 0; i < names.length; i++) assert.equal(D[i][i], 0);

// Trees: identical topology, names, branch lengths and heights.
function same(a, b, path = 'root') {
  assert.equal(a.name, b.name, path);
  close(a.branch_length, b.branch_length, path + ' branch');
  close(a.height, b.height, path + ' height');
  assert.equal(!!a.children, !!b.children, path);
  if (a.children) a.children.forEach((c, i) => same(c, b.children[i], `${path}/${i}`));
}
for (const { weights, tree } of fx.trees) {
  const t = buildTree(data, weights);
  same(t, tree, 'w=' + weights);
  assert.equal(leaves(t).length, names.length);
}
same(buildTree(fx.small.data), fx.small.tree, 'small');

// The /api/genres list form gives the same result as the raw dict.
const list = Object.entries(data).map(([name, g]) => ({ name, ...g }));
same(buildTree(list), fx.trees[0].tree, 'list input');

// Components add up to the matrix value; nearest() is sorted.
const c = components(data['Noir'], data['Nordic Noir']);
close(c.total, DEFAULT_WEIGHTS[0] * c.time + DEFAULT_WEIGHTS[1] * c.parent + DEFAULT_WEIGHTS[2] * c.chars, 'components');
close(c.total, D[names.indexOf('Noir')][names.indexOf('Nordic Noir')], 'components vs matrix');
const nn = nearest(data, 'Cyberpunk', 5);
assert.equal(nn.length, 5);
for (let i = 1; i < nn.length; i++) assert.ok(nn[i - 1].total <= nn[i].total);
console.log('genre_engine: all ok');
