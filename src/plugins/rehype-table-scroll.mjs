/**
 * table-scroll — a Sätteri hast plugin.
 *
 * Wraps every Markdown/MDX <table> in the same scroll container the careers
 * page writes by hand:
 *
 *   <div class="table-scroll md-table-scroll" role="region" tabindex="0"
 *        aria-label="…"> <table>…</table> </div>
 *
 * Why a build-time plugin instead of editing the MDX: the four /teach/ guides
 * are plain Markdown tables, and a table added later should be handled without
 * anyone remembering to wrap it. No page body text is touched — only a wrapper
 * element is inserted around the existing <table>.
 *
 * The container is `overflow-x: auto` (see `.table-scroll` in global.css), so a
 * table wider than a phone scrolls inside itself instead of pushing the whole
 * document sideways. A scrollable box has to be keyboard reachable, hence
 * tabindex="0"; tabindex plus an accessible name needs a role, hence
 * role="region" + aria-label — the exact combination careers.astro uses.
 *
 * aria-label comes from the nearest heading above the table, so the region is
 * named the way the page already names that section. A table with no heading
 * above it falls back to "Table N".
 *
 * Astro 7 runs Sätteri, not unified, so this is a `hastPlugins` entry on
 * `satteri()` rather than a `markdown.rehypePlugins` entry. @astrojs/mdx
 * inherits `markdown.processor`, so the MDX pages get it from the same place.
 */

const HEADINGS = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']);

function escapeAttr(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function hasTableScrollClass(node) {
  const c = node?.properties?.className ?? node?.properties?.class;
  if (!c) return false;
  const list = Array.isArray(c) ? c : String(c).split(/\s+/);
  return list.includes('table-scroll');
}

export default function tableScrollPlugin() {
  let n = 0;
  let used = new Map();

  return {
    name: 'table-scroll',
    before() {
      n = 0;
      used = new Map();
    },
    element: {
      filter: ['table'],
      visit(node, ctx) {
        n += 1;

        // Already inside a hand-written scroll container — no double wrap.
        const parent = ctx.parent(node);
        if (hasTableScrollClass(parent)) return;

        // Nearest preceding heading among this table's previous siblings.
        let label = '';
        const index = ctx.indexOf(node);
        const siblings = parent?.children ?? [];
        if (typeof index === 'number') {
          for (let i = index - 1; i >= 0; i -= 1) {
            const prev = siblings[i];
            if (prev && prev.type === 'element' && HEADINGS.has(prev.tagName)) {
              label = ctx.textContent(prev).replace(/\s+/g, ' ').trim();
              break;
            }
          }
        }
        let ariaLabel = label ? `${label} — table` : `Table ${n}`;

        // Several tables can sit under one heading (ai-workflow has three under
        // "Sample Data"). Two regions with the same accessible name are not
        // tellable apart in a screen reader's landmark list, so number them.
        const seen = (used.get(ariaLabel) ?? 0) + 1;
        used.set(ariaLabel, seen);
        if (seen > 1) ariaLabel = `${ariaLabel} ${seen}`;

        ctx.wrapNode(node, {
          raw:
            '<div class="table-scroll md-table-scroll" role="region" tabindex="0"' +
            ` aria-label="${escapeAttr(ariaLabel)}"></div>`,
        });
      },
    },
  };
}
