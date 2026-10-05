# Dr. Jiang 'John' Li - Academic Website

A professional academic website built with Astro showcasing Dr. Li's work as Program Chair for Analytics programs at Franklin University.

## 🚀 Features

- **Programs**: the B.S. in Analytics and M.S. in Business Analytics compared side by side
- **Curriculum to Careers**: every course mapped to the skills it teaches and the job roles it supports, with Lightcast salary and labour-market data — all driven by CSVs in `src/data/`
- **Teaching guides**: a docs-style reading experience with a sticky sidebar, scroll-spy, copy buttons and progress memory
- **68 flashcards** for analytics concept review
- **Pagefind** full-text search
- **Franklin University palette** sampled from franklin.edu
- **GitHub Actions** builds and deploys to GitHub Pages on every push to `master`

## 🏃‍♂️ Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production (includes search index)
npm run build
```

## 📁 Key Structure

```
├── astro.config.mjs         # Astro configuration
├── src/
│   ├── pages/               # Site pages (MDX)
│   │   ├── index.mdx        # Homepage
│   │   ├── program.mdx      # Programs: the two degrees compared
│   │   ├── careers.astro    # Curriculum to Careers (renders src/data/*.csv)
│   │   ├── course.mdx       # Courses
│   │   ├── publication.mdx  # Research
│   │   ├── post.mdx         # Posts
│   │   ├── teach.mdx        # Teaching materials & tools
│   │   └── teach/           # Teaching guides (ai-workflow, claude-onboarding, census-*)
│   ├── layouts/             # Layout.astro (all pages) + GuideLayout.astro (the four guides)
│   ├── data/                # Careers CSVs, their loader, and the guide manifest
│   ├── plugins/             # Build-time table-scroll wrapper
│   └── styles/              # Global CSS (colour tokens at the top)
├── public/                  # Static assets (copied verbatim to dist/)
│   ├── posts/               # Self-contained HTML posts (regularization, job_application, ...)
│   ├── teach/               # Flashcards app, tutorial images, datasets
│   └── img/                 # Images
└── .github/workflows/       # Build & deploy to GitHub Pages
```

## 🎨 Content Management

### Editing Pages
Pages are MDX files in `src/pages/`. Edit the Markdown and run `npm run dev` to preview.

### Teaching Guides
Guides live in `src/pages/teach/<slug>/index.mdx` with their assets in `public/teach/<slug>/`.

### Adding Posts
The posts index (`src/pages/post.mdx`) links to self-contained HTML outputs in `public/posts/`.

### Careers data
`/careers.html` renders CSVs in `src/data/`. To add a course, a job role or a
salary row, edit the CSV — the page needs no changes. Salary figures are
Lightcast; the page states the dataset, the CIP codes and the education-level
filter each set was drawn with, so keep those in step with the data.

> **`/teach/ai-workflow/` is frozen.** It is linked from a live course: its URL,
> its four numbered section headings and its `sec-*` anchor ids must not change.
> See `CLAUDE.md`.

## 🚀 Deployment

**Automatic**: GitHub Actions builds (`npm run build`) and deploys `dist/` to GitHub Pages on push to `master`.

## 🛠️ Tech Stack

- **Framework**: Astro (static output) + MDX
- **Styling**: Global CSS (ported from original theme)
- **Search**: Pagefind (built at deploy time)
- **CI/CD**: GitHub Actions
- **Deployment**: GitHub Pages

## 📞 Contact

- **Email**: jiang.li2@franklin.edu
- **Website**: [https://jiang-li.github.io](https://jiang-li.github.io)

---

**Interactive learning tools** • **Teaching guides** • **Built with Astro**
