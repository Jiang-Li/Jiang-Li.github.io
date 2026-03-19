# CLAUDE.md

Academic website for Dr. Jiang Li (Analytics Program Chair, Franklin University), built with Quarto.

## Quick Reference

- **Framework**: Quarto static site generator
- **Content**: `.qmd` files (Quarto Markdown with YAML frontmatter)
- **Styling**: Bootstrap (cosmo theme) + `custom.scss` + `style.css`
- **Automation**: Python course scraper in `teach/franklin-course-scraper/`
- **CI/CD**: GitHub Actions (`.github/workflows/update-courses.yml`)
- **Output**: `_site/` — generated, do NOT edit directly

## Commands

```bash
# Preview with hot-reload
quarto preview --port 4200

# Production build
quarto render

# Render single file
quarto render path/to/file.qmd

# Run course scraper (from repo root)
python teach/franklin-course-scraper/scripts/scrape_franklin_courses.py
```

## Key Paths

| Path | Purpose |
|------|---------|
| `_quarto.yml` | Main site configuration |
| `teach/course-schedule.qmd` | Course schedule page |
| `teach/franklin-course-scraper/course_request.md` | Courses to scrape (edit this to change tracked courses) |
| `teach/franklin-course-scraper/data/franklin_courses.csv` | Scraped course data |
| `teach/franklin-course-scraper/scripts/scrape_franklin_courses.py` | Main scraper script |
| `custom.scss` | Theme overrides (Franklin blue: #1f4e79) |
| `posts/` | Blog posts (each in its own folder with `index.qmd`) |

## Conventions

- **Python**: PEP 8, type hints, `@dataclass` for data structures
- **SCSS**: Modify `custom.scss` for theme changes, not `style.css`
- **Content**: New posts go in `posts/<slug>/index.qmd`
- **Course config**: Edit `teach/franklin-course-scraper/course_request.md` — prefix with `*` for first-term courses

## Verification

After changes, verify by:
1. `quarto render` (or render the specific changed file)
2. `quarto preview` and visually check
3. For scraper changes: run scraper, check CSV output, then render `teach/course-schedule.qmd`
