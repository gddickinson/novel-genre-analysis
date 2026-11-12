// Small, safe Markdown renderer for the writing guides in guides/: headings (#..####), paragraphs, bullet and numbered
// lists with nesting by indentation, horizontal rules, **bold**, *italic*, `code` and [links](http...). All text is
// HTML-escaped first, so no raw HTML from the source reaches the page. Headings get ids for the table of contents.
// (Adapted from the coffee_explorer renderer, plus nested lists, which the guides use.)
const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const escape = s => String(s).replace(/[&<>"']/g, c => ESC[c]);

export function slug(text) {
  return text.toLowerCase().replace(/<[^>]+>/g, '').replace(/&[a-z#0-9]+;/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

export function inline(text) {
  return escape(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

// A list is { tag, indent, items: [{ text, sub: list|null }] }; nested lists hang off the last item.
function listHtml(l) {
  return `<${l.tag}>${l.items.map(i => `<li>${inline(i.text)}${i.sub ? listHtml(i.sub) : ''}</li>`).join('')}</${l.tag}>`;
}

// Returns { html, toc: [{level, text, id}] }.
export function render(md) {
  const out = [], toc = [], used = new Map();
  let para = [], stack = []; // stack[0] is the top-level list
  const flushPara = () => { if (para.length) { out.push(`<p>${inline(para.join(' '))}</p>`); para = []; } };
  const flushList = () => { if (stack.length) { out.push(listHtml(stack[0])); stack = []; } };
  for (const raw of String(md).replace(/\r\n?/g, '\n').split('\n')) {
    const line = raw.trimEnd();
    let m;
    if (!line.trim()) { flushPara(); continue; }
    if ((m = line.match(/^(#{1,4})\s+(.*)$/))) {
      flushPara(); flushList();
      const level = m[1].length, text = m[2].trim();
      let id = slug(text) || 'section';
      const n = used.get(id) || 0; used.set(id, n + 1);
      if (n) id += '-' + n;
      toc.push({ level, text, id });
      out.push(`<h${level + 1} id="${id}">${inline(text)}</h${level + 1}>`);
    } else if (/^(-{3,}|\*{3,}|_{3,})$/.test(line.trim())) {
      flushPara(); flushList(); out.push('<hr>');
    } else if ((m = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.*)$/))) {
      flushPara();
      const indent = m[1].replace(/\t/g, '    ').length, tag = /\d/.test(m[2]) ? 'ol' : 'ul';
      while (stack.length > 1 && indent < stack[stack.length - 1].indent) stack.pop();
      let top = stack[stack.length - 1];
      if (top && indent > top.indent && top.items.length) {
        const parent = top.items[top.items.length - 1];
        parent.sub = parent.sub || { tag, indent, items: [] };
        stack.push(parent.sub); top = parent.sub;
      } else if (!top || top.tag !== tag) {
        flushList(); top = { tag, indent, items: [] }; stack = [top];
      }
      top.items.push({ text: m[3], sub: null });
    } else if (stack.length && /^\s{2,}\S/.test(raw)) {
      const top = stack[stack.length - 1];
      top.items[top.items.length - 1].text += ' ' + line.trim();
    } else {
      flushList(); para.push(line.trim());
    }
  }
  flushPara(); flushList();
  return { html: out.join('\n'), toc };
}
