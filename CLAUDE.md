# CLAUDE.md

Academic website for Dr. Jiang Li (Analytics Program Chair, Franklin University), built with Astro.

## Quick Reference

- **Framework**: Astro 5 (static output) + MDX
- **Content**: `.mdx` files in `src/pages/` (Markdown with YAML frontmatter)
- **Styling**: `src/styles/global.css` (ported from the original theme)
- **Layout**: `src/layouts/Layout.astro` (nav, footer, Pagefind search, Google Analytics)
- **Static assets**: `public/` — copied verbatim to `dist/` (self-contained HTML posts, flashcards app, images)
- **CI/CD**: GitHub Actions (`.github/workflows/deploy.yml`) — `npm run build`, deploys `dist/` to GitHub Pages
- **Output**: `dist/` — generated, do NOT edit directly

## Commands

```bash
# Install dependencies
npm install

# Preview with hot-reload
npm run dev

# Production build (Astro + Pagefind search index)
npm run build
```

## Key Paths

| Path | Purpose |
|------|---------|
| `astro.config.mjs` | Astro configuration (static output, `preserve` format) |
| `src/pages/index.mdx` | Homepage |
| `src/pages/teach.mdx` | Teaching materials & tools hub |
| `src/pages/teach/<slug>/index.mdx` | Teaching guides |
| `src/layouts/Layout.astro` | Shared layout |
| `src/styles/global.css` | Global styles |
| `public/posts/` | Self-contained HTML posts linked from `post.mdx` |
| `public/teach/analytics_review/flashcards.html` | Flashcards app |

## Conventions

- **URLs**: `build.format: 'preserve'` keeps `src/pages/teach/<slug>/index.mdx` → `/teach/<slug>/index.html`, matching the original site structure
- **Content parity**: Phase 1 was a pure Quarto → Astro stack swap; page content must stay identical to the original
- **New pages**: Add `.mdx` under `src/pages/`; they automatically use `src/layouts/Layout.astro`
- **Static HTML islands**: Put fully self-contained HTML under `public/` and link to them from MDX pages

## Verification

After changes, verify by:
1. `npm run build` (must complete cleanly, including Pagefind indexing)
2. `npm run dev` and visually check
3. Confirm all 10 pages emit: `index.html`, `program.html`, `course.html`, `publication.html`, `post.html`, `teach.html`, `teach/ai-workflow/index.html`, `teach/census-api-key/index.html`, `teach/census-zip-data/index.html`, `teach/claude-onboarding/index.html`
