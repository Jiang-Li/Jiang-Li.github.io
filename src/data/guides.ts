/**
 * The four teaching guides, in reading order.
 *
 * SINGLE SOURCE OF TRUTH — the docs sidebar (GuideLayout.astro) and the
 * prev/next pager both read this array. Do not restate the list anywhere else.
 *
 * `href` keeps the directory form that /teach.html already links to; with
 * `build.format: 'preserve'` each one is served from <dir>/index.html, which is
 * the URL DATA 495's Canvas course points at. Changing these breaks a live class.
 */
export interface Guide {
  /** Directory name under src/pages/teach/ — also the localStorage namespace. */
  slug: string;
  /** Full page title; used by the pager. Matches the MDX frontmatter `title`. */
  title: string;
  /** Short label for the narrow sidebar column. */
  shortTitle: string;
  /** Frozen public URL. */
  href: string;
}

export const guides: Guide[] = [
  {
    slug: 'ai-workflow',
    title: 'AI-Augmented Analytics Guide',
    shortTitle: 'AI Workflow',
    href: '/teach/ai-workflow/',
  },
  {
    slug: 'claude-onboarding',
    title: 'Getting Started with Claude',
    shortTitle: 'Claude Onboarding',
    href: '/teach/claude-onboarding/',
  },
  {
    slug: 'census-api-key',
    title: 'How to Get a U.S. Census Bureau API Key',
    shortTitle: 'Census API Key',
    href: '/teach/census-api-key/',
  },
  {
    slug: 'census-zip-data',
    title: 'Pulling ZIP-Level Census Data in Python',
    shortTitle: 'Census ZIP Data',
    href: '/teach/census-zip-data/',
  },
];

/** Resolve the guide a page belongs to from its MDX file path or its URL. */
export function findGuide(file?: string, pathname?: string): Guide | undefined {
  const haystack = `${file ?? ''}|${pathname ?? ''}`;
  return guides.find((g) => haystack.includes(`teach/${g.slug}/`));
}

/** Previous/next guide in manifest order; first has no prev, last has no next. */
export function guideNeighbours(slug: string): { prev?: Guide; next?: Guide } {
  const i = guides.findIndex((g) => g.slug === slug);
  if (i < 0) return {};
  return { prev: guides[i - 1], next: guides[i + 1] };
}

export interface GuideSection {
  slug: string;
  text: string;
}

/**
 * Raw MDX sources, needed because of a gap in the heading pipeline.
 *
 * Astro's heading collector (@astrojs/markdown-satteri `heading-ids`) filters
 * hast *elements* named h1..h6. In MDX, a literal `<h2 id="...">` is parsed as a
 * JSX element, not a hast element, so it never reaches the collector:
 * `Astro.props.headings` for /teach/ai-workflow/ comes back with ZERO depth-2
 * entries even though the page has six `<h2 id="sec-*">`. The other three guides
 * author their `##` in Markdown and are collected normally.
 *
 * Rewriting those `<h2>`s as Markdown would regenerate their ids and break the
 * load-bearing `#sec-*` anchors, so instead we read the source to recover the
 * document order and the hand-written ids, and still take the *slug and text* of
 * Markdown-authored headings from `Astro.props.headings` (the authoritative,
 * smart-punctuation-applied values).
 */
const sources = import.meta.glob<string>('/src/pages/teach/*/index.mdx', {
  query: '?raw',
  import: 'default',
  eager: true,
});

type SourceHeading = { id?: string; text: string };

function scanSourceH2s(src: string): SourceHeading[] {
  const found: SourceHeading[] = [];
  let inFence = false;
  for (const line of src.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const html = line.match(/^<h2\s+id="([^"]+)"\s*>(.*)<\/h2>\s*$/);
    if (html) {
      found.push({ id: html[1], text: html[2] });
      continue;
    }
    const md = line.match(/^##[ \t]+(.*?)\s*$/);
    if (md) found.push({ text: md[1] });
  }
  return found;
}

/**
 * The current guide's `<h2>` sections, in document order.
 * `headings` is `Astro.props.headings`; depth 2 only (h3 would make the
 * ai-workflow panel unusable — the four guides carry 51 h3s between them).
 */
export function guideSections(
  slug: string,
  headings: { depth: number; slug: string; text: string }[] = [],
): GuideSection[] {
  const collected = headings.filter((h) => h.depth === 2);
  const src = sources[`/src/pages/teach/${slug}/index.mdx`];
  if (!src) return collected.map((h) => ({ slug: h.slug, text: h.text }));

  const scanned = scanSourceH2s(src);
  const out: GuideSection[] = [];
  let i = 0;
  for (const h of scanned) {
    if (h.id) {
      out.push({ slug: h.id, text: h.text });
    } else if (collected[i]) {
      out.push({ slug: collected[i].slug, text: collected[i].text });
      i += 1;
    }
  }
  // If the scan and the collector disagree, trust the collector.
  return i === collected.length && out.length >= collected.length
    ? out
    : collected.map((h) => ({ slug: h.slug, text: h.text }));
}
