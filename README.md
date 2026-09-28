# Dr. Jiang 'John' Li - Academic Website

A professional academic website built with Astro showcasing Dr. Li's work as Program Chair for Analytics programs at Franklin University.

## 🚀 Features

- **🎓 Interactive Learning**: 67+ analytics concept review flashcards with flip animations
- **📱 Responsive Design**: Franklin University branding, mobile-first approach
- **🔍 Full-text Search**: Pagefind-powered site search
- **🤖 GitHub Actions**: Automated build and deploy to GitHub Pages
- **📊 Teaching Guides**: AI-augmented analytics workflow, Claude onboarding, and Census data tutorials

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
│   │   ├── program.mdx      # Analytics FAQ
│   │   ├── course.mdx       # Courses
│   │   ├── publication.mdx  # Research
│   │   ├── post.mdx         # Posts
│   │   ├── teach.mdx        # Teaching materials & tools
│   │   └── teach/           # Teaching guides (ai-workflow, claude-onboarding, census-*)
│   ├── layouts/             # Page layout (nav, footer, search)
│   └── styles/              # Global CSS
├── public/                  # Static assets (copied verbatim to dist/)
│   ├── posts/               # Self-contained HTML posts (regularization, job_application, ...)
│   ├── teach/               # Flashcards app, tutorial images, datasets
│   └── img/                 # Images
├── teach/franklin-course-scraper/  # Legacy course scraper (not wired to any page)
└── .github/workflows/       # Build & deploy to GitHub Pages
```

## 🎨 Content Management

### Editing Pages
Pages are MDX files in `src/pages/`. Edit the Markdown and run `npm run dev` to preview.

### Teaching Guides
Guides live in `src/pages/teach/<slug>/index.mdx` with their assets in `public/teach/<slug>/`.

### Adding Posts
The posts index (`src/pages/post.mdx`) links to self-contained HTML outputs in `public/posts/`.

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
