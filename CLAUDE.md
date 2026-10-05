# CLAUDE.md

Academic website for Dr. Jiang Li (Analytics Program Chair, Franklin University),
built with Astro. Live at <https://jiang-li.github.io>.

## Quick Reference

- **Framework**: Astro 7 (static output) + MDX + Tailwind 4
- **Content**: `.mdx` in `src/pages/`; `careers.astro` is `.astro` because it renders data
- **Data**: CSVs in `src/data/` — edit the data, not the page
- **Styling**: `src/styles/global.css`, one file, token-driven
- **Layouts**: `src/layouts/Layout.astro` (everything) and `GuideLayout.astro` (the four guides)
- **Search**: Pagefind, built by `npm run build`
- **CI/CD**: `.github/workflows/deploy.yml` — push to `master` builds and deploys to GitHub Pages
- **Output**: `dist/` — generated, never edit

## Commands

```bash
npm install
npm run dev     # hot reload
npm run build   # Astro + Pagefind index; CI runs exactly this
```

## Pages (11)

`index` · `program` · `careers` · `course` · `publication` · `post` · `teach`
· `teach/{ai-workflow,claude-onboarding,census-api-key,census-zip-data}`

`build.format: 'preserve'` keeps `src/pages/teach/<slug>/index.mdx` at
`/teach/<slug>/index.html`, matching the URLs the Quarto site published.

## 🔒 Frozen: `/teach/ai-workflow/`

This guide is linked from a live DATA 495 Canvas course. Do not change:

1. Its **URL**.
2. Its **four numbered sections** — numbers *and* names. Students are told
   "do Section 2" verbally, so `Section 2 = The Dialogue Model` has to hold.
3. Its `sec-*` **anchor ids** — the sidebar and the section cards link to them.

Its `<h2>`s are hand-written HTML, not Markdown, to keep those ids.

## Key paths

| Path | Purpose |
|------|---------|
| `src/layouts/Layout.astro` | Shell: head, SEO, nav, footer, optional in-page section nav |
| `src/layouts/GuideLayout.astro` | Docs shell for the four guides: sidebar, scroll-spy, pager, copy buttons, progress memory |
| `src/data/guides.ts` | The four-guide manifest — single source for sidebar *and* pager |
| `src/data/careers*.csv` | Careers page data (crosswalk, salary, skills, qualifications, job titles, focus areas) |
| `src/data/careers.ts` | CSV parser and loaders; no runtime dependency |
| `src/plugins/rehype-table-scroll.mjs` | Wraps every Markdown table in a scroll container |
| `src/styles/global.css` | All styling. Colour tokens at the top of the Franklin block |
| `public/` | Copied verbatim: self-contained HTML posts, flashcards app, images, `og-default.png` |

## Conventions

- **Colour**: use the `--fr-*` tokens (`--fr-blue` `#2F5A7C`, `--fr-navy` `#002B54`,
  `--fr-lime` `#AFBC22`, `--fr-blue-light`, `--fr-text`, `--fr-muted`, `--fr-surface`).
  Sampled from franklin.edu. Do not introduce another blue. Callout semantics
  (tip green, warning amber, important red) and syntax highlighting are
  deliberately outside the palette.
- **Measure**: long-form text caps at `72ch`; tables and cards use the full column.
- **Data pages**: new rows go in the CSV, never in the page.
- **SEO**: every page sets `description` in frontmatter. `Layout.astro` emits
  OG/Twitter/canonical/JSON-LD from it.
- **New pages**: `.mdx` under `src/pages/` picks up `Layout.astro` automatically.
  Long pages can set a `sections:` list in frontmatter to get the chip nav.
- **Static HTML islands** go under `public/` and are linked from MDX.

## Gotchas that cost real time

- **MDX frontmatter arrives as `Astro.props.frontmatter`**, not `Astro.props`.
  Reading the wrong one gave every page an empty `<title>` *and* blanked every
  Pagefind search result, with no build error.
- **`<script is:inline>` must not sit inside `{cond && (...)}`.** Astro emits the
  JSX braces as literal text, the script never parses, and nothing warns you.
  Render it unconditionally and guard inside the JS.
- **Astro 7's Markdown processor is Sätteri, not unified.** `markdown.rehypePlugins`
  fails the build; use `markdown.processor = satteri({ hastPlugins: [...] })`.
  Sätteri also only collects *Markdown* headings, so `Astro.props.headings` is
  empty for pages whose `<h2>`s are raw HTML — `guides.ts` recovers those from source.
- **Tailwind preflight zeroes the element layer.** Links, headings, lists, tables,
  inline code, `<hr>`, blockquotes have no styling unless `global.css` provides it.
  Bootstrap used to. It no longer exists here.
- **Specificity**: `.page-main img` (0-1-1) beats `.step-screenshot` (0-1-0). Check
  computed styles after adding any element-level rule.
- **`npm ci` is what CI runs** — keep `package-lock.json` in sync.

## Verification

After changes:

1. `npm run build` completes, including Pagefind.
2. All 11 pages emit, with a non-empty `<title>` and exactly one `<h1>`.
3. No broken links or in-page anchors.
4. No horizontal page scroll at 360px and 390px.
5. `/teach/ai-workflow/` unchanged: URL, four section headings, anchor ids.
