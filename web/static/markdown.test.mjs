// node markdown.test.mjs: the guide renderer handles the constructs used in guides/*.md and never passes raw HTML.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { render, inline } from './markdown.js';

const { html, toc } = render('# Title\n\n## Core\n\n### Sub\n**Bold line**\n\nText *soft* and `code`.\n\n- one\n- two\n  - two.a\n  - two.b\n- three\n\n1. first\n2. second\n\n---\n\n## Core\n');
assert.match(html, /<h2 id="title">Title<\/h2>/);
assert.match(html, /<h3 id="core">Core<\/h3>/);
assert.match(html, /<h3 id="core-1">/, 'duplicate headings get unique ids');
assert.match(html, /<h4 id="sub">/);
assert.match(html, /<p><strong>Bold line<\/strong><\/p>/);
assert.match(html, /<em>soft<\/em>/);
assert.match(html, /<code>code<\/code>/);
assert.match(html, /<ul><li>one<\/li><li>two<ul><li>two.a<\/li><li>two.b<\/li><\/ul><\/li><li>three<\/li><\/ul>/, 'nested list');
assert.match(html, /<ol><li>first<\/li><li>second<\/li><\/ol>/);
assert.match(html, /<hr>/);
assert.deepEqual(toc.map(t => t.level), [1, 2, 3, 2]);

// Safety: HTML in the source is escaped; only http(s) links become anchors.
assert.equal(inline('<script>alert(1)</script>'), '&lt;script&gt;alert(1)&lt;/script&gt;');
assert.equal(inline('[x](javascript:alert(1))'), '[x](javascript:alert(1))');
assert.equal(inline('2 * 3 * 4'), '2 * 3 * 4');

// Every committed guide renders: a table of contents, no leftover markers, balanced list tags.
const dir = new URL('../../guides/', import.meta.url);
const files = readdirSync(dir).filter(f => f.endsWith('-guide.md'));
assert.ok(files.length > 20);
for (const f of files) {
  const r = render(readFileSync(new URL(f, dir), 'utf8'));
  assert.ok(r.toc.length > 5, f);
  assert.ok(!/<h\d[^>]*>#/.test(r.html) && !/<li>\s*[-*+]\s/.test(r.html), f);
  assert.equal((r.html.match(/<ul>/g) || []).length, (r.html.match(/<\/ul>/g) || []).length, f);
}
console.log(`markdown: all ok (${files.length} guides)`);
